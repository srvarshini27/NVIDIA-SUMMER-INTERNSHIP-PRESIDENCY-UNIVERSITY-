import os
import pickle
import urllib.parse
import hashlib
import json
import numpy as np
import pandas as pd
import streamlit as st
from sentence_transformers import SentenceTransformer

def has_valid_image_url(row):
    """Checks if Image_URL exists and is valid (not empty, not NaN, and starts with http) in a row."""
    if row is None:
        return False
    url = None
    try:
        if isinstance(row, dict):
            url = row.get("Image_URL")
        else:
            if hasattr(row, "index") and "Image_URL" in row.index:
                url = row["Image_URL"]
            elif hasattr(row, "columns") and "Image_URL" in row.columns:
                url = row["Image_URL"]
            elif hasattr(row, "get"):
                url = row.get("Image_URL")
            elif "Image_URL" in row:
                url = row["Image_URL"]
    except Exception:
        pass
    if pd.isna(url) or not url or not isinstance(url, str) or not url.strip().startswith("http"):
        return False
    return True

def get_local_image_base64(image_path):
    """Converts a local image file to a base64 Data URL for high performance offline rendering."""
    import base64
    try:
        if os.path.exists(image_path):
            with open(image_path, "rb") as f:
                data = f.read()
                return f"data:image/jpeg;base64,{base64.b64encode(data).decode('utf-8')}"
    except Exception:
        pass
    # Return a transparent 1x1 base64 encoded PNG on failure so it never shows a broken icon
    return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="

def get_category_fallback_image(category):
    """Returns the base64 encoded local category fallback image."""
    mapping = {
        "Nature": "assets/images/nature.jpg",
        "Historical": "assets/images/heritage.jpg",
        "Religious": "assets/images/religious.jpg",
        "Adventure": "assets/images/adventure.jpg",
        "Shopping": "assets/images/city.jpg",
        "Local Market": "assets/images/city.jpg",
        "Food & Dining": "assets/images/city.jpg",
        "Cultural": "assets/images/city.jpg",
        "Food": "assets/images/city.jpg",
        "Modern": "assets/images/city.jpg",
        "Beach": "assets/images/beach.jpg",
        "Hill Station": "assets/images/hill_station.jpg",
        "Wildlife": "assets/images/wildlife.jpg"
    }
    path = mapping.get(category, "assets/images/nature.jpg")
    return get_local_image_base64(path)

