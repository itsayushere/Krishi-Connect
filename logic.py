"""
logic.py
--------
This is the "brain" of Krishi Connect. Each function here takes plain
Python values as input (numbers, strings) and returns a plain Python
dictionary as output. main.py's only job is to hand these functions
whatever the farmer typed into the form, and send back whatever these
functions return, as JSON.

Keeping this file separate from main.py means you can test all of this
logic with ordinary Python — no server, no browser needed. Try running:
    python3 -c "from logic import recommend_crop; print(recommend_crop('Loamy', 'Aligarh, UP', 2, 30000))"
"""

import io
from data import (
    CROP_DATABASE,
    IRRIGATION_METHODS,
    REGION_RAINFALL,
    PEST_DISEASE_DATABASE,
    PEST_FALLBACK,
)


# ---------------------------------------------------------------------
# Small shared helper
# ---------------------------------------------------------------------
def find_rainfall_zone(location: str) -> str:
    """
    Looks for a known state/region name inside whatever the farmer typed
    (e.g. "Aligarh, Uttar Pradesh" contains "uttar pradesh"). Falls back
    to "Medium" if we don't recognise anything — this keeps the app
    working even for a village name we've never heard of.
    """
    location_lower = location.lower()
    for region_name, zone in REGION_RAINFALL.items():
        if region_name in location_lower:
            return zone
    return "Medium"


def find_crop(crop_name: str):
    """Looks up a crop in CROP_DATABASE by name, case-insensitively."""
    for crop in CROP_DATABASE:
        if crop["name"].lower() == crop_name.lower():
            return crop
    return None


# ---------------------------------------------------------------------
# FEATURE 1: CROP ADVISOR
# ---------------------------------------------------------------------
def recommend_crop(soil_type: str, location: str, farm_size: float, budget: float) -> dict:
    """
    Scores every crop in CROP_DATABASE against the farmer's soil type
    and budget, then returns the top matches with plain-English reasons.

    Scoring is intentionally simple and explainable:
      +50 points  -> soil type matches
      +30 points  -> budget comfortably covers the crop's estimated cost
      +15 points  -> budget is close (within 70%) of the estimated cost
    A crop scores 0 (and is dropped) if the soil doesn't match at all.
    """
    if farm_size <= 0:
        return {"error": "Farm size must be greater than 0 acres."}
    if budget <= 0:
        return {"error": "Budget must be greater than 0."}

    budget_per_acre = budget / farm_size
    scored = []

    for crop in CROP_DATABASE:
        if soil_type.lower() not in [s.lower() for s in crop["suitable_soils"]]:
            continue  # skip crops that don't suit this soil at all

        score = 50
        reasons = [f"{crop['name']} is well-suited to {soil_type} soil."]

        if budget_per_acre >= crop["min_cost_per_acre"]:
            score += 30
            reasons.append(
                f"Your budget (about ₹{round(budget_per_acre):,}/acre) comfortably "
                f"covers the estimated cost of ₹{crop['min_cost_per_acre']:,}/acre."
            )
        elif budget_per_acre >= crop["min_cost_per_acre"] * 0.7:
            score += 15
            reasons.append(
                f"Your budget is a little tight for the estimated ₹{crop['min_cost_per_acre']:,}/acre "
                f"cost, but workable with careful spending."
            )
        else:
            reasons.append(
                f"Your budget is well below the estimated ₹{crop['min_cost_per_acre']:,}/acre "
                f"cost — proceed with caution or consider a smaller plot for this crop."
            )

        scored.append({**crop, "score": score, "reasons": reasons})

    scored.sort(key=lambda c: c["score"], reverse=True)
    top_matches = scored[:3]

    if not top_matches:
        return {
            "recommendations": [],
            "message": (
                f"No crops in our database are typically grown in {soil_type} soil. "
                "Try a different soil type, or treat this as a starting point and "
                "check with your local KVK."
            ),
        }

    results = []
    for crop in top_matches:
        results.append({
            "crop": crop["name"],
            "reason": " ".join(crop["reasons"]),
            "water_needs": crop["water_needs"],
            "season": crop["season"],
            "duration": crop["duration"],
            "expected_yield": crop["expected_yield"],
            "fertilizer_tip": crop["fertilizer_tip"],
            "estimated_total_cost": round(crop["min_cost_per_acre"] * farm_size),
        })

    return {"recommendations": results, "location": location, "farm_size": farm_size}


