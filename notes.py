"""Field notes written by a local open-source LLM (via Ollama). No internet needed."""
import json
from pathlib import Path

import httpx

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.1:8b"
CACHE_FILE = Path(__file__).parent / "data" / "notes_cache.json"

PROMPT = """You are a friendly field guide talking to someone standing outside.
In 2-3 short sentences, tell them how to spot a {common} ({scientific}):
what it looks like, where to look for it, and one fun fact.
Plain sentences only, no lists or headings. Leave out any detail you are unsure of.
You don't know where the person is, so don't say whether the bird lives "here"."""


def _load_cache():
    if CACHE_FILE.exists():
        return json.loads(CACHE_FILE.read_text())
    return {}


def field_note(common_name, scientific_name):
    """Return a short field note, cached so repeat birds are instant."""
    cache = _load_cache()
    if common_name in cache:
        return cache[common_name]

    try:
        response = httpx.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": PROMPT.format(common=common_name, scientific=scientific_name),
                "stream": False,
                "options": {"temperature": 0.3},
            },
            timeout=90,
        )
        response.raise_for_status()
        note = response.json()["response"].strip()
    except (httpx.HTTPError, KeyError):
        return "Field note unavailable right now (is Ollama running?). Look up, it's still out there!"

    cache[common_name] = note
    CACHE_FILE.parent.mkdir(exist_ok=True)
    CACHE_FILE.write_text(json.dumps(cache, indent=2))
    return note


if __name__ == "__main__":
    print(field_note("Northern Cardinal", "Cardinalis cardinalis"))