def get_image_url(row):
    """Safely extracts details from a row and returns a highly relevant local image base64 URL."""
    if row is None:
        return get_local_image_base64("assets/images/nature.jpg")
        
    place_name = ""
    city_name = ""
    state_name = ""
    category_name = ""
    
    # Extract fields from dict or Series (checking capitalized & lowercase keys)
    if isinstance(row, dict):
        place_name = row.get("Place", row.get("place_name", ""))
        city_name = row.get("City", row.get("city", ""))
        state_name = row.get("State", row.get("state", ""))
        category_name = row.get("Category", row.get("category", ""))
    else:
        try:
            if hasattr(row, "index"):
                for k in ["Place", "place_name"]:
                    if k in row.index: place_name = row[k]
                for k in ["City", "city"]:
                    if k in row.index: city_name = row[k]
                for k in ["State", "state"]:
                    if k in row.index: state_name = row[k]
                for k in ["Category", "category"]:
                    if k in row.index: category_name = row[k]
        except Exception:
            pass
            
    # Clean up fields
    place_name = str(place_name).strip().lower() if not pd.isna(place_name) else ""
    city_name = str(city_name).strip().lower() if not pd.isna(city_name) else ""
    state_name = str(state_name).strip().lower() if not pd.isna(state_name) else ""
    category_name = str(category_name).strip().lower() if not pd.isna(category_name) else ""
    
    # Step 1: Check for exact destination image exists locally
    if "mysore palace" in place_name:
        return get_local_image_base64("assets/images/mysore_palace.jpg")
    elif "coorg" in place_name or "coorg" in city_name:
        return get_local_image_base64("assets/images/coorg.jpg")
    elif "ooty" in place_name or "ooty" in city_name:
        return get_local_image_base64("assets/images/ooty.jpg")
    elif "hampi" in place_name or "hampi" in city_name:
        return get_local_image_base64("assets/images/hampi.jpg")
    elif "goa" in place_name or "goa" in city_name:
        return get_local_image_base64("assets/images/goa.jpg")
        
    # Step 2: Use category-based local images
    full_text = f"{place_name} {category_name} {city_name}"
    
    # Beach check
    if "beach" in full_text or "coast" in full_text or "shore" in full_text:
        return get_local_image_base64("assets/images/beach.jpg")
    # Hill Station check
    elif any(kw in full_text for kw in ["hill", "mountain", "peak", "valley", "tea garden", "mist", "ridge"]) or any(city_kw in city_name for city_kw in ["ooty", "munnar", "shimla", "manali", "gulmarg", "dharamshala", "kodaikanal", "mussoorie", "nainital", "darjeeling"]):
        return get_local_image_base64("assets/images/hill_station.jpg")
    # Heritage / Historical check
    elif "historical" in category_name or any(kw in full_text for kw in ["fort", "palace", "museum", "monument", "heritage", "ruin", "ancient", "gateway", "memorial", "castle", "tomb"]):
        return get_local_image_base64("assets/images/heritage.jpg")
    # Religious check
    elif "religious" in category_name or any(kw in full_text for kw in ["temple", "church", "mosque", "monastery", "shrine", "cathedral", "gurudwara", "ashram", "holy", "sacred", "spiritual"]):
        return get_local_image_base64("assets/images/religious.jpg")
    # Wildlife check
    elif any(kw in full_text for kw in ["wildlife", "safari", "zoo", "national park", "reserve", "forest", "tiger", "sanctuary"]):
        return get_local_image_base64("assets/images/wildlife.jpg")
    # Adventure check
    elif "adventure" in category_name or any(kw in full_text for kw in ["trek", "hiking", "rafting", "camp", "climbing", "zipline", "paragliding", "skiing"]):
        return get_local_image_base64("assets/images/adventure.jpg")
    # Nature check
    elif "nature" in category_name or any(kw in full_text for kw in ["lake", "falls", "waterfall", "cave", "sunset", "garden", "confluence", "meadow", "scenic"]):
        return get_local_image_base64("assets/images/nature.jpg")
    # City / Modern check (Shopping, Food, Modern, Cultural)
    elif any(cat_kw in category_name for cat_kw in ["shopping", "food", "modern", "cultural", "local market", "dining"]) or any(kw in full_text for kw in ["market", "bazaar", "mall", "street", "cafe", "bistro", "dhaba", "culinary", "amusement", "art gallery", "museum", "science"]):
        return get_local_image_base64("assets/images/city.jpg")
        
    # Default Fallback (never return broken image!)
    return get_local_image_base64("assets/images/nature.jpg")


def get_google_images_link(place_name, city_name=""):
    """Generates a Google Images search URL for the given place name and city name."""
    query_str = f"{place_name}"
    if city_name:
        query_str += f" {city_name}"
    query_str += " tourism"
    query = urllib.parse.quote(query_str)
    return f"https://www.google.com/search?tbm=isch&q={query}"

