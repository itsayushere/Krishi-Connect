"""
data.py
--------
This file is our "knowledge base" — plain Python lists and dictionaries
that hold everything the app knows about crops, irrigation, rainfall
patterns, and pests/diseases.

Why a separate file? Because it keeps DATA (facts) separate from LOGIC
(decisions). If you want to add a new crop, tweak a number, or add a new
pest, you only ever need to touch this file — logic.py and chatbot_logic.py
don't change.

NOTE ON ACCURACY: The costs, yields, and durations below are realistic
*approximations* for an educational demo, not verified agronomic data
from a government source. If you want to make this more rigorous for a
real submission, swap these numbers for figures from your state's
Department of Agriculture or an ICAR publication and cite them in your
report.
"""

# ---------------------------------------------------------------------
# 1. CROP DATABASE
# ---------------------------------------------------------------------
# Each crop is a dictionary. "suitable_soils" and "water_needs" are the
# fields logic.py uses most heavily for matching.
CROP_DATABASE = [
    {
        "name": "Rice",
        "suitable_soils": ["Clay", "Loamy", "Alluvial"],
        "water_needs": "High",
        "min_cost_per_acre": 18000,
        "duration": "120-150 days",
        "season": "Kharif (sown June-July)",
        "expected_yield": "20-25 quintals/acre",
        "fertilizer_tip": "Apply Urea, DAP and Potash in 3 split doses across the growth cycle.",
    },
    {
        "name": "Wheat",
        "suitable_soils": ["Loamy", "Clay", "Alluvial"],
        "water_needs": "Medium",
        "min_cost_per_acre": 14000,
        "duration": "110-130 days",
        "season": "Rabi (sown Oct-Dec)",
        "expected_yield": "18-22 quintals/acre",
        "fertilizer_tip": "Apply a balanced NPK dose at sowing, top-dress with Urea at first irrigation.",
    },
    {
        "name": "Maize",
        "suitable_soils": ["Loamy", "Sandy", "Alluvial"],
        "water_needs": "Medium",
        "min_cost_per_acre": 12000,
        "duration": "90-110 days",
        "season": "Kharif or Rabi",
        "expected_yield": "25-30 quintals/acre",
        "fertilizer_tip": "Responds well to Nitrogen; split it across sowing, knee-high and tasseling stages.",
    },
    {
        "name": "Sugarcane",
        "suitable_soils": ["Loamy", "Clay", "Alluvial"],
        "water_needs": "High",
        "min_cost_per_acre": 35000,
        "duration": "10-12 months",
        "season": "Year-round (Feb-March sowing is best)",
        "expected_yield": "350-400 quintals/acre",
        "fertilizer_tip": "Heavy feeder — needs regular Nitrogen top-dressing and organic manure at planting.",
    },
    {
        "name": "Cotton",
        "suitable_soils": ["Black", "Alluvial"],
        "water_needs": "Medium",
        "min_cost_per_acre": 20000,
        "duration": "150-180 days",
        "season": "Kharif (sown April-May)",
        "expected_yield": "8-10 quintals/acre",
        "fertilizer_tip": "Avoid excess Nitrogen — it encourages pests like bollworm. Balance with Potash.",
    },
    {
        "name": "Groundnut",
        "suitable_soils": ["Sandy", "Red", "Loamy"],
        "water_needs": "Low",
        "min_cost_per_acre": 15000,
        "duration": "100-120 days",
        "season": "Kharif",
        "expected_yield": "10-12 quintals/acre",
        "fertilizer_tip": "Needs Gypsum (Calcium Sulphate) at flowering for good pod filling.",
    },
    {
        "name": "Bajra",
        "suitable_soils": ["Sandy", "Red", "Black"],
        "water_needs": "Low",
        "min_cost_per_acre": 6000,
        "duration": "75-90 days",
        "season": "Kharif",
        "expected_yield": "8-10 quintals/acre",
        "fertilizer_tip": "Low input crop — light Nitrogen dose at sowing is usually enough.",
    },
    {
        "name": "Chana",
        "suitable_soils": ["Loamy", "Black", "Clay"],
        "water_needs": "Low",
        "min_cost_per_acre": 9000,
        "duration": "90-120 days",
        "season": "Rabi",
        "expected_yield": "8-10 quintals/acre",
        "fertilizer_tip": "A legume — fixes its own Nitrogen. Focus on Phosphorus instead.",
    },
    {
        "name": "Mustard",
        "suitable_soils": ["Loamy", "Alluvial", "Sandy"],
        "water_needs": "Low",
        "min_cost_per_acre": 8000,
        "duration": "110-140 days",
        "season": "Rabi",
        "expected_yield": "6-8 quintals/acre",
        "fertilizer_tip": "Sulphur boosts oil content — consider a Sulphur-containing fertilizer.",
    },
    {
        "name": "Potato",
        "suitable_soils": ["Loamy", "Sandy", "Alluvial"],
        "water_needs": "Medium",
        "min_cost_per_acre": 40000,
        "duration": "70-90 days",
        "season": "Rabi (planted Oct-Nov)",
        "expected_yield": "80-100 quintals/acre",
        "fertilizer_tip": "Needs high Potash for tuber quality, plus well-decomposed farmyard manure.",
    },
    {
        "name": "Soybean",
        "suitable_soils": ["Black", "Loamy"],
        "water_needs": "Medium",
        "min_cost_per_acre": 13000,
        "duration": "90-110 days",
        "season": "Kharif",
        "expected_yield": "10-12 quintals/acre",
        "fertilizer_tip": "A legume — needs less Nitrogen, but respond well to Phosphorus at sowing.",
    },
    {
        "name": "Tomato",
        "suitable_soils": ["Loamy", "Sandy", "Red"],
        "water_needs": "Medium",
        "min_cost_per_acre": 30000,
        "duration": "60-80 days",
        "season": "Varies by region — best in cooler months",
        "expected_yield": "150-200 quintals/acre",
        "fertilizer_tip": "Calcium helps prevent blossom-end rot; keep watering consistent, not erratic.",
    },
]

