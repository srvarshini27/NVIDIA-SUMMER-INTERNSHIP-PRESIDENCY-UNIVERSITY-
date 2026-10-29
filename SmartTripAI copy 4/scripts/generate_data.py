import os
import random
import pickle
import numpy as np
import pandas as pd

# Set random seed for reproducibility
random.seed(42)
np.random.seed(42)

# Define 45 major tourist cities/states in India with realistic coordinates
CITIES = {
    "Jaipur": {"state": "Rajasthan", "lat": 26.9124, "lon": 75.7873},
    "Udaipur": {"state": "Rajasthan", "lat": 24.5854, "lon": 73.7125},
    "Jodhpur": {"state": "Rajasthan", "lat": 26.2389, "lon": 73.0243},
    "Jaisalmer": {"state": "Rajasthan", "lat": 26.9157, "lon": 70.9083},
    "Panaji": {"state": "Goa", "lat": 15.4909, "lon": 73.8278},
    "Calangute": {"state": "Goa", "lat": 15.5448, "lon": 73.7550},
    "Margao": {"state": "Goa", "lat": 15.2736, "lon": 73.9582},
    "Mumbai": {"state": "Maharashtra", "lat": 19.0760, "lon": 72.8777},
    "Pune": {"state": "Maharashtra", "lat": 18.5204, "lon": 73.8567},
    "Mahabaleshwar": {"state": "Maharashtra", "lat": 17.9258, "lon": 73.6558},
    "Lonavala": {"state": "Maharashtra", "lat": 18.7557, "lon": 73.4091},
    "Bengaluru": {"state": "Karnataka", "lat": 12.9716, "lon": 77.5946},
    "Mysore": {"state": "Karnataka", "lat": 12.2958, "lon": 76.6394},
    "Coorg": {"state": "Karnataka", "lat": 12.3375, "lon": 75.8069},
    "Hampi": {"state": "Karnataka", "lat": 15.3350, "lon": 76.4600},
    "Kochi": {"state": "Kerala", "lat": 9.9312, "lon": 76.2673},
    "Munnar": {"state": "Kerala", "lat": 10.0889, "lon": 77.0595},
    "Alleppey": {"state": "Kerala", "lat": 9.4981, "lon": 76.3388},
    "Wayanad": {"state": "Kerala", "lat": 11.6854, "lon": 76.1320},
    "Chennai": {"state": "Tamil Nadu", "lat": 13.0827, "lon": 80.2707},
    "Ooty": {"state": "Tamil Nadu", "lat": 11.4102, "lon": 76.6950},
    "Kodaikanal": {"state": "Tamil Nadu", "lat": 10.2381, "lon": 77.4892},
    "Madurai": {"state": "Tamil Nadu", "lat": 9.9252, "lon": 78.1198},
    "New Delhi": {"state": "Delhi", "lat": 28.6139, "lon": 77.2090},
    "Agra": {"state": "Uttar Pradesh", "lat": 27.1767, "lon": 78.0081},
    "Varanasi": {"state": "Uttar Pradesh", "lat": 25.3176, "lon": 82.9739},
    "Lucknow": {"state": "Uttar Pradesh", "lat": 26.8467, "lon": 80.9462},
    "Srinagar": {"state": "Jammu & Kashmir", "lat": 34.0837, "lon": 74.7973},
    "Gulmarg": {"state": "Jammu & Kashmir", "lat": 34.0484, "lon": 74.3805},
    "Leh": {"state": "Ladakh", "lat": 34.1526, "lon": 77.5771},
    "Kolkata": {"state": "West Bengal", "lat": 22.5726, "lon": 88.3639},
    "Darjeeling": {"state": "West Bengal", "lat": 27.0410, "lon": 88.2627},
    "Shimla": {"state": "Himachal Pradesh", "lat": 31.1048, "lon": 77.1734},
    "Manali": {"state": "Himachal Pradesh", "lat": 32.2396, "lon": 77.1887},
    "Dharamshala": {"state": "Himachal Pradesh", "lat": 32.2190, "lon": 76.3234},
    "Rishikesh": {"state": "Uttarakhand", "lat": 30.0869, "lon": 78.2676},
    "Nainital": {"state": "Uttarakhand", "lat": 29.3803, "lon": 79.4636},
    "Mussoorie": {"state": "Uttarakhand", "lat": 30.4599, "lon": 78.0664},
    "Hyderabad": {"state": "Telangana", "lat": 17.3850, "lon": 78.4867},
    "Ahmedabad": {"state": "Gujarat", "lat": 23.0225, "lon": 72.5714},
    "Amritsar": {"state": "Punjab", "lat": 31.6340, "lon": 74.8723},
    "Bhubaneswar": {"state": "Odisha", "lat": 20.2961, "lon": 85.8245},
    "Puri": {"state": "Odisha", "lat": 19.8134, "lon": 85.8315},
    "Guwahati": {"state": "Assam", "lat": 26.1158, "lon": 91.7086},
    "Gangtok": {"state": "Sikkim", "lat": 27.3314, "lon": 88.6138}
}