def get_local_food_recommendations(state_name):
    """Returns local food specialties based on the state name."""
    state_foods = {
        "Rajasthan": ["Dal Baati Churma", "Gatte ki Sabzi", "Pyaz Kachori", "Laal Maas"],
        "Goa": ["Goan Fish Curry", "Bebinca", "Pork Vindaloo", "Goan Fish Recheado"],
        "Maharashtra": ["Vada Pav", "Pav Bhaji", "Misal Pav", "Puran Poli"],
        "Karnataka": ["Bisi Bele Bath", "Mysore Pak", "Ragi Mudde", "Coorg Pandi Curry"],
        "Kerala": ["Appam with Stew", "Karimeen Pollichathu", "Malabar Parotta", "Kerala Sadya"],
        "Tamil Nadu": ["Dosa", "Idli & Sambar", "Chettinad Chicken", "Filter Coffee"],
        "Delhi": ["Chole Bhature", "Butter Chicken", "Aloo Chaat", "Paranthas"],
        "Uttar Pradesh": ["Tunday Kababi", "Agra Peta", "Malai Yo", "Kachori Sabzi"],
        "Jammu & Kashmir": ["Rogan Josh", "Kahwa Tea", "Yakhni", "Matsgand"],
        "Ladakh": ["Thukpa", "Skyu", "Momos", "Butter Tea"],
        "West Bengal": ["Roshogolla", "Machher Jhol", "Luchi Alur Dom", "Sandesh"],
        "Himachal Pradesh": ["Siddu", "Madra", "Dhaam", "Tudkiya Bhath"],
        "Uttarakhand": ["Kafuli", "Aloo ke Gutke", "Bal Mithai", "Dubuk"],
        "Telangana": ["Hyderabadi Biryani", "Haleem", "Double ka Meetha", "Qubani ka Meetha"],
        "Gujarat": ["Dhokla", "Thepla", "Khandvi", "Undhiyu"],
        "Punjab": ["Sarson ka Saag & Makki ki Roti", "Amritsari Kulcha", "Lassi"],
        "Odisha": ["Chhena Poda", "Dalma", "Rasabali", "Pakhala Bhata"],
        "Assam": ["Masor Tenga", "Khaar", "Duck Meat Curry", "Pitha"],
        "Sikkim": ["Momos", "Thukpa", "Phagshapa", "Gundruk"]
    }
    return state_foods.get(state_name, ["Butter Chicken", "Masala Dosa", "Paneer Tikka", "Gulab Jamun"])

def get_packing_checklist(categories):
    """Generates a packing checklist based on the category types in the trip."""
    checklist = ["Comfortable footwear", "ID card & copies", "First-aid kit", "Mobile charger & power bank"]
    cats = {c.lower() for c in categories}
    if "nature" in cats or "adventure" in cats:
        checklist.extend(["Trekking shoes", "Insect repellent", "Reusable water bottle", "Sunscreen & sunglasses", "Rain jacket or umbrella"])
    if "historical" in cats or "cultural" in cats:
        checklist.extend(["Camera", "Hat/Cap", "Guidebooks/Maps", "Modest clothing for heritage sites"])
    if "religious" in cats:
        checklist.extend(["Modest/Conservative clothing", "Slip-on shoes", "Headscarf or handkerchief"])
    if "shopping" in cats or "food" in cats:
        checklist.extend(["Eco-friendly shopping bags", "Hand sanitizer", "Tissues/Wet wipes", "Small cash denominations"])
    return list(dict.fromkeys(checklist)) # Remove duplicates

def get_emergency_info():
    """Returns emergency contact details."""
    return {
        "National Emergency Number": "112",
        "Police Helpline": "100 / 112",
        "Ambulance / Medical": "108 / 102",
        "Tourist Helpline (Ministry of Tourism)": "1363 (24/7 toll-free, multi-lingual)",
        "Women Helpline": "1091"
    }


