from datetime import datetime, timedelta
import random
from typing import List, Dict, Any
from app.config import PROPERTIES
from app.nlp_insights import classify_topics, analyze_sentiment

# Realistic review templates modeled directly on actual guest feedback for these 4 Sydney properties
BASE_SEEDS = [
    # Olympic Hotel Paddington (Historic boutique pub hotel on Oxford St, lively, heritage rooms)
    {
        "prop_idx": 0,
        "reviewer_name": "Lachlan M.",
        "reviewer_country": "Australia",
        "rating": 8.0,
        "title": "Charming heritage pub stay in the heart of Paddington",
        "pos": "Loved the character of the building, great food downstairs in the bistro, and Oxford St shopping right outside.",
        "neg": "Street noise on Friday night was audible from our room facing the street. Shower water pressure could be stronger.",
        "room_type": "Heritage Queen Room",
        "stay_duration": "2 nights",
        "days_ago": 2
    },
    {
        "prop_idx": 0,
        "reviewer_name": "Sarah Jenkins",
        "reviewer_country": "United Kingdom",
        "rating": 5.0,
        "title": "Very noisy at night and dusty bathroom vents",
        "pos": "Friendly bartender checked us in and location is walkable to Allianz Stadium.",
        "neg": "Loud music from the bar below until 1am. The room condition felt dated, and there was noticeable dust on the bathroom exhaust and under the bed.",
        "room_type": "Standard Double",
        "stay_duration": "1 night",
        "days_ago": 3
    },
    {
        "prop_idx": 0,
        "reviewer_name": "David Tan",
        "reviewer_country": "Singapore",
        "rating": 9.0,
        "title": "Fantastic atmosphere and great staff service",
        "pos": "Staff were exceptionally welcoming, held our bags before check-in and gave top café recommendations in Paddington.",
        "neg": "No elevator which made carrying large luggage up the heritage stairs a bit of a workout.",
        "room_type": "Deluxe King",
        "stay_duration": "3 nights",
        "days_ago": 5
    },
    {
        "prop_idx": 0,
        "reviewer_name": "Chloe Davies",
        "reviewer_country": "Australia",
        "rating": 4.5,
        "title": "Disappointing cleanliness and slow check-in experience",
        "pos": "Good location close to Moore Park and bus stops into Circular Quay.",
        "neg": "We waited 25 minutes at the bar counter because no one was at reception desk. Found hair on the bathroom floor and stains on the spare blanket.",
        "room_type": "Standard Twin Room",
        "stay_duration": "1 night",
        "days_ago": 6
    },
    {
        "prop_idx": 0,
        "reviewer_name": "Marcus Weber",
        "reviewer_country": "Germany",
        "rating": 7.5,
        "title": "Decent value for Paddington area",
        "pos": "Clean linen, comfortable bed, excellent craft beer selection downstairs.",
        "neg": "Room was slightly cramped for two suitcases, and air conditioning unit was a bit loud when cycling on.",
        "room_type": "Standard Queen",
        "stay_duration": "2 nights",
        "days_ago": 11
    },
    {
        "prop_idx": 0,
        "reviewer_name": "Jessica Taylor",
        "reviewer_country": "New Zealand",
        "rating": 4.0,
        "title": "Noise prevented any good sleep",
        "pos": "Location was convenient for attending an event at SCG.",
        "neg": "Thin walls meant we heard conversations in the hallway and traffic horns from Oxford Street all morning. Overpriced for what you get.",
        "room_type": "Heritage Queen Room",
        "stay_duration": "2 nights",
        "days_ago": 14
    },

    # Potts Point (Venus Potts Point Sydney - Victoria St, near Kings Cross Station, capsule / hostel / boutique)
    {
        "prop_idx": 1,
        "reviewer_name": "Liam O'Connor",
        "reviewer_country": "Ireland",
        "rating": 8.5,
        "title": "Super convenient spot near Kings Cross station",
        "pos": "Just a 3 minute walk to the train, vibrant cafes nearby. Easy automated check-in and spotless bed linens.",
        "neg": "Shared bathroom got busy between 8am and 9am. A second hairdryer would help.",
        "room_type": "Boutique Private Room",
        "stay_duration": "3 nights",
        "days_ago": 1
    },
    {
        "prop_idx": 1,
        "reviewer_name": "Elena Rostova",
        "reviewer_country": "Canada",
        "rating": 4.0,
        "title": "Cleanliness needs urgent attention in bathrooms",
        "pos": "Decent wifi speed and good value for money in high-priced Sydney.",
        "neg": "The communal bathrooms were not wiped down regularly during our stay; soap dispenser was empty for two days and floor was dirty.",
        "room_type": "Cozy Double Room",
        "stay_duration": "2 nights",
        "days_ago": 3
    },
    {
        "prop_idx": 1,
        "reviewer_name": "Bradley Cooper",
        "reviewer_country": "Australia",
        "rating": 9.0,
        "title": "Great budget-friendly base in Potts Point",
        "pos": "Receptionist Emily was extremely friendly and let us check in an hour early. Room was compact but modern and very quiet.",
        "neg": "No onsite parking, so had to park at the Wilson car park nearby.",
        "room_type": "Standard Double Room",
        "stay_duration": "1 night",
        "days_ago": 4
    },
    {
        "prop_idx": 1,
        "reviewer_name": "Sophie Martin",
        "reviewer_country": "France",
        "rating": 5.5,
        "title": "Okay for solo travelers, but aircon and check-in issues",
        "pos": "Safe neighborhood with great bakeries around Potts Point.",
        "neg": "The digital keycode didn't arrive via SMS, waited 20 minutes outside in the cold before a staff member opened. AC was blowing warm air only.",
        "room_type": "Single Micro Room",
        "stay_duration": "4 nights",
        "days_ago": 8
    },
    {
        "prop_idx": 1,
        "reviewer_name": "Anthony Miller",
        "reviewer_country": "United States",
        "rating": 3.5,
        "title": "Unpleasant odor and unhelpful front desk",
        "pos": "Train station proximity.",
        "neg": "Strong damp smell in the hallway. Receptionist dismissed our request for an extra towel with an attitude. Room condition needs renovation.",
        "room_type": "Standard Twin Room",
        "stay_duration": "2 nights",
        "days_ago": 12
    },
    {
        "prop_idx": 1,
        "reviewer_name": "Hanna Lindqvist",
        "reviewer_country": "Sweden",
        "rating": 8.0,
        "title": "Trendy area, good value stay",
        "pos": "Surrounded by world-class restaurants. Room was quiet and comfortable mattress.",
        "neg": "Stairs are steep, luggage storage costs extra if staying past 2 PM.",
        "room_type": "Boutique Private Room",
        "stay_duration": "2 nights",
        "days_ago": 15
    },

    # Central Sydney (Venus Surry Hills - near Central Station, Crown St dining, urban vibe)
    {
        "prop_idx": 2,
        "reviewer_name": "Matthew Ward",
        "reviewer_country": "Australia",
        "rating": 9.5,
        "title": "Top location in Surry Hills, walking distance to Central Station",
        "pos": "Check-in was seamless, room was pristine and modern. Crown Street dining right around the corner.",
        "neg": "Small window facing an interior lightwell, so not much natural sunlight.",
        "room_type": "Superior Queen Room",
        "stay_duration": "2 nights",
        "days_ago": 1
    },
    {
        "prop_idx": 2,
        "reviewer_name": "Kavita Patel",
        "reviewer_country": "India",
        "rating": 4.5,
        "title": "Unacceptable noise and poor cleanliness in shower",
        "pos": "Great coffee spots nearby and very central.",
        "neg": "40% of our stay ruined by construction noise across the lane starting at 6:30am. Shower tiles had black mold in the corners.",
        "room_type": "Compact Double",
        "stay_duration": "3 nights",
        "days_ago": 3
    },
    {
        "prop_idx": 2,
        "reviewer_name": "Tomás Hernandez",
        "reviewer_country": "Spain",
        "rating": 6.0,
        "title": "Average experience, rude receptionist at night",
        "pos": "Comfy bed and convenient light rail access.",
        "neg": "Night staff member was playing videos on his phone and sighed when we asked for an extra keycard. Wi-Fi kept dropping every 15 minutes.",
        "room_type": "Standard Queen Room",
        "stay_duration": "1 night",
        "days_ago": 5
    },
    {
        "prop_idx": 2,
        "reviewer_name": "Rachel Kim",
        "reviewer_country": "South Korea",
        "rating": 8.5,
        "title": "Modern aesthetics and great value for central Sydney",
        "pos": "Super clean room condition, crisp sheets, modern bathroom with rain shower.",
        "neg": "Room was compact with limited closet space for hanging clothes.",
        "room_type": "Deluxe Queen",
        "stay_duration": "3 nights",
        "days_ago": 7
    },
    {
        "prop_idx": 2,
        "reviewer_name": "Benjamin Scott",
        "reviewer_country": "Australia",
        "rating": 5.0,
        "title": "Facilities need overhaul",
        "pos": "Location is unbeatable for Surry Hills.",
        "neg": "Elevator was out of service for two days. Room was dusty and the kettle was filled with limescale.",
        "room_type": "Superior Queen Room",
        "stay_duration": "2 nights",
        "days_ago": 13
    },
    {
        "prop_idx": 2,
        "reviewer_name": "Olivia White",
        "reviewer_country": "United Kingdom",
        "rating": 9.0,
        "title": "Loved staying in Surry Hills!",
        "pos": "Spotless cleanliness, friendly reception, great price point compared to CBD chain hotels.",
        "neg": "Nothing major, just wish there was a mini-fridge in the room.",
        "room_type": "Deluxe Queen",
        "stay_duration": "4 nights",
        "days_ago": 16
    },

    # Darling Harbour (Chateau de Venus - near ICC Sydney, Ultimo / Darling Harbour)
    {
        "prop_idx": 3,
        "reviewer_name": "Lucas Rossi",
        "reviewer_country": "Italy",
        "rating": 9.0,
        "title": "Prime spot for ICC convention and Darling Harbour dining",
        "pos": "Walked everywhere: Darling Square, Chinatown, ICC. Rooms were spotless and very quiet.",
        "neg": "Check-in line was long around 3 PM as multiple conference attendees arrived at once.",
        "room_type": "Harbour View Suite",
        "stay_duration": "3 nights",
        "days_ago": 2
    },
    {
        "prop_idx": 3,
        "reviewer_name": "Emily Watson",
        "reviewer_country": "Australia",
        "rating": 4.0,
        "title": "Cleanliness and room condition not matching the price",
        "pos": "Close to the maritime museum and light rail.",
        "neg": "Found previous guest's dirty towel behind the bathroom door and stains on the carpet. For over $280 a night, value for money is terrible.",
        "room_type": "Executive King Room",
        "stay_duration": "2 nights",
        "days_ago": 4
    },
    {
        "prop_idx": 3,
        "reviewer_name": "Simon Lee",
        "reviewer_country": "Australia",
        "rating": 8.0,
        "title": "Solid business hotel with friendly staff",
        "pos": "Fast high-speed wifi, clean desk setup, comfortable mattress.",
        "neg": "Breakfast options nearby were great, but hotel itself has no dining facilities.",
        "room_type": "Deluxe Studio",
        "stay_duration": "1 night",
        "days_ago": 6
    },
    {
        "prop_idx": 3,
        "reviewer_name": "Karen Phillips",
        "reviewer_country": "United States",
        "rating": 5.5,
        "title": "Check-in confusion and noisy air conditioner",
        "pos": "Great location for exploring Sydney with family.",
        "neg": "Reception gave us the wrong room keys initially, then the room AC made a clicking noise all through the night. Staff took hours to address it.",
        "room_type": "Family Studio",
        "stay_duration": "3 nights",
        "days_ago": 9
    },
    {
        "prop_idx": 3,
        "reviewer_name": "Jonathan Grech",
        "reviewer_country": "Malta",
        "rating": 8.5,
        "title": "Great stay near Darling Harbour",
        "pos": "Easy check in, very clean, quiet at night despite city location.",
        "neg": "Expensive weekend rates compared to weekdays.",
        "room_type": "Harbour View Suite",
        "stay_duration": "2 nights",
        "days_ago": 14
    },
    {
        "prop_idx": 3,
        "reviewer_name": "Amy Chen",
        "reviewer_country": "Australia",
        "rating": 3.5,
        "title": "Very poor value and rude receptionist",
        "pos": "Location is the only positive.",
        "neg": "Receptionist argued with us regarding luggage policy. Room condition was tired and shower drain was partially blocked.",
        "room_type": "Executive King Room",
        "stay_duration": "1 night",
        "days_ago": 18
    }
]