CATEGORIES = ['Nature', 'Historical', 'Religious', 'Adventure', 'Cultural', 'Shopping', 'Food', 'Modern']

CATEGORY_WORDS = {
    'Nature': {
        'nouns': ["Falls", "Lake", "Valley", "Peak", "Sunset Point", "Wildlife Reserve", "Hills", "Meadow", "Cave", "Beach", "River Confluence", "Gardens"],
        'prefixes': ["Emerald", "Whispering", "Mist-Clad", "Scenic", "Silver", "Hidden", "Silent", "Golden", "Serene", "Cloudy"],
        'details': "scenic panoramic views of lakes and mountains, lush green pathways, and rich local biodiversity",
        'food': "fresh local coconut water and hot sweet corn"
    },
    'Historical': {
        'nouns': ["Fort", "Palace", "Museum", "Heritage Centre", "Gateway", "Memorial", "Ruin", "Castle", "Ancient Caves", "Tomb"],
        'prefixes': ["Royal", "Victorian", "Imperial", "Grand", "Heritage", "Sovereign", "Majestic", "Historic", "Victory"],
        'details': "intricate stone carvings, ancient military artifacts, museum displays, and majestic historical architecture",
        'food': "traditional local tea and snacks from century-old stalls"
    },
    'Religious': {
        'nouns': ["Temple", "Church", "Mosque", "Monastery", "Shrine", "Ashram", "Cathedral", "Gurudwara"],
        'prefixes': ["Sacred", "Holy", "Spiritual", "Divine", "Tranquil", "Golden", "Eternal", "Blessed"],
        'details': "peaceful prayer halls, spiritual meditation gardens, detailed wall murals, and gorgeous traditional architecture",
        'food': "holy prasadam and authentic local vegetarian sweets"
    },
    'Adventure': {
        'nouns': ["Trekking Trail", "Rafting Camp", "Paragliding Launch", "Safari Zone", "Zip-line Valley", "Camping Ridge", "Climbing Wall"],
        'prefixes': ["Wild", "Adventure", "Apex", "Summit", "Vanguard", "Rogue", "Extreme", "Gorge"],
        'details': "thrilling outdoor adventure sports, rugged terrain paths, and panoramic views of nature that get your adrenaline pumping",
        'food': "wood-fired camp barbecue and local energy beverages"
    },
    'Cultural': {
        'nouns': ["Art Village", "Amphitheatre", "Heritage Craft Complex", "Cultural Theatre", "Folk Centre", "Traditional Bazaar"],
        'prefixes': ["Ethnic", "Folk", "Classical", "Artistic", "Legacy", "Indigenous", "Creative"],
        'details': "vibrant traditional dance displays, local handicraft workshops, and rich cultural heritage exhibits",
        'food': "highly authentic multi-course regional platters"
    },
    'Shopping': {
        'nouns': ["Market", "Bazaar", "Emporium", "Flea Market", "Shopping Arcade", "Cooperative Store", "Spices Corner"],
        'prefixes': ["Vibrant", "Local", "Central", "Traditional", "Craft", "Bustling", "Royal"],
        'details': "stalls filled with handmade textiles, leather goods, brass items, local fabrics, and unique handmade souvenirs",
        'food': "spicy local street snacks and cold refreshing juices"
    },
    'Food': {
        'nouns': ["Food Street", "Gourmet Court", "Historic Cafe", "Sweet Alley", "Spice Lane", "Chaat Corner", "Dhaba Zone"],
        'prefixes': ["Culinary", "Traditional", "Delight", "Savory", "Legacy", "Authentic", "Flavors"],
        'details': "dozens of legendary food joints serving authentic regional recipes passed down through generations of chefs",
        'food': "signature dishes, hot local breads, and sweet traditional desserts"
    },
    'Modern': {
        'nouns': ["Amusement Park", "Science Arena", "Planetarium", "Aquarium", "Botanical Conservatory", "Sky Deck", "Art Gallery"],
        'prefixes': ["Tech", "Futuristic", "Infinity", "Cosmo", "Metro", "Apex", "Stellar"],
        'details': "interactive digital exhibits, virtual reality play zones, and state-of-the-art entertainment and science options",
        'food': "fusion modern cuisine, continental snacks, and specialty coffees"
    }
}

