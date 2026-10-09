# 🌿 Touch Grass

**Hear a bird on the trail? Tap Listen, find out what it is, and put your phone away. Works with no signal.**

Touch Grass is an offline bird call identifier built for a hackathon about using open-source AI to get people off screens and outside. Everything runs on your own device. The screen is on for about 10 seconds, and the rest of the time you're looking up.

## How it works

1. **Listen:** record 12 seconds of birdsong in the browser (or upload a recording).
2. **Identify:** [BirdNET](https://github.com/kahst/BirdNET-Analyzer), an open audio model from the Cornell Lab of Ornithology, picks out the species. Your location and the date narrow it to birds that actually live near you this time of year.
3. **Field note:** a local open-source LLM (Llama 3.1 8B via [Ollama](https://ollama.com)) writes 2–3 sentences on how to spot the bird.
4. **Life list:** every species you hear is saved, so you have a reason to go find the next one.

```
Browser (record / upload, result card, life list)
        │  localhost only
        ▼
FastAPI backend (app.py)
        ├── birds.py   BirdNET: audio → species
        ├── notes.py   Llama 3.1 via Ollama: species → field note (cached)
        └── data/      life list + note cache (JSON)
```

No cloud APIs, no accounts, no internet calls. Turn Wi-Fi off and it still works.

## Setup (macOS)

You need [Homebrew](https://brew.sh) and [uv](https://docs.astral.sh/uv/).

```bash
brew install ffmpeg ollama
brew services start ollama
ollama pull llama3.1:8b        # ~5 GB, one time
uv sync                        # installs Python dependencies
```

## Run

```bash
uv run uvicorn app:app
```

Open **http://localhost:8000**, allow microphone and location access, and tap **Listen**.

No birds nearby? Play a bird call from another device, or upload a test recording:

```bash
mkdir -p samples
curl -L -o samples/soundscape.wav https://github.com/joeweiss/birdnetlib/raw/main/tests/test_files/soundscape.wav
```

You can also run each part on its own:

```bash
uv run python birds.py samples/soundscape.wav   # species from a recording
uv run python notes.py                          # a sample field note
```

## Try it offline

1. Open the app once with Wi-Fi on and allow location (it's remembered).
2. Turn Wi-Fi off.
3. Reload, tap **Listen**: you still get the species, the field note, and a life list update.

## Notes and limits

- BirdNET scores each 3-second chunk; the app shows the top 3 species with confidence. Background noise lowers accuracy.
- Non-wildlife sounds BirdNET detects (voices, dogs, engines…) are filtered out of results.
- Field notes come from an 8B model and can occasionally get small details wrong. The species ID comes from BirdNET, not the LLM.
- Location is rounded to ~1 km before use and never leaves the device.

## Credits and licenses

- **BirdNET** model © Cornell Lab of Ornithology / Chemnitz University of Technology, licensed [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) (non-commercial use).
- **[birdnetlib](https://github.com/joeweiss/birdnetlib)**, Python wrapper for BirdNET, Apache-2.0.
- **Llama 3.1** by Meta, under the [Llama 3.1 Community License](https://www.llama.com/llama3_1/license/).
- **Ollama**, **FastAPI**, **ffmpeg**: open-source tools used to run it all locally.