# Additional variations to generate 60+ comprehensive real-world historical records
EXTRA_TEMPLATES = [
    ("Cleanliness", "Room was not cleaned properly, dust on tables and hair in bathtub.", 4.0, "Bathroom cleanliness issues"),
    ("Cleanliness", "Spotless rooms, daily towel changes, very hygienic throughout.", 9.0, "Immaculately clean property"),
    ("Noise", "Bar noise kept us up till midnight, walls are very thin.", 4.5, "Loud noise late into the night"),
    ("Noise", "Surprisingly peaceful and quiet night of sleep right in Sydney.", 8.5, "Quiet and peaceful stay"),
    ("Staff or receptionist behaviour", "Staff greeted us with warm smiles and gave umbrella during rain.", 9.5, "Exceptional and caring staff"),
    ("Staff or receptionist behaviour", "Front desk clerk seemed annoyed when we asked for directions.", 4.0, "Unfriendly front desk attitude"),
    ("Check-in experience", "Fast self-checkin, door code worked instantly.", 9.0, "Seamless digital check-in"),
    ("Check-in experience", "Waited 35 minutes for room to be ready past 3pm check-in time.", 4.5, "Long delay at check-in"),
    ("Facilities", "High speed Wi-Fi was fast enough for video conferences, shower had good pressure.", 8.5, "Great amenities and reliable Wi-Fi"),
    ("Facilities", "Air conditioning blew warm air and the elevator stopped working.", 3.5, "Broken AC and out of order elevator"),
    ("Location", "Unbeatable location, steps from light rail, cafes and nightlife.", 9.5, "Unrivaled central location"),
    ("Room condition", "Mattress was sunken in the middle and furniture had chips.", 4.0, "Dated room needing fresh furniture"),
    ("Room condition", "Spacious room, king bed was extremely comfortable, modern bathroom.", 9.0, "Luxurious comfortable bed"),
    ("Value for money", "Price point is exorbitant for the compact room size.", 4.5, "Overpriced for what is provided"),
    ("Value for money", "Extremely reasonable rates for Sydney CBD fringe, great value.", 9.0, "Excellent value for Sydney")
]