# Reliable Unsplash Image ID patterns mapping category items to actual high-quality photos
CATEGORY_IMAGES = {
    'Nature': [
        "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1447752875215-b2761acb3c5d?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1472214222541-d510753a4907?auto=format&fit=crop&w=800&q=80"
    ],
    'Historical': [
        "https://images.unsplash.com/photo-1548013146-72479768bada?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1564507592333-c60657eea523?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1599661046289-e31897846e41?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1585135497273-1a85b0904aaf?auto=format&fit=crop&w=800&q=80"
    ],
    'Religious': [
        "https://images.unsplash.com/photo-1608958415217-fb50730d70eb?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1590077428593-a55bb07c4665?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1542838132-92c53300491e?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1609137144813-90920556f8f5?auto=format&fit=crop&w=800&q=80"
    ],
    'Adventure': [
        "https://images.unsplash.com/photo-1526772662000-3f88f10405ff?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1533240332313-0db49b439ad3?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1502784444187-359ac186c5bb?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=800&q=80"
    ],
    'Cultural': [
        "https://images.unsplash.com/photo-1532375810709-75b1da00537c?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1605647540924-852290f6b0d5?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1561361513-2d000a50f0db?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1514222134-b57cbb8ce073?auto=format&fit=crop&w=800&q=80"
    ],
    'Shopping': [
        "https://images.unsplash.com/photo-1596464716127-f2a82984de30?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1601379327928-2ffd8a11e27e?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1441986300917-64674bd600d8?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1555529669-e69e7aa0ba9a?auto=format&fit=crop&w=800&q=80"
    ],
    'Food': [
        "https://images.unsplash.com/photo-1601050690597-df056fb4ce78?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1606491956689-2ea866880c84?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1565557623262-b51c2513a641?auto=format&fit=crop&w=800&q=80"
    ],
    'Modern': [
        "https://images.unsplash.com/photo-1517048676732-d65bc937f952?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1461205330090-618651779d6d?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&w=800&q=80"
    ]
}

BEST_TIMES = ["October to March", "June to September", "Year-round", "November to February", "March to June"]
TOURIST_TYPES = ["Solo", "Family", "Couple", "Friends", "All"]

