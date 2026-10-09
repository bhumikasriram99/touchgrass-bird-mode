"""Touch Grass bird ID: web server tying BirdNET, field notes, and the life list together.

Run with:  uv run uvicorn app:app --reload
Then open: http://localhost:8000
"""
import json
import shutil
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

import birds
import notes

BASE = Path(__file__).parent
LIFELIST_FILE = BASE / "data" / "lifelist.json"

app = FastAPI(title="Touch Grass")


def load_lifelist():
    if LIFELIST_FILE.exists():
        return json.loads(LIFELIST_FILE.read_text())
    return {}


def add_to_lifelist(match):
    """Record a sighting. Returns True if this is a new species for the list."""
    lifelist = load_lifelist()
    now = datetime.now().isoformat(timespec="minutes")
    name = match["common_name"]
    is_new = name not in lifelist
    if is_new:
        lifelist[name] = {"scientific_name": match["scientific_name"], "first_heard": now, "times_heard": 0}
    lifelist[name]["last_heard"] = now
    lifelist[name]["times_heard"] += 1
    LIFELIST_FILE.parent.mkdir(exist_ok=True)
    LIFELIST_FILE.write_text(json.dumps(lifelist, indent=2))
    return is_new


@app.get("/")
def index():
    return FileResponse(BASE / "static" / "index.html")


@app.post("/identify")
def identify(
    audio: UploadFile = File(...),
    lat: float | None = Form(None),
    lon: float | None = Form(None),
):
    suffix = Path(audio.filename or "").suffix or ".webm"
    with tempfile.NamedTemporaryFile(suffix=suffix) as upload:
        shutil.copyfileobj(audio.file, upload)
        upload.flush()
        try:
            matches = birds.identify(upload.name, lat=lat, lon=lon)
        except subprocess.CalledProcessError:
            raise HTTPException(400, "Couldn't read that audio. Try another recording.")

    if not matches:
        return {"matches": [], "note": None, "new_species": False}

    top = matches[0]
    return {
        "matches": matches,
        "note": notes.field_note(top["common_name"], top["scientific_name"]),
        "new_species": add_to_lifelist(top),
    }


@app.get("/lifelist")
def lifelist():
    return load_lifelist()
