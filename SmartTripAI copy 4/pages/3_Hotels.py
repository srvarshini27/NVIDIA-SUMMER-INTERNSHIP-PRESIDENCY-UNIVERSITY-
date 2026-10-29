import streamlit as st
import pandas as pd
import hashlib
import math
from utils.helper import init_session_state, inject_styles, load_hotel_data, get_google_images_link, inject_banner_style

# Initialize state and inject custom CSS
init_session_state()
inject_styles()

# Safety check
if not st.session_state["plan_generated"]:
    st.warning("⚠️ No trip plan has been generated yet. Please go to the Home page to specify your interests and generate a plan.")
    if st.button("✈️ Go to Home Page", type="primary"):
        st.switch_page("pages/1_Home.py")
    st.stop()

# Retrieve state values
hotel_df = load_hotel_data()
top_destinations = st.session_state["recommended_destinations"]
primary_city = top_destinations.iloc[0]["City"]
selected_hotel = st.session_state["selected_hotel"]
days = st.session_state["days"]
travel_style = st.session_state["travel_style"]
number_of_people = st.session_state.get("number_of_people", 1)

# Helper to update active hotel and recalculate budget
def select_new_hotel(hotel_record):
    st.session_state["selected_hotel"] = hotel_record
    days_count = st.session_state["days"]
    breakdown = st.session_state["budget_breakdown"]
    total_budget_limit = st.session_state["budget"]
    
    if travel_style in ["Solo", "Couple"]:
        rooms = 1
    else:
        rooms = math.ceil(number_of_people / 2)
        
    new_hotel_cost_total = hotel_record["Hotel_Price"] * rooms * days_count
    
    subtotal = new_hotel_cost_total + breakdown["Travel_Cost"] + breakdown["Entry_Fees"] + breakdown["Food_Cost"]
    new_misc_total = subtotal * 0.15
    new_total_estimated = subtotal + new_misc_total
    
    st.session_state["budget_breakdown"] = {
        "Hotel_Cost": new_hotel_cost_total,
        "Rooms": rooms,
        "Number_Of_People": number_of_people,
        "Travel_Cost": breakdown["Travel_Cost"],
        "Entry_Fees": breakdown["Entry_Fees"],
        "Food_Cost": breakdown["Food_Cost"],
        "Misc_Cost": new_misc_total,
        "Total_Estimated": new_total_estimated,
        "Within_Budget": new_total_estimated <= total_budget_limit
    }
    st.toast(f"✅ Active Hotel updated to: {hotel_record['Hotel_Name']}!", icon="🏨")