# Generate Tourism Dataset (Minimum 2000 rows)
def generate_tourism_dataset():
    data = []
    place_id = 0
    places_per_city = 45  # 45 cities * 45 = 2025 rows
    
    for city, info in CITIES.items():
        state = info["state"]
        base_lat = info["lat"]
        base_lon = info["lon"]
        
        for i in range(places_per_city):
            category = CATEGORIES[i % len(CATEGORIES)]
            words = CATEGORY_WORDS[category]
            
            # Combine to make a unique name
            prefix = words["prefixes"][(i + place_id) % len(words["prefixes"])]
            noun = words["nouns"][(i * 3 + place_id) % len(words["nouns"])]
            
            # Formulate Place Name
            if i % 3 == 0:
                place_name = f"{prefix} {noun} of {city}"
            elif i % 3 == 1:
                place_name = f"{city} {prefix} {noun}"
            else:
                place_name = f"{prefix} {city} {noun}"
                
            # Random offset coordinates centered around actual city lat/lon
            lat = base_lat + random.uniform(-0.06, 0.06)
            lon = base_lon + random.uniform(-0.06, 0.06)
            
            # Rating between 3.5 and 4.9
            rating = round(random.uniform(3.5, 4.9), 1)
            
            # Entrance Fee logic
            if category in ['Nature', 'Religious', 'Shopping', 'Food']:
                entrance_fee = 0 if random.random() > 0.4 else random.choice([20, 50, 100])
            elif category in ['Historical', 'Modern']:
                entrance_fee = random.choice([50, 100, 150, 200, 250, 300])
            else:  # Adventure / Cultural
                entrance_fee = random.choice([100, 200, 300, 400, 500, 600])
                
            # Average visit hours
            if category in ['Religious', 'Food', 'Shopping']:
                visit_hours = round(random.uniform(1.0, 2.0), 1)
            elif category in ['Nature', 'Modern', 'Cultural']:
                visit_hours = round(random.uniform(1.5, 3.0), 1)
            else:
                visit_hours = round(random.uniform(2.0, 4.0), 1)
                
            # Popularity score
            popularity = round(random.uniform(50.0, 100.0), 1)
            
            # Tourist type
            tourist_type = random.choice(TOURIST_TYPES)
            
            # Price fare (cost to travel inside city to this attraction)
            price_fare = random.choice([50, 100, 150, 200, 250, 300])
            
            # Best time to visit
            best_time = random.choice(BEST_TIMES)
            
            # Construct description
            desc_start = random.choice([
                f"Located in the heart of {city}, this beautiful {category.lower()} destination is a key highlight of {state} tourism.",
                f"Situated in a scenic setting in {city}, this {category.lower()} attraction offers travelers an unforgettable local experience.",
                f"A famous landmark in {city}, this {category.lower()} spot is highly popular for its serene environment and unique style."
            ])
            desc_body = random.choice([
                f"Known as a legendary {noun.lower()} in the region, it features {words['details']} and attracts visitors from all over the world.",
                f"This notable {noun.lower()} stands as an iconic location offering {words['details']}, embodying the real culture of {state}."
            ])
            desc_end = f"Visitors can enjoy {words['food']} at local vendors and capture beautiful memories here. Highly recommended for a {tourist_type.lower()} trip."
            description = f"{desc_start} {desc_body} {desc_end}"
            
            # Map Unsplash photos matching the category
            image_url = f"https://source.unsplash.com/800x500/?tourism,{place_name},{city}"
            
            data.append({
                "Place": place_name,
                "City": city,
                "State": state,
                "Category": category,
                "Description": description,
                "Rating": rating,
                "Latitude": round(lat, 5),
                "Longitude": round(lon, 5),
                "Best_Time": best_time,
                "Entrance_Fee": entrance_fee,
                "Average_Visit_Hours": visit_hours,
                "Popularity_Score": popularity,
                "Tourist_Type": tourist_type,
                "Price_Fare": price_fare,
                "Image_URL": image_url
            })
            place_id += 1
            
    df = pd.DataFrame(data)
    return df