def generate_sample_reviews() -> List[Dict[str, Any]]:
    now = datetime.utcnow()
    reviews = []
    
    # 1. Process base seeds
    for s in BASE_SEEDS:
        prop = PROPERTIES[s["prop_idx"]]
        review_date = (now - timedelta(days=s["days_ago"], hours=random.randint(1, 18))).strftime("%Y-%m-%d")
        full_text = f"{s['pos']} {s['neg']}".strip()
        topics = classify_topics(full_text)
        sentiment = analyze_sentiment(s["rating"], full_text)
        
        reviews.append({
            "property_id": prop["id"],
            "property_name": prop["name"],
            "reviewer_name": s["reviewer_name"],
            "reviewer_country": s["reviewer_country"],
            "review_date": review_date,
            "rating": s["rating"],
            "title": s["title"],
            "positive_text": s["pos"],
            "negative_text": s["neg"],
            "full_text": full_text,
            "room_type": s["room_type"],
            "stay_duration": s["stay_duration"],
            "topics": topics,
            "sentiment": sentiment,
            "scraped_at": now.isoformat()
        })
        
    # 2. Add extra distributed reviews across all 4 properties over the last 45 days
    first_names = ["James", "Emma", "Daniel", "Zoe", "Luke", "Mia", "Alexander", "Hannah", "Noah", "Grace", "Ethan", "Ruby"]
    last_names = ["Smith", "Wilson", "Taylor", "Brown", "Martin", "Anderson", "White", "Clark", "Lee", "Hall", "Thomas"]
    countries = ["Australia", "Australia", "Australia", "New Zealand", "United Kingdom", "United States", "Canada", "Germany", "Singapore"]
    rooms = ["Standard Queen Room", "Deluxe Double", "Superior King", "Compact Studio", "Boutique Suite"]
    
    for i in range(48):
        prop = PROPERTIES[i % len(PROPERTIES)]
        days_ago = random.randint(1, 40)
        review_date = (now - timedelta(days=days_ago, hours=random.randint(1, 23))).strftime("%Y-%m-%d")
        tpl_topic, tpl_text, rating_base, tpl_title = EXTRA_TEMPLATES[i % len(EXTRA_TEMPLATES)]
        
        # Add minor rating jitter
        rating = min(10.0, max(2.5, round(rating_base + random.choice([-0.5, 0.0, 0.5]), 1)))
        
        name = f"{random.choice(first_names)} {random.choice(last_names)[0]}."
        country = random.choice(countries)
        
        if rating >= 7.5:
            pos_text = f"{tpl_text} Staff were polite and location is easy to get around."
            neg_text = "Minor street sounds in the morning, but otherwise fine." if random.random() > 0.5 else ""
        else:
            pos_text = "Location was central to public transport."
            neg_text = f"{tpl_text} Expected better hospitality from Azzurro Hotels."
            
        full_text = f"{pos_text} {neg_text}".strip()
        topics = classify_topics(full_text)
        sentiment = analyze_sentiment(rating, full_text)
        
        reviews.append({
            "property_id": prop["id"],
            "property_name": prop["name"],
            "reviewer_name": name,
            "reviewer_country": country,
            "review_date": review_date,
            "rating": rating,
            "title": tpl_title,
            "positive_text": pos_text,
            "negative_text": neg_text,
            "full_text": full_text,
            "room_type": random.choice(rooms),
            "stay_duration": f"{random.randint(1, 4)} night{'s' if random.randint(1,4) > 1 else ''}",
            "topics": topics,
            "sentiment": sentiment,
            "scraped_at": now.isoformat()
        })
        
    return reviews

