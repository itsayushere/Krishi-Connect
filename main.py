"""
main.py
-------
This is the "front desk" of our backend. It doesn't make any farming
decisions itself — it just:
  1. Listens for HTTP requests from the browser (the frontend).
  2. Validates the data using Pydantic models below.
  3. Hands the data to the right function in logic.py / chatbot_logic.py.
  4. Sends back whatever that function returns, as JSON.

Run this with:  uvicorn main:app --reload
Then open:      http://127.0.0.1:8000
(See the README for full setup steps.)
"""

import os
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from logic import recommend_crop, recommend_irrigation, diagnose_pest
from chatbot_logic import get_chat_response
from data import SOIL_TYPES, CROP_DATABASE

app = FastAPI(title="Krishi Connect API")

# CORS lets the browser call this API even if the frontend were ever served
# from a different origin (e.g. VS Code's Live Server on a different port).
# We serve the frontend from this same server below, so this isn't strictly
# required for the default setup — but it's one less thing to debug if you
# ever run the frontend separately during development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------
# REQUEST SHAPES (Pydantic models)
# ---------------------------------------------------------------------
# These describe exactly what JSON we expect the frontend to send.
# FastAPI uses them to validate incoming data automatically — if a
# required field is missing or the wrong type, the farmer's browser gets
# a clear 422 error back before our logic code ever runs.
class CropRequest(BaseModel):
    soil_type: str
    location: str
    farm_size: float = Field(gt=0, description="Farm size in acres")
    budget: float = Field(gt=0, description="Budget in rupees")


class IrrigationRequest(BaseModel):
    location: str
    crop: str


class ChatRequest(BaseModel):
    message: str


# ---------------------------------------------------------------------
# ROUTES
# ---------------------------------------------------------------------
@app.get("/api/health")
def health_check():
    """A simple route to confirm the backend is alive. Handy while testing."""
    return {"status": "ok", "message": "Krishi Connect API is running"}


@app.get("/api/crops")
def list_crops():
    """Returns the crop names and soil types, so the frontend can build its dropdowns
    from the same source of truth as the backend, instead of a hardcoded copy."""
    return {
        "crops": [c["name"] for c in CROP_DATABASE],
        "soil_types": SOIL_TYPES,
    }


@app.post("/api/crop-advisor")
def crop_advisor(req: CropRequest):
    return recommend_crop(req.soil_type, req.location, req.farm_size, req.budget)


@app.post("/api/irrigation")
def irrigation(req: IrrigationRequest):
    return recommend_irrigation(req.location, req.crop)


@app.post("/api/pest-assistant")
async def pest_assistant(
    crop: str = Form(...),
    description: str = Form(...),
    image: UploadFile = File(None),
):
    # File uploads arrive as an UploadFile; we read its raw bytes only if
    # a file was actually attached (image is optional).
    image_bytes = await image.read() if image is not None else None
    return diagnose_pest(crop, description, image_bytes)


@app.post("/api/chat")
def chat(req: ChatRequest):
    return {"reply": get_chat_response(req.message)}

# ---------------------------------------------------------------------
# SERVE THE FRONTEND
# ---------------------------------------------------------------------
# This must be the LAST thing we register. FastAPI checks routes in the
# order they're defined, so all the /api/... routes above get first
# chance to handle a request; anything else (like "/" or "/style.css")
# falls through to these static files. html=True makes it serve
# frontend/index.html automatically when the browser asks for "/".
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = BASE_DIR
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")