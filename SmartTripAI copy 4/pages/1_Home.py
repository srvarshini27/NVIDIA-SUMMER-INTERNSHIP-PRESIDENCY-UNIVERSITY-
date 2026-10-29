import streamlit as st
import pandas as pd
import numpy as np
import math
from sklearn.metrics.pairwise import cosine_similarity
from utils.helper import (
    init_session_state, inject_styles, check_data_files,
    load_tourism_data, load_hotel_data, load_nearby_attractions,
    load_embeddings_and_metadata, load_embedding_model,
    get_google_images_link, inject_banner_style
)

# Safety check
if not check_data_files():
    st.warning("⏳ SmartTrip AI is initializing datasets and downloading neural models. This may take up to 2-3 minutes on the first startup. Please refresh in a moment...")
    st.info("System status: Generating synthetic datasets (2,000+ places, 3,000+ hotels, 5,000+ attractions) and precomputing SentenceTransformer embeddings...")
    st.stop()

# Data is ready, load it
try:
    tourism_df = load_tourism_data()
    hotel_df = load_hotel_data()
    attractions_df = load_nearby_attractions()
    embeddings, metadata_df = load_embeddings_and_metadata()
except Exception as e:
    st.error(f"Error loading datasets: {e}")
    st.stop()

# Premium Travel Hero Banner
inject_banner_style("hero-home", "home_banner.jpg")
st.markdown(
    """
    <div class="hero-section hero-home">
        <div class="hero-overlay">
            <h1 class="hero-title">Plan Your Perfect Journey</h1>
            <p class="hero-subtitle">Intelligent AI recommendations, custom itineraries, and budget metrics tailored for your dream adventure</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Welcome Banner Hero (Glassmorphism)
st.markdown(
    """
    <div class='glass-card' style='background: linear-gradient(135deg, rgba(45, 212, 191, 0.15) 0%, rgba(6, 182, 212, 0.15) 100%); border-color: rgba(45, 212, 191, 0.25);'>
        <h3 style='color: #2dd4bf; margin-top: 0; font-weight: 700;'>Discover Travel in the Era of AI</h3>
        <p style='color: #cbd5e1; font-size: 1.05rem; line-height: 1.6; margin-bottom: 0;'>
            SmartTrip AI maps your unique interests semantically using <b>SentenceTransformers</b> 
            across <b>2,025+ destinations</b>. It automatically queries <b>3,150+ lodging properties</b> 
            and schedules localized dining and markets from our <b>6,075+ nearby attractions</b> catalog, 
            preparing optimized itineraries and budgets in seconds.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# Curated diverse popular destinations (Option B)
popular_destinations = [
    {
        "Place": "Taj Mahal",
        "City": "Agra",
        "State": "Uttar Pradesh",
        "Category": "Historical",
        "Rating": 4.9,
        "Description": "An iconic white marble mausoleum on the south bank of the Yamuna River. A UNESCO World Heritage site and one of the New Seven Wonders of the World."
    },
    {
        "Place": "Golden Temple",
        "City": "Amritsar",
        "State": "Punjab",
        "Category": "Religious",
        "Rating": 4.9,
        "Description": "Also known as Sri Harmandir Sahib, it is the preeminent spiritual shrine of Sikhism, famous for its golden exterior and serene tank."
    },
    {
        "Place": "Kerala Backwaters",
        "City": "Alappuzha",
        "State": "Kerala",
        "Category": "Nature",
        "Rating": 4.8,
        "Description": "A serene network of lagoons, lakes, and canals fringed by palm trees, famous for traditional houseboat journeys."
    }
]

st.write("### 📸 Discover Popular Indian Destinations")
col_img1, col_img2, col_img3 = st.columns(3)
cols = [col_img1, col_img2, col_img3]

for col, sample in zip(cols, popular_destinations):
    g_link = get_google_images_link(sample['Place'], sample['City'])
    
    with col:
        st.markdown(
            f"""
            <div class='premium-card'>
                <div class='card-content'>
                    <div>
                        <h4 style='color: #fff; margin: 0 0 6px 0; font-weight: 700; font-size: 1.35rem;'>{sample['Place']}</h4>
                        <p style='color: #94a3b8; font-size: 0.85rem; margin: 4px 0;'>📍 {sample['City']}, {sample['State']}</p>
                        <div style='margin: 8px 0;'>
                            <span class='custom-tag'>{sample['Category']}</span>
                            <span class='custom-tag-sec'>⭐ {sample['Rating']}</span>
                        </div>
                        <p class='card-description'>{sample['Description']}</p>
                    </div>
                    <div class='card-hover-button-wrapper'>
                        <a href='{g_link}' target='_blank' class='view-photos-btn'>🖼️ View Photos</a>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

st.markdown("<div class='gradient-divider'></div>", unsafe_allow_html=True)

# Trip planning form specifications
st.write("### ⚙️ Build Your Personalized Journey")
st.markdown("<p style='color: #94a3b8; margin-top:-10px;'>Provide your preferences to initialize the Semantic Recommendation Engine.</p>", unsafe_allow_html=True)

st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

col_left, col_right = st.columns(2)

with col_left:
    interest_input = st.text_input(
        "🧠 Travel Interests & Activities",
        value=st.session_state.get("interests", ""),
        placeholder="e.g., peaceful beaches, historical forts, sunset views, spice shopping",
        help="Type anything! The system uses semantic search embeddings to match your interest."
    )
    
    cities_list = ["All Cities"] + sorted(list(tourism_df["City"].unique()))
    city_choice = st.selectbox(
        "📍 Destination City",
        cities_list,
        index=cities_list.index(st.session_state.get("city", "All Cities")),
        help="Choose a specific city, or select 'All Cities' to discover destinations nationally."
    )
    
    days_choice = st.slider(
        "📅 Duration (Days)",
        min_value=1,
        max_value=7,
        value=st.session_state["days"],
        step=1
    )

with col_right:
    travel_style = st.selectbox(
        "👥 Travel Style",
        ["Solo", "Couple", "Group"],
        index=["Solo", "Couple", "Group"].index(st.session_state.get("travel_style", "Solo")),
        help="Travel styles influence budget calculations and destination matching scores."
    )
    
    if travel_style == "Solo":
        number_of_people = 1
    elif travel_style == "Couple":
        number_of_people = 2
    else:
        number_of_people = st.number_input(
            "👥 Number of People",
            min_value=3,
            max_value=100,
            value=max(3, int(st.session_state.get("number_of_people", 3))),
            step=1,
            help="Specify the total number of travelers."
        )
        
    budget_input = st.number_input(
        "💳 Total Trip Budget (INR)",
        min_value=5000.0,
        max_value=1000000.0,
        value=st.session_state["budget"],
        step=5000.0,
        help="Your budget will be compared against hotel prices, entry fees, transport, and meal costs."
    )

st.markdown("</div>", unsafe_allow_html=True)

col_btn1, col_btn2, col_btn3 = st.columns([1.5, 1, 1.5])
with col_btn2:
    generate_btn = st.button("🚀 Generate Trip Plan", use_container_width=True, type="primary")

if generate_btn:
    if not interest_input.strip():
        st.error("⚠️ Please specify your travel interest to proceed.")
        st.stop()
        
    with st.spinner("🧠 Scanning neural vector database... mapping travel interests..."):
        model = load_embedding_model()
        query_emb = model.encode([interest_input])
        df_match = tourism_df.copy()
        
        if city_choice != "All Cities":
            df_match = df_match[df_match["City"] == city_choice]
            
        if len(df_match) == 0:
            st.markdown(
                f"""
                <div class='glass-card' style='border-left: 5px solid #ef4444; background: rgba(239, 68, 68, 0.05);'>
                    <h4 style='color: #f87171; margin-top:0;'>🔍 Empty State: No Destinations Found</h4>
                    <p style='color: #cbd5e1; margin-bottom:0;'>We couldn't find any destinations matching the city <b>{city_choice}</b> in our index. Please select 'All Cities' or adjust your parameters.</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.stop()
            
        filtered_indices = df_match.index.tolist()
        filtered_embs = embeddings[filtered_indices]
        
        sims = cosine_similarity(query_emb, filtered_embs)[0]
        df_match["Semantic_Similarity"] = sims
        df_match["Similarity_Score"] = np.clip((df_match["Semantic_Similarity"] - 0.1) / 0.7, 0.0, 1.0) * 100.0
        
        daily_budget = budget_input / days_choice
        attraction_allowance = daily_budget * 0.15
        
        budget_fits = []
        for idx, row in df_match.iterrows():
            total_cost = row["Entrance_Fee"] + row["Price_Fare"]
            if total_cost <= attraction_allowance:
                fit = 100.0
            else:
                fit = max(0.0, 1.0 - (total_cost - attraction_allowance) / attraction_allowance) * 100.0
            budget_fits.append(fit)
        df_match["Budget_Fit"] = budget_fits
        
        df_match["Rating_Score"] = np.clip((df_match["Rating"] - 3.5) / 1.4, 0.0, 1.0) * 100.0
        df_match["Popularity_Score_Scaled"] = np.clip((df_match["Popularity_Score"] - 50.0) / 50.0, 0.0, 1.0) * 100.0
        
        df_match["Tourist_Match_Score"] = (
            0.40 * df_match["Similarity_Score"] +
            0.20 * df_match["Budget_Fit"] +
            0.20 * df_match["Rating_Score"] +
            0.20 * df_match["Popularity_Score_Scaled"]
        )
        
        df_match = df_match.sort_values(by="Tourist_Match_Score", ascending=False)
        required_places = 2 * days_choice
        top_destinations = df_match.head(required_places)
        
        if len(top_destinations) < required_places:
            additional_needed = required_places - len(top_destinations)
            extra_df = tourism_df[~tourism_df["Place"].isin(top_destinations["Place"])]
            if city_choice != "All Cities":
                extra_df = extra_df[extra_df["State"] == df_match.iloc[0]["State"]]
            extra_df = extra_df.head(additional_needed)
            top_destinations = pd.concat([top_destinations, extra_df])
            
        itinerary = {}
        for d in range(days_choice):
            day_num = d + 1
            place_am = top_destinations.iloc[2 * d]
            place_pm = top_destinations.iloc[2 * d + 1]
            
            nearby_food = attractions_df[
                (attractions_df["Nearby_Place"] == place_am["Place"]) & 
                (attractions_df["Category"] == "Food & Dining")
            ].sort_values(by="Rating", ascending=False)
            
            food_spot = nearby_food.iloc[0]["Attraction_Name"] if len(nearby_food) > 0 else "Local Culinary Delights Cafe"
            
            nearby_shopping = attractions_df[
                (attractions_df["Nearby_Place"] == place_pm["Place"]) & 
                (attractions_df["Category"].isin(["Shopping", "Local Market", "Viewpoint"]))
            ].sort_values(by="Rating", ascending=False)
            
            shopping_spot = nearby_shopping.iloc[0]["Attraction_Name"] if len(nearby_shopping) > 0 else "Traditional Craft Bazaar"
            
            itinerary[day_num] = {
                "AM_Place": place_am.to_dict(),
                "Lunch_Spot": food_spot,
                "PM_Place": place_pm.to_dict(),
                "Evening_Spot": shopping_spot
            }
            
        primary_city = top_destinations.iloc[0]["City"]
        city_hotels = hotel_df[hotel_df["City"] == primary_city]
        
        max_hotel_price = daily_budget * 0.45
        recommended_hotels = city_hotels[city_hotels["Hotel_Price"] <= max_hotel_price]
        
        if len(recommended_hotels) == 0:
            recommended_hotels = city_hotels.sort_values(by="Hotel_Price").head(5)
        else:
            recommended_hotels = recommended_hotels.sort_values(by=["Hotel_Rating", "Distance_From_Attraction"], ascending=[False, True]).head(5)
            
        default_hotel = recommended_hotels.iloc[0].to_dict() if len(recommended_hotels) > 0 else None
        hotel_cost_daily = default_hotel["Hotel_Price"] if default_hotel else 1500.0
        
        if travel_style in ["Solo", "Couple"]:
            rooms = 1
        else:
            rooms = math.ceil(number_of_people / 2)
            
        hotel_cost_total = hotel_cost_daily * rooms * days_choice
        travel_cost_daily = 300.0 * number_of_people
        travel_cost_total = travel_cost_daily * days_choice
        entry_fees_total = top_destinations["Entrance_Fee"].sum() * number_of_people
        food_cost_daily = 400.0 * number_of_people
        food_cost_total = food_cost_daily * days_choice
        
        subtotal = hotel_cost_total + travel_cost_total + entry_fees_total + food_cost_total
        misc_cost_total = subtotal * 0.15
        total_estimated = subtotal + misc_cost_total
        
        budget_breakdown = {
            "Hotel_Cost": hotel_cost_total,
            "Rooms": rooms,
            "Number_Of_People": number_of_people,
            "Travel_Cost": travel_cost_total,
            "Entry_Fees": entry_fees_total,
            "Food_Cost": food_cost_total,
            "Misc_Cost": misc_cost_total,
            "Total_Estimated": total_estimated,
            "Within_Budget": total_estimated <= budget_input
        }
        
        st.session_state["interests"] = interest_input
        st.session_state["travel_style"] = travel_style
        st.session_state["number_of_people"] = number_of_people
        st.session_state["budget"] = budget_input
        st.session_state["days"] = days_choice
        st.session_state["city"] = city_choice
        st.session_state["recommended_destinations"] = top_destinations
        st.session_state["itinerary"] = itinerary
        st.session_state["selected_hotel"] = default_hotel
        st.session_state["hotel_recommendations"] = recommended_hotels
        st.session_state["budget_breakdown"] = budget_breakdown
        st.session_state["plan_generated"] = True
        
        st.success("🎉 Trip plan generated successfully!")
        st.switch_page("pages/2_Explore_Trip.py")

# (System Architecture Statistics removed)


