"""BirdNET wrapper: audio file in, top species out. Runs fully offline."""
import subprocess
import tempfile
import threading
from datetime import datetime
from pathlib import Path

from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer

_analyzer = None
_lock = threading.Lock()  # the BirdNET model isn't safe to run from two requests at once


def _get_analyzer():
    global _analyzer
    if _analyzer is None:
        _analyzer = Analyzer()
    return _analyzer


def to_wav(src, dst):
    """Browsers record webm/ogg; convert anything to mono 48 kHz wav for BirdNET."""
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-ac", "1", "-ar", "48000", str(dst)],
        check=True,
    )


def identify(audio_path, lat=None, lon=None, min_conf=0.25, top_n=3):
    """Return up to top_n species, best confidence first. Empty list = no confident match."""
    options = {"min_conf": min_conf}
    if lat is not None and lon is not None:
        # Location + date narrows the list to birds that live there this time of year.
        options.update(lat=lat, lon=lon, date=datetime.now())

    with tempfile.TemporaryDirectory() as tmp:
        wav = Path(tmp) / "clip.wav"
        to_wav(audio_path, wav)
        with _lock:
            recording = Recording(_get_analyzer(), str(wav), **options)
            recording.analyze()

    # BirdNET scores every 3-second chunk; keep each species' best chunk.
    best = {}
    for d in recording.detections:
        name = d["common_name"]
        if name not in best or d["confidence"] > best[name]["confidence"]:
            best[name] = {
                "common_name": name,
                "scientific_name": d["scientific_name"],
                "confidence": round(d["confidence"], 2),
            }
    return sorted(best.values(), key=lambda b: -b["confidence"])[:top_n]


if __name__ == "__main__":
    import sys

    for match in identify(sys.argv[1]):
        print(f"{match['confidence']:.2f}  {match['common_name']} ({match['scientific_name']})")
