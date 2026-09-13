# Krishi-Connect
"Krishi Connect is a web app that gives farmers plain-language answers to four everyday
decisions: which crop to grow, how to irrigate it, what might be wrong with a sick plant,
and general farming questions through a chat interface. The backend is a Python REST API
built with FastAPI; the frontend is plain HTML/CSS/JavaScript. All the recommendation logic
is rule-based — scoring systems and keyword matching against a hand-built dataset — not a
trained machine-learning model, which keeps it fully explainable and needing no internet
API key to run."


## 2. Architecture, in one diagram

```
 BROWSER                                   SERVER (uvicorn, port 8000)
 ┌─────────────────────┐                   ┌──────────────────────────────┐
 │ index.html           │                   │ main.py  (FastAPI app)       │
 │ style.css             │  fetch() /JSON   │  - Pydantic validation        │
 │ script.js  ──────────┼──────────────────>│  - /api/... routes            │
 │  (event listeners,    │<──────────────────┤  - calls logic.py functions   │
 │   fetch calls,        │  JSON response    │  - calls chatbot_logic.py     │
 │   DOM rendering)      │                   │        │                     │
 └─────────────────────┘                   │        ▼                     │
                                             │  logic.py / chatbot_logic.py │
                                             │  (all decision-making)       │
                                             │        │                     │
                                             │        ▼                     │
                                             │  data.py                     │
                                             │  (crops, irrigation methods, │
                                             │   rainfall zones, pests)     │
                                             └──────────────────────────────┘
```

One process serves everything — there is no separate frontend server.
`app.mount("/", StaticFiles(...))` in `main.py` is registered *last*, so all
`/api/...` routes get first chance to handle a request before static files
are served as a fallback.

## 3. Tech stack cheat sheet

| Layer | Tech | Purpose |
|---|---|---|
| Backend language | Python 3.11 | All logic |
| Web framework | FastAPI | Defines the REST API |
| Server | Uvicorn | Runs the FastAPI app (`uvicorn main:app --reload`) |
| Validation | Pydantic | Validates incoming JSON shape/types automatically |
| Image handling | Pillow (PIL) | Opens/resizes the optional pest photo |
| Frontend | HTML5 / CSS3 / vanilla JS | UI, styling, interactivity (no framework) |
| Data exchange | JSON (multipart/form-data for the photo upload) | Frontend ↔ backend format |
| Data storage | Python lists/dicts in `data.py` | In-memory only, not a real database |
| Fonts | Google Fonts (Fraunces, Work Sans) | Loaded via `@import` in `style.css` |

## 4. File-by-file map

- **`main.py`** — the "front desk." Defines the FastAPI app, the Pydantic request models
  (`CropRequest`, `IrrigationRequest`, `ChatRequest`), the six `/api/...` routes, and mounts
  the static frontend files last.
- **`logic.py`** — the brain for three features: `recommend_crop`, `recommend_irrigation`,
  `diagnose_pest` (+ helper functions `find_rainfall_zone`, `find_crop`,
  `analyze_image_color`). Pure functions: plain Python in, plain dictionary out — testable
  without a server or browser.
- **`chatbot_logic.py`** — the rule-based chatbot. `CHAT_INTENTS` (12 intents with keyword
  lists + canned responses) and `get_chat_response()`.
- **`data.py`** — the knowledge base: `CROP_DATABASE` (12 crops), `SOIL_TYPES` (7 types),
  `IRRIGATION_METHODS` (keyed by Low/Medium/High), `REGION_RAINFALL` (~26 Indian states/
  regions mapped to High/Medium/Low), `PEST_DISEASE_DATABASE` (11 pest/disease entries),
  `PEST_FALLBACK`.
- **`index.html`** — page structure: a top nav + five `<section class="view">` panels
  (home, crop advisor, irrigation, pest assistant, chat), all toggled by JS, not separate
  page loads.
- **`style.css`** — design tokens as CSS variables (`:root`), then layout, forms, and the
  "note-card" result panels.
- **`script.js`** — view switching, populating dropdowns from `/api/crops`, submitting each
  form via `fetch`, and rendering the JSON response into note-cards.

  ## 5. Feature deep-dives

### Crop Advisor
Filters `CROP_DATABASE` to crops whose `suitable_soils` includes the chosen soil, then scores:
- **+50** base for a soil match
- **+30** if `budget ÷ farm_size` comfortably covers the crop's `min_cost_per_acre`
- **+15** if it's within 70% of that cost (tight but workable)
- **+0** (with a caution note) if well below

Sorts by score, returns the top 3, each with a plain-English reason built from the actual numbers.

### Smart Irrigation
No scoring — pure two-step lookup:
1. `find_crop()` → get the crop's `water_needs` (Low/Medium/High) from `CROP_DATABASE`.
2. That value is used directly as the key into `IRRIGATION_METHODS` (Low→Drip,
   Medium→Sprinkler, High→Flood/Basin).
3. Separately, `find_rainfall_zone()` scans the typed location for a known state name in
   `REGION_RAINFALL` (defaults to "Medium" if nothing matches) and adds a rainfall-specific tip.

### Pest & Disease Assistant
Two independent signals:
1. **Keyword match**: filters `PEST_DISEASE_DATABASE` to entries relevant to the chosen crop
   (or marked `"all"`), scores each by counting keyword hits in the farmer's free-text
   description, returns the highest scorer (must be >0) or `PEST_FALLBACK`.