# All soil types the app understands (used to build the dropdown on the frontend)
SOIL_TYPES = ["Alluvial", "Black", "Red", "Laterite", "Sandy", "Clay", "Loamy"]

# ---------------------------------------------------------------------
# 2. IRRIGATION METHODS
# ---------------------------------------------------------------------
# Keyed by water need (matches the "water_needs" field in CROP_DATABASE),
# so logic.py can look a crop up in CROP_DATABASE, then use that crop's
# water_needs value as the key here.
IRRIGATION_METHODS = {
    "Low": {
        "method": "Drip Irrigation",
        "reason": "Low-water crops lose most value from precise, slow watering at the root zone instead of "
                  "wetting the whole field. Drip irrigation can cut water use by 30-50% compared to flooding.",
        "frequency": "Short daily or alternate-day cycles (20-40 minutes), adjusted for soil moisture.",
    },
    "Medium": {
        "method": "Sprinkler Irrigation",
        "reason": "Sprinklers spread water evenly over a larger area without the heavy water demand of "
                  "flooding, which suits crops that need steady but moderate moisture.",
        "frequency": "Every 4-6 days, more often during flowering or grain-filling stages.",
    },
    "High": {
        "method": "Flood / Basin Irrigation",
        "reason": "High-water crops like rice actually benefit from standing water, which also helps "
                  "suppress weeds. This needs reliable water access and soil that holds water well.",
        "frequency": "Maintain a shallow standing water layer, especially during the vegetative stage.",
    },
}

# ---------------------------------------------------------------------
# 3. REGION -> RAINFALL ZONE
# ---------------------------------------------------------------------
# A rough map of Indian states to a rainfall category. We match a
# farmer's typed location against these keys (see logic.py), so this
# is intentionally approximate, not meteorological data.
REGION_RAINFALL = {
    "kerala": "High", "assam": "High", "meghalaya": "High", "west bengal": "High",
    "goa": "High", "konkan": "High", "sikkim": "High", "arunachal": "High",
    "uttar pradesh": "Medium", "bihar": "Medium", "madhya pradesh": "Medium",
    "odisha": "Medium", "andhra pradesh": "Medium", "telangana": "Medium",
    "chhattisgarh": "Medium", "punjab": "Medium", "haryana": "Medium",
    "karnataka": "Medium", "jharkhand": "Medium", "tamil nadu": "Medium",
    "rajasthan": "Low", "gujarat": "Low", "kutch": "Low", "marathwada": "Low",
    "vidarbha": "Low", "ladakh": "Low",
}

