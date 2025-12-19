# ==========================
# LOCATIONS FOR DATA COLLECTION
# ==========================
# Format: {"geo": "latitude,longitude,radius", "name": "location_name"}
# Radius can be in miles (m), kilometers (km), or default

LOCATIONS = [
    {"geo": "19.0760,72.8777,0.5km", "name": "Mumbai_Central"},
    {"geo": "19.1136,72.8697,0.5km", "name": "Mumbai_South"},
    {"geo": "19.0883,72.8385,0.5km", "name": "Mumbai_East"},
    
    {"geo": "28.6139,77.2090,0.5km", "name": "Delhi_Central"},
    {"geo": "28.5244,77.1855,0.5km", "name": "Delhi_South"},
    
    {"geo": "12.9352,77.6245,0.5km", "name": "Bangalore_Central"},
]

# ==========================
# KEYWORDS FOR URBAN LAND-USE CLASSIFICATION
# ==========================
# Organized by category for easier maintenance

RESIDENTIAL_KEYWORDS = [
    "House", "Home", "Bungalow", "Villa", "Condominium", "Duplex",
    "Townhouse", "Estate", "Residential Area", "Apartment Complex",
    "Multi-family home", "Single-family home", "Sleep", "Bedtime",
    "Family", "Household", "Domestic", "Living", "Comfort",
    "Ghar", "Niwas", "Vasahat", "Jhuggi", "Slum", "Chawl",
]

COMMERCIAL_KEYWORDS = [
    "Retail", "Shop", "Store", "Supermarket", "Marketplace", "Business",
    "Office", "Commercial Space", "Outlet", "Franchise", "Corporate",
    "Service Center", "Mall", "Shopping Plaza", "Food Court",
    "Buy", "Purchase", "Selling", "Sale", "Deal", "Offer", "Discount",
    "Bazaar", "Haat", "Dukaan", "Vyapar", "Showroom", "Market",
]

INDUSTRIAL_KEYWORDS = [
    "Factory", "Manufacturing", "Industry", "Plant", "Storage", "Godown",
    "Distribution Center", "Workshop", "Production Facility",
    "Industrial Complex", "Assembly Line", "Machinery", "Processing",
]

TRANSPORT_KEYWORDS = [
    "Airport", "Train Station", "Bus Station", "Subway", "Tram",
    "Taxi Stand", "Parking Lot", "Toll Booth", "Port", "Dock", "Harbor",
    "Bus Terminal", "Metro", "Car Park", "Commute", "Traffic", "Transit",
    "Congestion", "Rush hour", "Delay", "Journey", "Commuter",
    "Gaadi", "Yatayat", "Manchhal", "Rasta", "Sthanak",
]

HOSPITALITY_KEYWORDS = [
    "Hotel", "Motel", "Inn", "Resort", "Hostel", "Lodge", "Guesthouse",
    "Restaurant", "Cafe", "Coffee", "Eating", "Dinner", "Lunch",
    "Breakfast", "Snack", "Dine", "Cuisine", "Menu", "Order",
    "Dhaba", "Khana", "Bhojan", "Rasoi", "Chai", "Street food",
]

EDUCATION_KEYWORDS = [
    "School", "College", "University", "Campus", "Student", "Study",
    "Class", "Learning", "Academic", "Exam", "Teacher", "Lecture",
    "Admission", "Graduation", "Tutorial", "Education",
    "Pathshala", "Vidyalaya", "Mahavidyalaya", "Shiksha", "Vidyarthi",
]

HEALTHCARE_KEYWORDS = [
    "Hospital", "Clinic", "Doctor", "Medical", "Health", "Patient",
    "Treatment", "Pharmacy", "Medicine", "Appointment", "Check-up",
    "Illness", "Sick", "Recovery", "Vaccine", "Emergency", "Surgery",
    "Vaidya", "Chikitsalaya", "Aushadhi", "Aarogya",
]