# Upgraded custom CSS for modern, premium, colorful tourism-themed UI
CUSTOM_CSS = """
<style>
    /* Global Styles & Animations */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Smooth page fade-in animation */
    .stApp {
        background: radial-gradient(circle at top right, #1e293b, #0b0f19);
        animation: fadeIn 0.8s ease-out;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Header Style */
    .app-title {
        font-size: 3.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #2dd4bf 0%, #06b6d4 50%, #3b82f6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
        letter-spacing: -0.02em;
    }
    .app-subtitle {
        font-size: 1.2rem;
        color: #94a3b8;
        margin-bottom: 2.2rem;
        font-weight: 300;
    }
    
    /* Hero Banner styling */
    .hero-section {
        position: relative;
        background: linear-gradient(135deg, #0d9488 0%, #1e1b4b 100%);
        border-radius: 24px;
        height: 250px;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        margin-bottom: 35px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.4);
    }
    .hero-overlay {
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: linear-gradient(180deg, rgba(15,23,42,0.2) 0%, rgba(15,23,42,0.8) 100%);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        padding: 40px;
    }
    .hero-title {
        font-size: 2.8rem !important;
        font-weight: 800 !important;
        color: #ffffff !important;
        text-shadow: 0 4px 12px rgba(0,0,0,0.6);
        margin: 0 0 10px 0 !important;
        letter-spacing: -0.02em;
        line-height: 1.2;
    }
    .hero-subtitle {
        font-size: 1.2rem !important;
        color: #e2e8f0 !important;
        text-shadow: 0 2px 8px rgba(0,0,0,0.6);
        font-weight: 350 !important;
        max-width: 650px;
        margin: 0 !important;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0b0f19 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    section[data-testid="stSidebar"] div[class*="stSidebarUserContent"] {
        padding-top: 2rem;
    }
    
    /* Premium Travel Cards - Image Free Gradient and Glassmorphism */
    .premium-card {
        position: relative;
        background: linear-gradient(135deg, rgba(22, 38, 70, 0.55) 0%, rgba(11, 19, 43, 0.85) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        overflow: hidden;
        height: 330px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1), 
                    box-shadow 0.4s cubic-bezier(0.16, 1, 0.3, 1),
                    border-color 0.4s ease;
        margin-bottom: 35px;
        padding: 28px;
        box-sizing: border-box;
    }
    
    .premium-card:hover {
        transform: translateY(-8px) scale(1.03);
        box-shadow: 0 20px 40px rgba(45, 212, 191, 0.2);
        border-color: rgba(45, 212, 191, 0.45);
        z-index: 10;
    }
    
    .card-content {
        display: flex;
        flex-direction: column;
        height: 100%;
        justify-content: space-between;
    }
    
    .card-description {
        color: #cbd5e1;
        font-size: 0.85rem;
        line-height: 1.5;
        margin-top: 10px;
        overflow: hidden;
        display: -webkit-box;
        -webkit-line-clamp: 3;
        -webkit-box-orient: vertical;
    }

    .card-hover-button-wrapper {
        opacity: 0;
        transform: translateY(12px);
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        display: flex;
        justify-content: center;
        width: 100%;
        margin-top: auto;
    }
    
    .premium-card:hover .card-hover-button-wrapper {
        opacity: 1;
        transform: translateY(0);
    }
    
    .view-photos-btn {
        background: rgba(45, 212, 191, 0.1) !important;
        border: 1px solid rgba(45, 212, 191, 0.4) !important;
        color: #2dd4bf !important;
        text-decoration: none !important;
        border-radius: 12px !important;
        padding: 6px 18px !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        text-align: center !important;
        width: 80% !important;
        display: inline-block !important;
        transition: all 0.2s ease !important;
    }
    
    .view-photos-btn:hover {
        background: rgba(45, 212, 191, 0.25) !important;
        border-color: #2dd4bf !important;
        color: #ffffff !important;
        box-shadow: 0 4px 12px rgba(45, 212, 191, 0.2) !important;
    }
    
    /* Timeline hover photos link wrapper */
    .card-hover-button-wrapper-timeline {
        opacity: 0;
        transform: translateX(10px);
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }
    
    .timeline-card:hover .card-hover-button-wrapper-timeline {
        opacity: 1;
        transform: translateX(0);
    }
    
    /* Glassmorphic Cards */
    .glass-card {
        background: rgba(30, 41, 59, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 18px;
        padding: 30px;
        margin-bottom: 35px;
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
        transition: border-color 0.3s ease, box-shadow 0.3s ease;
    }
    .glass-card:hover {
        border-color: rgba(20, 184, 166, 0.3);
        box-shadow: 0 10px 30px rgba(20, 184, 166, 0.05);
    }
    
    /* Timeline styles for itinerary */
    .timeline-card {
        background: rgba(17, 24, 39, 0.45);
        border-left: 4px solid #14b8a6;
        border-radius: 0 16px 16px 0;
        padding: 22px 28px;
        margin-bottom: 28px;
        border-top: 1px solid rgba(255, 255, 255, 0.03);
        border-right: 1px solid rgba(255, 255, 255, 0.03);
        border-bottom: 1px solid rgba(255, 255, 255, 0.03);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
        transition: transform 0.3s cubic-bezier(0.165, 0.84, 0.44, 1), background 0.3s ease;
    }
    .timeline-card:hover {
        transform: translateX(6px);
        background: rgba(22, 30, 49, 0.6);
        border-left-color: #2dd4bf;
    }
    
    .timeline-time-col {
        font-weight: 800;
        color: #2dd4bf;
        font-size: 1rem;
        letter-spacing: 0.05em;
        min-width: 100px;
    }
    
    /* Custom Tags */
    .custom-tag {
        display: inline-block;
        background: rgba(45, 212, 191, 0.12);
        color: #2dd4bf;
        border: 1px solid rgba(45, 212, 191, 0.25);
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 8px;
        margin-bottom: 8px;
    }
    .custom-tag-sec {
        display: inline-block;
        background: rgba(249, 115, 22, 0.12);
        color: #ffedd5;
        border: 1px solid rgba(249, 115, 22, 0.25);
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 8px;
        margin-bottom: 8px;
    }
    
    /* Metrics Box */
    .metric-value {
        font-size: 2.3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-label {
        color: #94a3b8;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 600;
        margin-bottom: 4px;
    }
    
    /* Interactive Streamlit Tabs Custom Styling */
    div[data-testid="stTabs"] button[data-baseweb="tab"] {
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        color: #94a3b8 !important;
        background-color: transparent !important;
        border: none !important;
        padding: 14px 28px !important;
        transition: all 0.3s ease !important;
        border-bottom: 2px solid transparent !important;
    }
    div[data-testid="stTabs"] button[data-baseweb="tab"]:hover {
        color: #2dd4bf !important;
    }
    div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] {
        color: #2dd4bf !important;
        border-bottom: 2px solid #2dd4bf !important;
        background-color: rgba(45, 212, 191, 0.05) !important;
        border-radius: 8px 8px 0 0 !important;
    }
    
    /* Primary buttons (Plan / Generate actions) are styled to be large and prominent */
    div.stButton > button[kind="primary"] {
        border-radius: 12px !important;
        font-weight: 600 !important;
        min-height: 44px !important;
        height: 44px !important;
        font-size: 1.05rem !important;
        transition: all 0.3s ease !important;
    }
    div.stButton > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 15px rgba(20, 184, 166, 0.25) !important;
    }
    
    /* Compact, clean secondary buttons under columns (cards/itinerary) */
    div[data-testid="column"] div.stButton > button:not([kind="primary"]), 
    div[data-testid="column"] div[data-testid="stLinkButton"] > a {
        padding: 4px 8px !important;
        font-size: 0.78rem !important;
        min-height: 28px !important;
        height: 28px !important;
        line-height: 20px !important;
        border-radius: 6px !important;
        margin: 4px auto !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        max-width: 110px !important;
        width: 100% !important;
    }

    div[data-testid="column"] div.stButton > button:not([kind="primary"]):hover, 
    div[data-testid="column"] div[data-testid="stLinkButton"] > a:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(20, 184, 166, 0.15) !important;
        border-color: #2dd4bf !important;
    }

    /* Compact, clean secondary buttons globally under columns/cards */
    div.stButton > button:not([kind="primary"]), 
    div.stDownloadButton > button, 
    div[data-testid="stLinkButton"] > a {
        padding: 5px 12px !important;
        font-size: 0.82rem !important;
        min-height: 32px !important;
        height: 32px !important;
        line-height: 20px !important;
        border-radius: 8px !important;
        margin: 0 !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    div.stButton > button:not([kind="primary"]):hover, 
    div.stDownloadButton > button:hover, 
    div[data-testid="stLinkButton"] > a:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(20, 184, 166, 0.15) !important;
        border-color: #2dd4bf !important;
    }
    
    /* Divider Layout */
    .gradient-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(45, 212, 191, 0.4), transparent);
        margin: 42px 0;
    }
</style>
"""

