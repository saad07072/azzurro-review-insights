import os
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Detect Vercel or read-only container environments
IS_VERCEL = "VERCEL" in os.environ

if IS_VERCEL:
    DATA_DIR = Path("/tmp/azzurro_data")
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    DB_PATH = DATA_DIR / "azzurro_reviews.db"
    # Copy pre-seeded DB or seed json to /tmp if not present
    bundled_db = BASE_DIR / "data" / "azzurro_reviews.db"
    if bundled_db.exists() and not DB_PATH.exists():
        shutil.copy(bundled_db, DB_PATH)
else:
    DATA_DIR = BASE_DIR / "data"
    DATA_DIR.mkdir(exist_ok=True)
    DB_PATH = DATA_DIR / "azzurro_reviews.db"

SAMPLE_JSON_PATH = BASE_DIR / "data" / "sample_reviews.json"

PROPERTIES = [
    {
        "id": "olympic-paddington",
        "name": "Olympic Hotel Paddington",
        "url": "https://www.booking.com/hotel/au/olympic-paddington.html",
        "city": "Sydney",
        "suburb": "Paddington",
        "target_slug": "olympic-paddington"
    },
    {
        "id": "venus-potts-point",
        "name": "Potts Point (Venus Potts Point Sydney)",
        "url": "https://www.booking.com/hotel/au/venus-potts-point-sydney.html",
        "city": "Sydney",
        "suburb": "Potts Point",
        "target_slug": "venus-potts-point-sydney"
    },
    {
        "id": "venus-surry-hills",
        "name": "Central Sydney (Venus Surry Hills)",
        "url": "https://www.booking.com/hotel/au/venus-surry-hills.html",
        "city": "Sydney",
        "suburb": "Surry Hills",
        "target_slug": "venus-surry-hills"
    },
    {
        "id": "chateau-de-venus",
        "name": "Darling Harbour (Chateau de Venus)",
        "url": "https://www.booking.com/hotel/au/chateau-de-venus.html",
        "city": "Sydney",
        "suburb": "Darling Harbour / Ultimo",
        "target_slug": "chateau-de-venus"
    }
]

TOPIC_KEYWORDS = {
    "Cleanliness": [
        "clean", "dirty", "stain", "stains", "dust", "dusty", "hair", "smell", "odor", "linen", 
        "towel", "towels", "sheets", "bedding", "bathroom", "toilet", "hygiene", "mold", "filthy", "tidy", "spotless"
    ],
    "Check-in experience": [
        "check-in", "check in", "checkin", "reception", "keys", "keycard", "front desk", "queue", 
        "wait", "waiting", "early check-in", "late arrival", "check out", "checkout", "luggage storage", "deposit"
    ],
    "Staff or receptionist behaviour": [
        "staff", "receptionist", "manager", "host", "service", "friendly", "rude", "polite", 
        "helpful", "unhelpful", "attitude", "welcoming", "dismissive", "courteous", "unprofessional", "accommodating"
    ],
    "Noise": [
        "noise", "noisy", "loud", "soundproof", "street", "traffic", "bar", "pub", "music", 
        "thin walls", "neighbour", "neighbor", "footsteps", "party", "horns", "construction", "slamming"
    ],
    "Facilities": [
        "wifi", "wi-fi", "internet", "elevator", "lift", "stairs", "air conditioning", "aircon", "ac", 
        "heater", "heating", "shower", "hot water", "water pressure", "tv", "television", "gym", "pool", "kitchen", "fridge", "microwave"
    ],
    "Location": [
        "location", "convenient", "subway", "train", "station", "bus", "walk", "walkable", 
        "central", "shops", "restaurants", "safe area", "distance", "cbd", "harbour", "transit", "close to"
    ],
    "Room condition": [
        "room", "bed", "mattress", "pillows", "spacious", "small", "tiny", "cramped", "window", 
        "view", "old", "dated", "modern", "renovated", "broken", "maintenance", "lighting", "socket", "power point"
    ],
    "Value for money": [
        "price", "value", "expensive", "cheap", "affordable", "cost", "overpriced", "worth it", 
        "rip-off", "bargain", "budget", "rates", "paid", "worth the money", "fair price"
    ]
}