RECREATION_KEYWORDS = [
    "Park", "Playground", "Sports Facility", "Swimming Pool", "Gym",
    "Fitness Center", "Spa", "Amusement Park", "Zoo", "Garden",
    "Beach", "Golf Course", "Theater", "Cinema", "Arcade",
    "Recreation", "Entertainment", "Leisure", "Fun", "Enjoy",
    "Movie", "Game", "Play", "Sports", "Exercise", "Fitness",
    "Udyan", "Krida", "KheL", "Vyayam", "Manoranjan",
]

RELIGIOUS_KEYWORDS = [
    "Church", "Temple", "Mosque", "Synagogue", "Gurudwara", "Shrine",
    "Cemetery", "Crematorium", "Chapel", "Religious Site",
    "Prayer", "Worship", "Ceremony", "Festival", "Celebration",
    "Spiritual", "Community", "Faith", "Ritual", "Sacred",
    "Mandir", "Masjid", "Gurdwara", "Puja", "Namaz",
]

CIVIC_KEYWORDS = [
    "Library", "Public Park", "Community Hall", "Police Station",
    "Fire Station", "Government Office", "Public Restroom", "Town Hall",
    "City Hall", "Municipal Building", "Court House", "Military Base",
    "Post Office", "Embassy",
]

AGRICULTURAL_KEYWORDS = [
    "Farm", "Agricultural Land", "Crop Field", "Orchard", "Vineyard",
    "Dairy", "Poultry", "Barn", "Greenhouse", "Livestock", "Pasture",
    "Plantation", "Farming Equipment", "Tractor",
    "Kheti", "Khetihaad", "Fasul", "Beej", "Khad", "Sinchai", "Pashu",
]

UTILITY_KEYWORDS = [
    "Power Plant", "Water Treatment", "Sewage Plant", "Gas Station",
    "Petrol Pump", "Electric Substation", "Water Pump", "Recycling Center",
    "Wind Farm", "Solar Farm",
]

NATURAL_KEYWORDS = [
    "National Park", "Wetland", "Marsh", "Forest", "Wildlife Sanctuary",
    "Conservation Area", "Protected Area", "Green Zone", "Eco Park",
]

CULTURAL_KEYWORDS = [
    "Museum", "Art Gallery", "Heritage Site", "Monument", "Historic Site",
    "Archaeological Site", "Cultural Center", "Convention Center",
]

SENTIMENT_KEYWORDS = [
    "Love", "Amazing", "Great", "Awesome", "Perfect", "Beautiful",
    "Lovely", "Wonderful", "Fantastic", "Excellent", "Best",
    "Busy", "Thriving", "Vibrant", "Lively", "Congested",
    "Stuck", "Delayed", "Chaos", "Messy", "Dirty", "Noisy",
    "Poor", "Bad", "Awful", "Problem", "Exhausted", "Tired",
]

# ==========================
# COMBINED KEYWORD LIST
# ==========================
KEYWORDS = (
    RESIDENTIAL_KEYWORDS +
    COMMERCIAL_KEYWORDS +
    INDUSTRIAL_KEYWORDS +
    TRANSPORT_KEYWORDS +
    HOSPITALITY_KEYWORDS +
    EDUCATION_KEYWORDS +
    HEALTHCARE_KEYWORDS +
    RECREATION_KEYWORDS +
    RELIGIOUS_KEYWORDS +
    CIVIC_KEYWORDS +
    AGRICULTURAL_KEYWORDS +
    UTILITY_KEYWORDS +
    NATURAL_KEYWORDS +
    CULTURAL_KEYWORDS +
    SENTIMENT_KEYWORDS
)

print(f"[INFO] Loaded {len(LOCATIONS)} locations and {len(KEYWORDS)} keywords")
print(f"[INFO] Total possible queries: {len(LOCATIONS) * len(KEYWORDS):,}")
