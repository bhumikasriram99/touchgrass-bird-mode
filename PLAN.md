# Offline Bird Call Identifier

## Pitch
Hear a bird on the trail, tap **Listen**, and in seconds know what it is, with no signal needed.
Open-source AI does all the work on your own device. The screen is used for about 10 seconds; the rest of the time you're outside looking up.

## Core user flow
1. Open the page and tap **Listen** (records 10–15 sec). An **upload a file** fallback is always available.
2. BirdNET returns the top species and confidence scores.
3. A local LLM writes a 2–3 line field note ("what to look for").
4. The sighting is added to your **life list**, with the prompt "Go find another."

## Architecture
```
Browser page (record / upload, result card, life list)
        │  HTTP (localhost)
        ▼
Python backend (FastAPI)
  POST /identify  → audio in → species + confidence + field note
  GET  /lifelist  → saved sightings
        │
        ├── BirdNET (open model, Cornell Lab)   audio → species
        ├── Ollama + small open LLM (~3B)       species → field note
        └── lifelist.json                       storage
```

## Tech choices
| Piece | Choice | Why                                                                       |
|---|---|---------------------------------------------------------------------------|
| Bird ID | BirdNET (via a Python wrapper) | Proven open model, runs locally. License is non-commercial (CC BY-NC-SA)  |
| Field notes | Ollama + small open-weight LLM (e.g. a ~3B Llama/Qwen/Gemma) | Runs locally and fast on a laptop                                         |
| Backend | FastAPI | Simple, Python, serves the page too                                       |
| Frontend | One HTML page + a little JS (browser mic recording) | No build tools, no framework                                              |
| Storage | JSON file | No database setup                                                         |
| Audio conversion | ffmpeg | Browsers record webm/ogg; BirdNET wants wav/mp3                           |

## MVP scope
**Must have**
- [ ] Record or upload audio → top species + confidence
- [ ] Field note for the top species
- [ ] Life list (persists between runs)
- [ ] Works with Wi-Fi off

**Stretch (only if must-haves are done)**
- [x] Location and date filter (BirdNET supports lat/lon/week, which improves accuracy)
- [ ] "Birds you might hear around here this week" to nudge people outside
- [ ] Phone access over local network / phone-side inference

**Out of scope:** accounts, maps, social features, training models, native app.

## Risks & mitigations
| Risk | Mitigation |
|---|---|
| BirdNET install / Python version issues | Do it first; use a virtual environment; go/no-go gate |
| Browser audio format mismatch | Convert with ffmpeg; keep the upload fallback |
| Background noise → wrong ID | Show top 3 + confidence; demo with clean clips first |
| LLM slow or makes up facts | Small model, short prompt, ground it on the species name only; keep notes brief |
| Mic permission in browser | Use `localhost` (browsers allow mic there) |
