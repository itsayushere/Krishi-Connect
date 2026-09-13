"""
chatbot_logic.py
-----------------
The "Krishi AI" chat assistant. This is a RULE-BASED chatbot: it does not
call any external AI model. Instead, each "intent" below has a list of
trigger keywords and a canned (but genuinely useful) response. When a
farmer sends a message, we count how many keywords from each intent show
up in it, and reply with whichever intent scored highest.

This technique has a real name — "keyword-based intent matching" — and
it's a legitimate, classic starting point for chatbots. It's honest
about its limits (it can't have a free-flowing conversation), but for a
mini-project it's fast, free, needs no API key, and is fully explainable.

WANT TO UPGRADE THIS LATER? The clean way to do it: keep this function's
signature (it takes a string, returns a string) and swap the body for a
call to a real AI API (e.g. Google Gemini's free tier). Nothing else in
the app would need to change. The README has a short pointer on this.
"""

CHAT_INTENTS = [
    {
        "name": "greeting",
        "keywords": ["hi", "hello", "hey", "namaste", "good morning", "good afternoon", "good evening"],
        "response": (
            "Namaste! I'm Krishi AI. Ask me about fertilizers, irrigation, soil health, "
            "common government schemes, or general farming practices — or use the Crop "
            "Advisor, Smart Irrigation, or Pest Assistant tools for more specific help."
        ),
    },
    {
        "name": "fertilizer",
        "keywords": ["fertilizer", "fertiliser", "khaad", "nutrient", "npk", "urea", "manure", "compost"],
        "response": (
            "Good fertilizer use starts with a soil test — your nearest Krishi Vigyan Kendra (KVK) "
            "can usually do this cheaply. As a general rule: Nitrogen (N) drives leafy growth, "
            "Phosphorus (P) supports roots and flowering, and Potassium (K) supports overall "
            "plant health and disease resistance. Organic options like compost and farmyard "
            "manure improve soil structure over the long run, not just a single season."
        ),
    },
    {
        "name": "irrigation_general",
        "keywords": ["water", "irrigation", "watering", "drip", "sprinkler", "flood irrigation"],
        "response": (
            "The right irrigation method depends heavily on your crop and region — try the "
            "Smart Irrigation tool above for a specific recommendation. As a general rule: "
            "drip irrigation saves the most water for low-water crops, sprinklers suit "
            "medium-water crops over larger areas, and flood/basin irrigation suits "
            "high-water crops like rice."
        ),
    },
    {
        "name": "soil_health",
        "keywords": ["soil test", "soil health", "soil quality", "soil card"],
        "response": (
            "The Soil Health Card scheme lets farmers get free or low-cost soil testing through "
            "government labs, with recommendations on fertilizer and nutrients specific to your "
            "field. Ask at your nearest KVK or Common Service Centre (CSC) about getting a "
            "Soil Health Card for your land."
        ),
    },
    {
        "name": "organic_farming",
        "keywords": ["organic", "natural farming", "pesticide free", "chemical free"],
        "response": (
            "Organic/natural farming relies on compost, crop rotation, biological pest control "
            "(like neem-based sprays), and green manure instead of synthetic chemicals. It "
            "usually takes a few seasons for soil health and yields to stabilize after switching, "
            "so it's often introduced gradually on part of a farm first, rather than all at once."
        ),
    },
    {
        "name": "weather",
        "keywords": ["weather", "rain", "monsoon", "forecast", "climate"],
        "response": (
            "I don't have access to live weather data in this demo. For an actual forecast, "
            "check the India Meteorological Department (IMD) website or app, which gives "
            "district-level agricultural weather advisories."
        ),
    },
    {
        "name": "schemes",
        "keywords": ["scheme", "subsidy", "loan", "insurance", "pm kisan", "pmfby", "kisan credit"],
        "response": (
            "A few major central schemes worth knowing: PM-KISAN (direct income support), "
            "PMFBY / Pradhan Mantri Fasal Bima Yojana (crop insurance), and the Kisan Credit "
            "Card (low-interest farm loans). Scheme rules and benefit amounts do change, so "
            "confirm current details at your nearest Common Service Centre, KVK, or the "
            "official agriculture department website before applying."
        ),
    },
    {
        "name": "market_price",
        "keywords": ["price", "mandi", "market rate", "sell crop", "selling"],
        "response": (
            "For current mandi (market) prices, eNAM (electronic National Agriculture Market, "
            "enam.gov.in) lets you check and trade crops online across registered mandis. Your "
            "local mandi board or Krishi Vigyan Kendra can also give same-day rates."
        ),
    },
    {
        "name": "pest_redirect",
        "keywords": ["pest", "disease", "insect", "bug", "infection", "fungus"],
        "response": (
            "For a specific pest or disease question, try the Pest & Disease Assistant tool "
            "above — describe what you're seeing (or upload a photo) and it'll suggest likely "
            "causes and next steps."
        ),
    },
    {
        "name": "crop_redirect",
        "keywords": ["which crop", "what to grow", "suggest crop", "best crop", "crop selection"],
        "response": (
            "For a crop suggestion based on your soil, land size, and budget, try the Crop "
            "Advisor tool above — it'll give you specific recommendations with reasons."
        ),
    },
    {
        "name": "thanks",
        "keywords": ["thank you", "thanks", "thank u", "shukriya", "dhanyavad"],
        "response": "You're welcome! Feel free to ask anything else about farming.",
    },
    {
        "name": "goodbye",
        "keywords": ["bye", "goodbye", "see you", "alvida"],
        "response": "Take care, and good luck with the harvest! Come back anytime you have a question.",
    },
]

FALLBACK_RESPONSE = (
    "I'm a simple rule-based assistant built for this demo, so I can only help with topics "
    "I've been given: fertilizers, irrigation, soil health, common schemes, market prices, "
    "and general farming practices. Try rephrasing, or use the Crop Advisor, Smart Irrigation, "
    "or Pest Assistant tools above for structured help."
)


def get_chat_response(message: str) -> str:
    """
    Scores every intent by counting keyword matches in the farmer's
    message, and returns the response of whichever intent scores
    highest. Returns FALLBACK_RESPONSE if nothing matches at all.
    """
    message_lower = message.lower()
    best_intent = None
    best_score = 0

    for intent in CHAT_INTENTS:
        score = sum(1 for keyword in intent["keywords"] if keyword in message_lower)
        if score > best_score:
            best_score = score
            best_intent = intent

    if best_intent:
        return best_intent["response"]
    return FALLBACK_RESPONSE