# ---------------------------------------------------------------------
# 4. PEST & DISEASE DATABASE
# ---------------------------------------------------------------------
# "crops": ["all"] means the problem can show up on any crop.
# "keywords": phrases we search for inside the farmer's free-text description.
PEST_DISEASE_DATABASE = [
    {
        "name": "Aphid infestation",
        "crops": ["all"],
        "keywords": ["aphid", "sticky leaves", "curling leaves", "small green insects",
                     "tiny insects", "honeydew", "cluster of insects"],
        "risk_level": "Medium",
        "actions": [
            "Spray a neem oil solution (30-50ml neem oil per 15L water) every 7 days.",
            "Introduce or protect natural predators like ladybird beetles.",
            "Avoid excess Nitrogen fertilizer — it makes new growth more attractive to aphids.",
            "Use yellow sticky traps to monitor and reduce populations.",
        ],
    },
    {
        "name": "Leaf curl virus",
        "crops": ["Cotton", "Tomato"],
        "keywords": ["leaf curl", "curling", "shrivel", "yellow veins", "stunted growth", "crinkled leaves"],
        "risk_level": "High",
        "actions": [
            "Remove and destroy infected plants to stop the virus from spreading.",
            "Control whitefly (the insect that spreads this virus) with neem-based spray.",
            "Use virus-resistant seed varieties when replanting.",
            "Avoid planting new crops right next to an already-infected field.",
        ],
    },
    {
        "name": "Powdery mildew",
        "crops": ["Wheat", "Mustard", "Tomato"],
        "keywords": ["white powder", "white spots", "powdery", "white coating", "dusty leaves"],
        "risk_level": "Medium",
        "actions": [
            "Spray a sulfur-based fungicide as soon as symptoms appear.",
            "Improve air circulation with proper plant spacing — don't overcrowd.",
            "Water at the base in the morning, not overhead in the evening.",
            "Remove and dispose of badly affected leaves.",
        ],
    },
    {
        "name": "Blight (early/late)",
        "crops": ["Potato", "Tomato"],
        "keywords": ["dark spots", "black spots", "brown patches", "rotting", "wilting stems", "leaf spots"],
        "risk_level": "High",
        "actions": [
            "Apply a copper-based fungicide immediately.",
            "Remove and destroy infected plants — don't compost them.",
            "Improve field drainage; blight spreads fastest in wet, humid conditions.",
            "Rotate crops each season instead of planting potato/tomato in the same spot.",
        ],
    },
    {
        "name": "Stem borer",
        "crops": ["Rice", "Maize", "Sugarcane"],
        "keywords": ["dead heart", "holes in stem", "wilting center", "boring holes", "tunnel", "dried central shoot"],
        "risk_level": "High",
        "actions": [
            "Set up pheromone traps to monitor and trap adult moths.",
            "Apply a recommended insecticide (ask your local KVK for the current one approved for your crop).",
            "Remove and destroy affected tillers/stems promptly.",
            "Keep field bunds clean to reduce hiding spots for pests.",
        ],
    },
    {
        "name": "Bollworm damage",
        "crops": ["Cotton"],
        "keywords": ["holes in boll", "boll damage", "caterpillar", "worm", "holes in fruit", "larvae"],
        "risk_level": "High",
        "actions": [
            "Use pheromone traps to monitor moth activity early.",
            "Apply a neem-based biopesticide as a first line of defense.",
            "Avoid excess Nitrogen, which encourages lush growth that attracts bollworm.",
            "Consult your KVK about Bt cotton varieties for future seasons.",
        ],
    },
    {
        "name": "Yellow rust",
        "crops": ["Wheat"],
        "keywords": ["yellow stripes", "orange powder", "rust", "yellow streaks", "orange spots"],
        "risk_level": "High",
        "actions": [
            "Spray a Propiconazole-based fungicide at the first sign of rust.",
            "Use rust-resistant wheat varieties in future sowings.",
            "Monitor closely during cool, humid weather — rust spreads fastest then.",
            "Avoid very late sowing, which increases rust risk.",
        ],
    },
    {
        "name": "Possible nutrient deficiency",
        "crops": ["all"],
        "keywords": ["yellowing", "yellow leaves", "pale leaves", "stunted", "slow growth", "pale green"],
        "risk_level": "Low",
        "actions": [
            "Get a soil test done at your nearest Krishi Vigyan Kendra (KVK) — it's usually free or low-cost.",
            "Apply a balanced NPK fertilizer based on the test results.",
            "If leaves are pale and growth is slow, a light Urea top-dressing often helps.",
            "Add organic compost or farmyard manure to improve soil health over time.",
        ],
    },
    {
        "name": "Root rot",
        "crops": ["all"],
        "keywords": ["wilting", "root rot", "plant dying", "black roots", "drooping suddenly", "mushy roots"],
        "risk_level": "High",
        "actions": [
            "Improve field drainage — root rot is almost always linked to waterlogging.",
            "Avoid overwatering, especially in clay soils that hold water longer.",
            "Apply a Trichoderma-based bio-fungicide to the soil.",
            "Remove and destroy severely affected plants to protect the rest of the field.",
        ],
    },
    {
        "name": "Locust / grasshopper damage",
        "crops": ["all"],
        "keywords": ["locust", "grasshopper", "swarm", "eaten leaves", "chewed leaves", "defoliation"],
        "risk_level": "High",
        "actions": [
            "Alert your local agriculture department immediately — swarms are tracked regionally.",
            "Use a recommended insecticide spray on affected areas.",
            "Noise and smoke can help disperse small swarms temporarily.",
            "If the crop is near maturity, consider an early harvest to save what you can.",
        ],
    },
    {
        "name": "Fruit fly damage",
        "crops": ["Tomato"],
        "keywords": ["maggots", "fruit fly", "rotting fruit", "holes in fruit", "larvae inside fruit"],
        "risk_level": "Medium",
        "actions": [
            "Set up fruit fly traps using a methyl eugenol lure.",
            "Collect and destroy fallen or rotting fruit — it's a breeding ground.",
            "Cover developing fruit with light bags where practical.",
            "Spray neem oil solution as a preventive measure.",
        ],
    },
]

# Fallback advice when we can't confidently match a description to anything above.
PEST_FALLBACK = {
    "problem": "No confident match found",
    "risk_level": "Unknown",
    "actions": [
        "Take clear, well-lit photos of the affected leaves, stems, or fruit.",
        "Contact your nearest Krishi Vigyan Kendra (KVK) for an expert, in-person opinion.",
        "Call the Kisan Call Centre (toll-free, 22 languages): 1800-180-1551.",
        "Try describing more specific symptoms — leaf color, spot shape, insect appearance, or where on the plant it started.",
    ],
}