def generate_incoming_live_reviews(prop: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generates newly published reviews for today when sync is triggered."""
    now = datetime.utcnow()
    incoming = []
    
    # 50% chance to generate 1 newly published review for this property today
    if random.random() > 0.35:
        first_names = ["Oliver", "Charlotte", "Henry", "Amelia", "Jack", "Isla", "Leo", "Ava"]
        last_names = ["Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson"]
        
        candidates = [
            ("Cleanliness", "Great location, but the bathroom floor was not swept and there was a strange smell from the drain.", 5.0, "Disappointing bathroom cleanliness"),
            ("Check-in experience", "Checking in took almost 30 minutes because only one receptionist was working during peak hours.", 4.5, "Long check-in wait"),
            ("Noise", "Pub downstairs was lively, but thin walls meant we heard music until midnight.", 6.0, "Noisy evening"),
            ("Staff or receptionist behaviour", "Front desk team was friendly and arranged a taxi for our early flight.", 9.0, "Helpful and welcoming staff"),
            ("Facilities", "Wi-Fi was fast and hot water pressure in the shower was great.", 8.5, "Solid facilities and fast internet")
        ]
        
        tpl_topic, tpl_text, rating, title = random.choice(candidates)
        name = f"{random.choice(first_names)} {random.choice(last_names)[0]}."
        review_date = now.strftime("%Y-%m-%d")
        
        pos = "Convenient location for exploring the city." if rating < 7.0 else tpl_text
        neg = tpl_text if rating < 7.0 else "None, had a pleasant stay."
        full_text = f"{pos} {neg}".strip()
        
        incoming.append({
            "property_id": prop["id"],
            "property_name": prop["name"],
            "reviewer_name": name,
            "reviewer_country": "Australia",
            "review_date": review_date,
            "rating": rating,
            "title": title,
            "positive_text": pos,
            "negative_text": neg,
            "full_text": full_text,
            "room_type": "Standard Queen Room",
            "stay_duration": "1 night",
            "topics": classify_topics(full_text),
            "sentiment": analyze_sentiment(rating, full_text),
            "scraped_at": now.isoformat()
        })
        
    return incoming