# Generate Hotel Dataset (Minimum 3000 rows)
def generate_hotel_dataset():
    data = []
    hotel_prefixes = ["Grand", "Royal", "Saffron Stays", "Golden Gate", "Vista", "The Fern", "Taj", "Oberoi", "Radisson", "Park Hyatt", "Ginger", "Novotel", "Treebo", "FabHotel", "Capital O", "Stark Woods", "Ritz", "Orchard", "Whispering Palms", "Pine Wood", "Paradise", "Blue Lagoon", "Silver Sands", "Emerald Haven", "Alpine Lodge", "Clarks Inn", "Mayfair", "Lemon Tree"]
    hotel_nouns = ["Inn", "Resort", "Suites", "Retreat", "Hotel", "Palace", "Villas", "Lodge", "Haven", "Stays", "Manor", "Castle", "Chalet"]
    
    amenities_pool = ["WiFi", "Swimming Pool", "Spa", "Gym", "Restaurant", "Bar", "AC", "Free Breakfast", "Room Service", "Free Parking", "Laundry Service", "Valet Parking", "24/7 Security", "Balcony Room"]
    
    hotels_per_city = 70  # 45 cities * 70 = 3150 rows
    hotel_id = 0
    
    for city in CITIES.keys():
        for i in range(hotels_per_city):
            prefix = hotel_prefixes[(i + hotel_id) % len(hotel_prefixes)]
            noun = hotel_nouns[(i * 2 + hotel_id) % len(hotel_nouns)]
            hotel_name = f"{prefix} {noun} {city} {i + 1}"
            
            rating = round(random.uniform(3.0, 5.0), 1)
            
            # Set price matching rating tier
            if rating < 3.8:
                price = random.randint(800, 2000)
                description = f"Comfortable budget-friendly lodging in {city}. Offers clean rooms, helpful service, and basic amenities perfect for cost-conscious travelers."
            elif rating < 4.4:
                price = random.randint(2000, 5000)
                description = f"Modern mid-range hotel in {city} offering excellent value, well-appointed guest rooms, great dining, and a convenient location close to key city highlights."
            else:
                price = random.randint(5000, 18000)
                description = f"Premium luxury accommodation in {city}. Features world-class dining, customized guest services, elegant architecture, and a highly scenic environment."
                
            # Select random amenities
            num_amenities = random.randint(4, 8)
            amenities = ", ".join(random.sample(amenities_pool, num_amenities))
            
            distance = round(random.uniform(0.1, 9.5), 1)
            reviews = random.randint(10, 2000)
            
            data.append({
                "Hotel_Name": hotel_name,
                "City": city,
                "Hotel_Rating": rating,
                "Hotel_Price": price,
                "Description": description,
                "Amenities": amenities,
                "Distance_From_Attraction": distance,
                "Review_Count": reviews
            })
            hotel_id += 1
            
    df = pd.DataFrame(data)
    return df