# ---------------------------------------------------------------------
# FEATURE 2: SMART IRRIGATION
# ---------------------------------------------------------------------
def recommend_irrigation(location: str, crop_name: str) -> dict:
    """
    Looks the crop up in CROP_DATABASE to get its water need, then looks
    up the region's rainfall zone, and combines both into one recommendation.
    """
    crop = find_crop(crop_name)
    if not crop:
        return {"error": f"'{crop_name}' isn't in our crop database yet."}

    water_need = crop["water_needs"]
    rainfall_zone = find_rainfall_zone(location)
    method_info = IRRIGATION_METHODS[water_need]

    if rainfall_zone == "Low":
        rainfall_tip = (
            "Your region typically sees low rainfall, so water conservation matters most here — "
            "consider mulching around the base of plants to reduce evaporation."
        )
    elif rainfall_zone == "High":
        rainfall_tip = (
            "Your region typically sees good rainfall, so you may only need active irrigation "
            "during dry spells or right after transplanting."
        )
    else:
        rainfall_tip = (
            "Your region has moderate rainfall — plan on supplementing it during flowering "
            "and grain-filling, which is when crops are most sensitive to water stress."
        )

    return {
        "crop": crop["name"],
        "recommended_method": method_info["method"],
        "reason": method_info["reason"],
        "frequency": method_info["frequency"],
        "rainfall_zone": rainfall_zone,
        "rainfall_tip": rainfall_tip,
        "location": location,
    }


# ---------------------------------------------------------------------
# FEATURE 3: PEST & DISEASE ASSISTANT
# ---------------------------------------------------------------------
def analyze_image_color(image_bytes: bytes):
    """
    A *simple, honest* bit of image processing — not machine learning.
    We just resize the image and average its pixel colours. Leaning
    yellow/brown is a weak signal for stress or disease; it's a nice
    supporting clue, not a diagnosis by itself. This uses Pillow (PIL),
    which is a genuinely useful library to know for basic image work.
    """
    try:
        from PIL import Image
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img = img.resize((40, 40))  # small size = fast average, we don't need detail
        pixels = list(img.getdata())
        n = len(pixels)
        avg_r = sum(p[0] for p in pixels) / n
        avg_g = sum(p[1] for p in pixels) / n
        avg_b = sum(p[2] for p in pixels) / n

        if avg_r > 150 and avg_g > 120 and avg_b < 110:
            return (
                "The photo leans yellow/brown overall, which can point to nutrient stress, "
                "drying, or fungal spotting — worth combining with a written description "
                "of exactly where and how it looks affected."
            )
        elif avg_g > avg_r and avg_g > avg_b:
            return (
                "The photo looks mostly green/healthy in overall colour. Colour alone can't "
                "catch spots, holes, or insects, though — describe those separately if you see them."
            )
        else:
            return "Photo received. For the best match, also describe the specific symptoms you can see."
    except Exception:
        return None  # if the image can't be read, we just skip the note rather than fail the whole request


def diagnose_pest(crop: str, description: str, image_bytes: bytes = None) -> dict:
    """
    Scores every entry in PEST_DISEASE_DATABASE by counting how many of
    its keywords appear in the farmer's description, restricted to
    entries that apply to this crop (or apply to "all" crops). Returns
    the best match, or a helpful fallback if nothing scores above 0.
    """
    description_lower = description.lower()
    best_match = None
    best_score = 0

    for entry in PEST_DISEASE_DATABASE:
        applies_to_this_crop = "all" in [c.lower() for c in entry["crops"]] or \
                                crop.lower() in [c.lower() for c in entry["crops"]]
        if not applies_to_this_crop:
            continue

        score = sum(1 for keyword in entry["keywords"] if keyword in description_lower)
        if score > best_score:
            best_score = score
            best_match = entry

    image_note = analyze_image_color(image_bytes) if image_bytes else None

    if not best_match:
        result = dict(PEST_FALLBACK)  # copy so we don't mutate the shared fallback dict
        result["image_note"] = image_note
        return result

    return {
        "problem": best_match["name"],
        "risk_level": best_match["risk_level"],
        "actions": best_match["actions"],
        "image_note": image_note,
    }