def init_session_state():
    """Initializes the Streamlit session state fields to default values."""
    defaults = {
        "interests": "",
        "travel_style": "Solo",
        "number_of_people": 1,
        "budget": 30000.0,
        "days": 3,
        "city": "All Cities",
        "plan_generated": False,
        "recommended_destinations": None,
        "itinerary": None,
        "selected_hotel": None,
        "hotel_recommendations": None,
        "nearby_attractions": None,
        "budget_breakdown": None,
        "match_scores": None
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

def inject_styles():
    """Injects custom CSS styles into the Streamlit page."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

@st.cache_data
def load_tourism_data():
    """Loads the tourism dataset."""
    return pd.read_csv("data/tourism_dataset.csv")

@st.cache_data
def load_hotel_data():
    """Loads the hotel dataset."""
    return pd.read_csv("data/hotel_dataset.csv")

@st.cache_data
def load_nearby_attractions():
    """Loads the nearby attractions dataset."""
    return pd.read_csv("data/nearby_attractions.csv")

@st.cache_resource
def load_embeddings_and_metadata():
    """Loads precomputed embeddings and metadata."""
    embeddings = np.load("data/tourism_embeddings.npy")
    with open("data/tourism_metadata.pkl", "rb") as f:
        metadata_df = pickle.load(f)
    return embeddings, metadata_df

@st.cache_resource
def load_embedding_model():
    """Loads the SentenceTransformers model."""
    return SentenceTransformer("all-MiniLM-L6-v2")

def check_data_files():
    """Checks if all required data files exist."""
    required_files = [
        "data/tourism_dataset.csv",
        "data/hotel_dataset.csv",
        "data/nearby_attractions.csv",
        "data/tourism_embeddings.npy",
        "data/tourism_metadata.pkl"
    ]
    return all(os.path.exists(f) for f in required_files)

# (Saved Trips helpers removed)

def inject_banner_style(page_class, banner_name, fallback_gradient="linear-gradient(135deg, #0d9488 0%, #1e1b4b 100%)"):
    """Injects a CSS style tag defining the background for a page-specific hero section class using static serving."""
    import shutil
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src_path = os.path.join(base_dir, "assets", "banners", banner_name)
    
    # Set up static directory for Streamlit static serving
    static_dir = os.path.join(base_dir, "static", "banners")
    os.makedirs(static_dir, exist_ok=True)
    
    dest_path = os.path.join(static_dir, banner_name)
    has_image = False
    
    if os.path.exists(src_path):
        try:
            # Only copy if destination doesn't exist or has different size
            if not os.path.exists(dest_path) or os.path.getsize(src_path) != os.path.getsize(dest_path):
                shutil.copy2(src_path, dest_path)
            has_image = True
        except Exception:
            pass

    if has_image:
        static_url = f"/app/static/banners/{banner_name}"
        bg_style = f"""
        background-image: linear-gradient(180deg, rgba(15, 23, 42, 0.45) 0%, rgba(15, 23, 42, 0.85) 100%), url('{static_url}') !important;
        background-repeat: no-repeat !important;
        background-position: center !important;
        background-size: cover !important;
        """
    else:
        bg_style = f"background: {fallback_gradient} !important;"
    
    style_html = f"""
    <style>
        .{page_class} {{
            {bg_style}
        }}
    </style>
    """
    st.html(style_html)