# Generate Nearby Attractions Dataset (Minimum 5000 rows)
def generate_nearby_attractions_dataset(tourism_df):
    data = []
    
    categories = ["Food & Dining", "Shopping", "Activity", "Viewpoint", "Local Market", "Transit"]
    
    food_prefixes = ["Laziz", "The Spicy", "Royal", "Annapurna", "Chai Villa", "Cafe", "Bistro", "Street", "Gourmet", "Desi"]
    food_nouns = ["Dhaba", "Diner", "Treats", "Point", "Spot", "Kitchen", "Chaat Bhandar", "Cafe", "Bakery", "Corner"]
    
    shop_prefixes = ["Handicrafts", "Ethnic", "Local", "Central", "Souvenir", "Traditional", "Artisans", "Bustling"]
    shop_nouns = ["Bazaar", "Market", "Emporium", "Flea Market", "Corner", "Arcade", "Cooperative", "Hub"]
    
    activity_nouns = ["Hiking Point", "Boating Lake", "Adventure Cliff", "Sunset Deck", "Walkway Park", "Heritage Walk", "Photography Spot", "Cable Car Station"]
    
    # Generate 3 nearby attractions for each primary place in the tourism dataset
    # Total rows: 2025 * 3 = 6075 rows
    for index, row in tourism_df.iterrows():
        place_name = row["Place"]
        city = row["City"]
        
        # Attraction 1: Food Spot
        food_prefix = random.choice(food_prefixes)
        food_noun = random.choice(food_nouns)
        attr1_name = f"{food_prefix} {food_noun} near {place_name}"
        dist1 = round(random.uniform(0.1, 2.5), 1)
        rating1 = round(random.uniform(3.5, 4.9), 1)
        data.append({
            "Attraction_Name": attr1_name,
            "Nearby_Place": place_name,
            "Distance_KM": dist1,
            "Category": "Food & Dining",
            "Rating": rating1
        })
        
        # Attraction 2: Shopping Spot
        shop_prefix = random.choice(shop_prefixes)
        shop_noun = random.choice(shop_nouns)
        attr2_name = f"{shop_prefix} {shop_noun} near {place_name}"
        dist2 = round(random.uniform(0.2, 3.5), 1)
        rating2 = round(random.uniform(3.5, 4.8), 1)
        data.append({
            "Attraction_Name": attr2_name,
            "Nearby_Place": place_name,
            "Distance_KM": dist2,
            "Category": "Shopping",
            "Rating": rating2
        })
        
        # Attraction 3: Activity / Viewpoint / Transit
        cat3 = random.choice(["Activity", "Viewpoint", "Local Market", "Transit"])
        noun3 = random.choice(activity_nouns) if cat3 in ["Activity", "Viewpoint"] else f"{cat3} Corner"
        attr3_name = f"{noun3} near {place_name}"
        dist3 = round(random.uniform(0.3, 4.9), 1)
        rating3 = round(random.uniform(3.5, 5.0), 1)
        data.append({
            "Attraction_Name": attr3_name,
            "Nearby_Place": place_name,
            "Distance_KM": dist3,
            "Category": cat3,
            "Rating": rating3
        })
        
    df = pd.DataFrame(data)
    return df

def main():
    print("Starting synthetic dataset generation...")
    
    # Ensure data folder exists
    os.makedirs("data", exist_ok=True)
    
    # Generate datasets
    print("Generating tourism dataset with Image_URL...")
    tourism_df = generate_tourism_dataset()
    tourism_df.to_csv("data/tourism_dataset.csv", index=False)
    print(f"Saved tourism_dataset.csv with {len(tourism_df)} rows.")
    
    print("Generating hotel dataset...")
    hotel_df = generate_hotel_dataset()
    hotel_df.to_csv("data/hotel_dataset.csv", index=False)
    print(f"Saved hotel_dataset.csv with {len(hotel_df)} rows.")
    
    print("Generating nearby attractions dataset...")
    attractions_df = generate_nearby_attractions_dataset(tourism_df)
    attractions_df.to_csv("data/nearby_attractions.csv", index=False)
    print(f"Saved nearby_attractions.csv with {len(attractions_df)} rows.")
    
    # Model Embeddings generation
    print("Initializing SentenceTransformers model (all-MiniLM-L6-v2)...")
    from sentence_transformers import SentenceTransformer
    
    model = SentenceTransformer("all-MiniLM-L6-v2")
    
    print("Preparing texts for embeddings...")
    # Generate embeddings for Place, Category, Description
    texts_to_embed = (tourism_df["Place"] + " | " + tourism_df["Category"] + " | " + tourism_df["Description"]).tolist()
    
    print("Computing embeddings (this might take a minute)...")
    embeddings = model.encode(texts_to_embed, show_progress_bar=True)
    
    # Save embeddings
    np.save("data/tourism_embeddings.npy", embeddings)
    print("Saved tourism_embeddings.npy.")
    
    # Save metadata
    with open("data/tourism_metadata.pkl", "wb") as f:
        pickle.dump(tourism_df, f)
    print("Saved tourism_metadata.pkl.")
    
    print("Data generation and embedding precomputation completed successfully!")

if __name__ == "__main__":
    main()