# Premium Travel Hero Banner
inject_banner_style("hero-hotels", "hotels_banner.jpg")
st.markdown(
    """
    <div class="hero-section hero-hotels">
        <div class="hero-overlay">
            <h1 class="hero-title">Hotel Accommodations</h1>
            <p class="hero-subtitle">Discover comfortable stays and select rooms that fit your travel parameters</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Currently Selected Hotel Card
st.write("### 🛎️ Selected Hotel Reservation")
if selected_hotel:
    breakdown = st.session_state["budget_breakdown"]
    rooms = breakdown.get("Rooms", 1)
    total_stay_price = breakdown["Hotel_Cost"]
    
    st.markdown(
        f"""
        <div class='glass-card' style='border-left: 5px solid #2dd4bf; background: rgba(45, 212, 191, 0.05);'>
            <div style='display: flex; justify-content: space-between; align-items: start; flex-wrap: wrap;'>
                <div>
                    <h3 style='margin: 0; color: #f8fafc;'>{selected_hotel['Hotel_Name']}</h3>
                    <p style='color: #94a3b8; margin: 4px 0;'>📍 City: {selected_hotel['City']} | 🏃 {selected_hotel['Distance_From_Attraction']} KM from city center landmarks</p>
                </div>
                <div style='text-align: right;'>
                    <strong style='font-size: 1.5rem; color: #2dd4bf;'>₹{selected_hotel['Hotel_Price']:,}</strong> <span style='color: #94a3b8; font-size: 0.85rem;'>/ night / room</span><br>
                    <span style='color: #94a3b8; font-size: 0.85rem;'>Total for {rooms} room(s), {days} night(s): ₹{total_stay_price:,}</span>
                </div>
            </div>
            <div style='margin-top: 8px;'>
                <span class='custom-tag-sec'>⭐ {selected_hotel['Hotel_Rating']} Rating</span>
                <span style='color: #64748b; font-size: 0.85rem;'>💬 Based on {selected_hotel['Review_Count']} reviews</span>
            </div>
            <div style='color: #cbd5e1; margin-top: 10px; font-size: 0.95rem; line-height: 1.5;'>{selected_hotel['Description']}</div>
            <div style='margin-top: 12px;'>
                {" ".join([f"<span class='custom-tag'>{amenity.strip()}</span>" for amenity in selected_hotel['Amenities'].split(',')])}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.info("No hotel selected. Please select one from the options below.")

st.markdown("<div class='gradient-divider'></div>", unsafe_allow_html=True)

# Recommended Hotels in City section with Filter panel
st.write(f"### 🔍 Discover Lodging in *{primary_city}*")

# Filter Sidebar or Panel
st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
    max_price = st.slider(
        "💵 Max Price Per Night (INR)",
        min_value=500,
        max_value=20000,
        value=8000,
        step=500
    )
with col_f2:
    min_rating = st.selectbox(
        "⭐ Minimum Hotel Rating",
        [3.0, 3.5, 4.0, 4.5],
        index=1
    )
with col_f3:
    search_query = st.text_input(
        "🔍 Search Amenities or Names",
        placeholder="e.g., WiFi, Pool, Spa"
    )
st.markdown("</div>", unsafe_allow_html=True)

# Query & Filter dataset
filtered_hotels = hotel_df[
    (hotel_df["City"] == primary_city) &
    (hotel_df["Hotel_Price"] <= max_price) &
    (hotel_df["Hotel_Rating"] >= min_rating)
]

# Apply textual search query if entered
if search_query.strip():
    q = search_query.lower()
    filtered_hotels = filtered_hotels[
        filtered_hotels["Hotel_Name"].str.lower().str.contains(q) |
        filtered_hotels["Amenities"].str.lower().str.contains(q)
    ]

# Sort matching hotels
filtered_hotels = filtered_hotels.sort_values(by="Hotel_Rating", ascending=False).head(9)

if len(filtered_hotels) == 0:
    st.warning("⚠️ No hotels matched your specific filters. Try adjusting price limits or rating criteria.")
else:
    st.write(f"Showing top {len(filtered_hotels)} matching hotels:")
    
    # 3-Column Grid for Hotel Cards
    cols_grid = st.columns(3)
    for index, (_, row) in enumerate(filtered_hotels.iterrows()):
        col_cell = cols_grid[index % 3]
        is_selected = selected_hotel and row["Hotel_Name"] == selected_hotel["Hotel_Name"]
        card_border = "border-color: rgba(45, 212, 191, 0.65); background: rgba(45, 212, 191, 0.03);" if is_selected else ""
        g_link = get_google_images_link(row["Hotel_Name"], row["City"])
        
        card_html = f"""
        <div class='premium-card' style='{card_border}'>
            <div class='card-content'>
                <div>
                    <div style='display: flex; justify-content: space-between; align-items: start; margin-bottom: 4px;'>
                        <strong style='font-size: 1.15rem; color: #f8fafc; font-weight: 700; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 65%;'>{row['Hotel_Name']}</strong>
                        <span style='color: #2dd4bf; font-weight: 800; font-size: 1.1rem;'>₹{row['Hotel_Price']:,} <span style='font-size:0.75rem; font-weight:400; color:#94a3b8;'>/ nt</span></span>
                    </div>
                    <div style='color: #94a3b8; font-size: 0.85rem; margin-bottom: 8px;'>📍 {row['City']} | {row['Distance_From_Attraction']} KM</div>
                    <div style='margin-bottom: 8px;'>
                        <span class='custom-tag-sec'>⭐ {row['Hotel_Rating']}</span>
                        <span style='color: #64748b; font-size: 0.8rem;'>💬 {row['Review_Count']} reviews</span>
                    </div>
                    <p class='card-description'>{row['Description']}</p>
                </div>
                <div class='card-hover-button-wrapper'>
                    <a href='{g_link}' target='_blank' class='view-photos-btn'>🖼️ View Photos</a>
                </div>
            </div>
        </div>
        """
        
        with col_cell:
            st.markdown(card_html, unsafe_allow_html=True)
            if is_selected:
                st.button("🟢 Active", key=f"active_hotel_{index}", disabled=True, use_container_width=True)
            else:
                if st.button("🛎️ Choose", key=f"choose_hotel_btn_{index}", use_container_width=True):
                    select_new_hotel(row.to_dict())
                    st.rerun()