2. **Image colour check** (optional): Pillow resizes the photo to 40×40px and averages R/G/B.
   Yellow/brown-leaning average → nutrient-stress note. Green-leaning → "looks healthy by
   colour" note. This is arithmetic on pixels, not object/disease recognition — it never
   identifies *what* is in the photo.

### Krishi AI Chat
"Keyword-based intent matching" (the file's own docstring's term). 12 intents, each with a
keyword list and one fixed response. Message is lowercased, scored against every intent by
keyword-hit count, highest scorer (>0) wins. No match → fallback message.

## 6. "Is this real AI?" — the answer to have ready

No external AI/ML API is called anywhere (no OpenAI, Gemini, Anthropic — check `main.py`'s
imports: only `fastapi`, `pydantic`, `os`, and your own files). Every recommendation comes
from **rule-based logic**: weighted scoring and keyword matching against a hand-built
dataset — a technique called a rule-based system or expert system, one of AI's oldest
branches, distinct from machine learning (which learns from training data instead of being
explicitly programmed). "Krishi AI" is the chatbot's in-app name, not a technical claim.

**Why this was a reasonable choice for this project:** fully explainable (you can trace
every recommendation back to exact numbers), needs no API key or internet dependency, fully
deterministic (same input → same output, good for a graded demo), and fast to build and
verify within a project timeline.

**Documented upgrade path:** `chatbot_logic.py`'s comments describe swapping its internals
for a real LLM API call later (e.g. a free-tier model) without changing anything else in the
app, since the function still just takes a string in and returns a string out.

## 7. Anticipated viva questions & model answers

**General / architecture**
- *What kind of application is this?* A client-server web app: browser frontend + Python
  REST API backend, both served by one process.
- *How many servers are running?* One — uvicorn, serving both the API and the static
  frontend files.
- *Why split logic.py from main.py?* Separation of concerns — main.py only handles HTTP
  (requests/responses/validation); logic.py holds pure decision-making functions that can be
  tested independently, without any server or browser.
- *Why is data.py separate too?* Separates data (facts) from logic (decisions) — adding a
  new crop or pest means editing only data.py, never touching the algorithms.

**Backend / API**
- *What does FastAPI do here?* Turns Python functions into HTTP endpoints, auto-validates
  incoming JSON against Pydantic models, and auto-generates interactive docs at `/docs`.
- *What happens if a farmer sends a negative farm size?* Pydantic's `Field(gt=0)` constraint
  on `CropRequest` rejects it automatically with a 422 error before `recommend_crop()` ever
  runs. `logic.py` also double-checks this internally as a second line of defense.
- *Why does the pest endpoint use Form/File instead of a Pydantic model?* Because it accepts
  an optional image file — files can't be embedded in JSON, so that request is sent as
  `multipart/form-data` instead.
- *What does CORS middleware do, and do you actually need it?* It lets the browser call the
  API even from a different origin. Since the frontend is served from the same FastAPI app,
  it's not strictly required here, but it's a defensive safeguard in case the frontend is
  ever hosted separately during development.
- *How would you test an endpoint without the frontend?* FastAPI's built-in Swagger UI at
  `/docs` lets you call any endpoint directly in the browser.

**Frontend**
- *How does clicking a nav button change the page without reloading?* All buttons share a
  `data-view` attribute; one JS click handler hides all `.view` sections and shows the
  matching one — no page navigation happens at all.
- *How do the dropdowns get their options?* `script.js` calls `/api/crops` on page load,
  which returns crop names and soil types straight from `data.py`, so the frontend never has
  a stale hardcoded copy.
- *Why does the pest form use FormData instead of JSON?* Because it may include a file
  (photo), which JSON can't represent — FormData handles the multipart encoding automatically.

**Feature logic**
- *Why does budget divide by farm size in Crop Advisor?* Because crop costs in the database
  are per-acre — normalizing budget the same way makes it a fair comparison regardless of
  farm size.
- *What if two crops score the same?* They keep their relative order from the database
  (Python's sort is stable) — whichever came first in `CROP_DATABASE` appears first.
- *What if the pest description matches zero keywords?* The generic `PEST_FALLBACK` advice
  is returned — pointing the farmer to a KVK or the Kisan Call Centre rather than guessing.
- *Can the photo alone diagnose a disease?* No — it only nudges toward a colour-based hint
  (stressed/yellowing vs. healthy-looking) and is always shown alongside the text-based
  match, never as a standalone diagnosis.

**AI / limitations / future scope**

- *Why not use a real AI model?* Explainability, zero cost/API-key dependency, and
  determinism were prioritized for a project of this scope; see Section 6 above.
- *What are the current limitations?* The chatbot only recognizes pre-defined keywords, not
  free-form questions; the "database" is in-memory Python data, not a persistent database;
  costs/yields in data.py are educational approximations, not verified government figures
  (this is stated directly in data.py's own docstring).
- *How would you extend this?* Swap `get_chat_response()`'s internals for a real LLM API
  call (signature unchanged); replace `data.py` with a real database (SQLite/PostgreSQL) for
  persistence; replace the pixel-averaging image check with an actual trained image
  classification model for pest/disease detection from photos.
