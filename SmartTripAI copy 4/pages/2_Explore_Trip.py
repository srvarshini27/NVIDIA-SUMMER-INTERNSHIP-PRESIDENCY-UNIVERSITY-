import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px
import plotly.graph_objects as go
import hashlib
import numpy as np
import math
from utils.helper import (
    init_session_state, inject_styles, load_nearby_attractions, load_hotel_data, 
    get_google_images_link, get_local_food_recommendations, 
    get_packing_checklist, get_emergency_info, inject_banner_style
)

# Initialize state and inject custom CSS
init_session_state()
inject_styles()

# Safety check
if not st.session_state["plan_generated"]:
    st.warning("⚠️ Please generate a trip plan from the Home page first.")
    if st.button("✈️ Go to Home Page", type="primary"):
        st.switch_page("pages/1_Home.py")
    st.stop()

# Retrieve state values
top_destinations = st.session_state["recommended_destinations"]
itinerary = st.session_state["itinerary"]
selected_hotel = st.session_state["selected_hotel"]
interests = st.session_state["interests"]
travel_style = st.session_state["travel_style"]
number_of_people = st.session_state.get("number_of_people", 1)
days = st.session_state["days"]
city = st.session_state["city"]
hotel_df = load_hotel_data()
attractions_df = load_nearby_attractions()

selected_places = top_destinations["Place"].tolist()
primary_city = top_destinations.iloc[0]["City"]
primary_state = top_destinations.iloc[0]["State"]

# Premium Travel Hero Banner
inject_banner_style("hero-explore", "explore_banner.jpg")
st.markdown(
    """
    <div class="hero-section hero-explore">
        <div class="hero-overlay">
            <h1 class="hero-title">Explore Your Journey</h1>
            <p class="hero-subtitle">Review recommendations, customize your lodging, inspect maps, and review financial estimations</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Quick Parameter Summary Bar
st.markdown(
    f"""
    <div class='glass-card' style='padding: 16px 24px; margin-bottom: 20px; display: flex; flex-wrap: wrap; gap: 30px;'>
        <div><span style='color: #94a3b8; font-size: 0.85rem;'>QUERY INTERESTS</span><br><strong style='color: #2dd4bf;'>"{interests}"</strong></div>
        <div><span style='color: #94a3b8; font-size: 0.85rem;'>STYLE</span><br><strong style='color: #f8fafc;'>{travel_style}</strong></div>
        <div><span style='color: #94a3b8; font-size: 0.85rem;'>TRAVELERS</span><br><strong style='color: #f8fafc;'>{number_of_people} Person(s)</strong></div>
        <div><span style='color: #94a3b8; font-size: 0.85rem;'>DAYS</span><br><strong style='color: #f8fafc;'>{days} Days</strong></div>
        <div><span style='color: #94a3b8; font-size: 0.85rem;'>TARGET DESTINATION</span><br><strong style='color: #f8fafc;'>{city if city != "All Cities" else primary_city}</strong></div>
    </div>
    """,
    unsafe_allow_html=True
)

# Tabs navigation
tab_overview, tab_itinerary, tab_nearby, tab_budget = st.tabs([
    "📊 Overview & Inspector", "📅 Itinerary Planner", "🔍 Nearby Attractions", "💳 Budget Summary"
])

# =====================================================================
# TAB 1: OVERVIEW & INSPECTOR
# =====================================================================
with tab_overview:
    st.write("### 🎯 Recommended Destinations")
    st.markdown("<p style='color: #94a3b8; margin-top:-10px;'>Our neural network mapped these locations based on your interest keywords. Hover for an immersive preview.</p>", unsafe_allow_html=True)
    
    # Grid of destination cards
    cols_grid = st.columns(3)
    for index, (_, row) in enumerate(top_destinations.iterrows()):
        col_cell = cols_grid[index % 3]
        score = row["Tourist_Match_Score"]
        score_color = "#10b981" if score >= 85 else ("#14b8a6" if score >= 70 else "#f59e0b")
        g_link = get_google_images_link(row['Place'], row['City'])
        desc = row.get("Description", "Discover this amazing tourism location, offering scenery, historical highlights, and local specialities.")
        
        card_html = f"""
        <div class='premium-card'>
            <div class='card-content'>
                <div>
                    <div style='display: flex; justify-content: space-between; align-items: start; margin-bottom: 4px;'>
                        <strong style='font-size: 1.15rem; color: #f8fafc; font-weight: 700; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 70%;'>{row['Place']}</strong>
                        <span style='color: {score_color}; font-weight: 800; font-size: 1.05rem;'>{score:.1f}% Match</span>
                    </div>
                    <div style='color: #94a3b8; font-size: 0.85rem; margin-bottom: 8px;'>📍 {row['City']}, {row['State']}</div>
                    <div style='margin-bottom: 8px;'>
                        <span class='custom-tag'>{row['Category']}</span>
                        <span class='custom-tag-sec'>⭐ {row['Rating']}</span>
                    </div>
                    <p class='card-description'>{desc}</p>
                </div>
                <div class='card-hover-button-wrapper'>
                    <a href='{g_link}' target='_blank' class='view-photos-btn'>🖼️ View Photos</a>
                </div>
            </div>
        </div>
        """
        
        with col_cell:
            st.markdown(card_html, unsafe_allow_html=True)
                        
    st.markdown("<div class='gradient-divider'></div>", unsafe_allow_html=True)
    
    # Dynamic click inspector panel
    st.write("### 🔍 Interactive Destination Details Inspector")
    st.markdown("<p style='color: #94a3b8; margin-top:-10px;'>Select a destination below to deep-dive into details, entry fees, and map coordinates.</p>", unsafe_allow_html=True)
    
    inspect_choice = st.selectbox(
        "🔍 Choose place to inspect",
        selected_places,
        label_visibility="collapsed"
    )
    
    inspect_row = top_destinations[top_destinations["Place"] == inspect_choice].iloc[0]
    col_det_left, col_det_right = st.columns([1.1, 1.3])
    
    with col_det_left:
        inspect_g_link = get_google_images_link(inspect_choice, inspect_row["City"])
        
        st.markdown(
            f"""
            <div class='premium-card' style='height: 180px; margin-bottom: 20px;'>
                <div class='card-content'>
                    <div>
                        <h4 style='color: #fff; margin: 0; font-weight: 700;'>{inspect_choice}</h4>
                        <p style='color: #94a3b8; font-size: 0.9rem; margin-top: 4px;'>📍 {inspect_row['City']}, {inspect_row['State']}</p>
                        <p style='color: #cbd5e1; font-size: 0.9rem; margin-top: 8px;'>Category: <b>{inspect_row['Category']}</b> | Rating: <b>⭐ {inspect_row['Rating']}</b></p>
                    </div>
                    <div class='card-hover-button-wrapper'>
                        <a href='{inspect_g_link}' target='_blank' class='view-photos-btn'>🖼️ View Photos</a>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Details grid
        st.markdown(
            f"""
            <div class='glass-card' style='padding: 16px 20px; background: rgba(30,41,59,0.3);'>
                <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 12px;'>
                    <div><span style='color:#94a3b8; font-size:0.8rem;'>⭐ RATING</span><br><strong style='color:#f8fafc;'>{inspect_row['Rating']} / 5.0</strong></div>
                    <div><span style='color:#94a3b8; font-size:0.8rem;'>🎟️ ENTRANCE FEE</span><br><strong style='color:#f8fafc;'>₹{inspect_row['Entrance_Fee']}</strong></div>
                    <div><span style='color:#94a3b8; font-size:0.8rem;'>⏱️ VISIT HOURS</span><br><strong style='color:#f8fafc;'>{inspect_row['Average_Visit_Hours']} hours</strong></div>
                    <div><span style='color:#94a3b8; font-size:0.8rem;'>👥 TOURIST TYPE</span><br><strong style='color:#f8fafc;'>{inspect_row['Tourist_Type']}</strong></div>
                    <div><span style='color:#94a3b8; font-size:0.8rem;'>📅 BEST SEASON</span><br><strong style='color:#f8fafc;'>{inspect_row['Best_Time']}</strong></div>
                    <div><span style='color:#94a3b8; font-size:0.8rem;'>🚖 TRAVEL FARE</span><br><strong style='color:#f8fafc;'>₹{inspect_row['Price_Fare']}</strong></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.link_button("🖼️ View Photos - Google Search", inspect_g_link, use_container_width=True)
        
    with col_det_right:
        st.markdown(f"<h2>{inspect_choice}</h2>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div style='margin-bottom: 12px;'>
                <span class='custom-tag'>{inspect_row['Category']}</span>
                <span class='custom-tag-sec'>📍 {inspect_row['City']}, {inspect_row['State']}</span>
                <span class='custom-tag' style='background: rgba(16,185,129,0.12); color:#34d399; border-color:rgba(16,185,129,0.25);'>Match: {inspect_row['Tourist_Match_Score']:.1f}%</span>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.write("#### 📝 Description")
        st.write(inspect_row["Description"])
        
        # Local attractions query
        inspect_attrs = attractions_df[attractions_df["Nearby_Place"] == inspect_choice].sort_values(by="Rating", ascending=False).head(3)
        st.write("#### 🍴 Nearby Attractions")
        for _, attr in inspect_attrs.iterrows():
            st.markdown(
                f"""
                <div style='display:flex; justify-content:space-between; font-size:0.9rem; padding: 8px 12px; background:rgba(255,255,255,0.03); border-radius:8px; margin-bottom:6px;'>
                    <span>🗺️ {attr['Attraction_Name']} ({attr['Category']})</span>
                    <strong style='color:#2dd4bf;'>⭐ {attr['Rating']} | {attr['Distance_KM']} KM</strong>
                </div>
                """,
                unsafe_allow_html=True
            )
            
        # Add single map indicator
        st.write("#### 🗺️ Map Position")
        p_lat = inspect_row["Latitude"]
        p_lon = inspect_row["Longitude"]
        layer_s = pdk.Layer(
            "ScatterplotLayer",
            pd.DataFrame([{"lat": p_lat, "lon": p_lon, "name": inspect_choice}]),
            get_position=["lon", "lat"],
            get_color=[20, 184, 166, 220],
            get_radius=100,
            radius_scale=2,
            pickable=True
        )
        st.pydeck_chart(pdk.Deck(
            layers=[layer_s],
            initial_view_state=pdk.ViewState(latitude=p_lat, longitude=p_lon, zoom=12.5, pitch=0),
            tooltip={"html": "<b>{name}</b>"}
        ))

# =====================================================================
# TAB 2: REDESIGNED DAY-WISE ITINERARY
# =====================================================================
with tab_itinerary:
    st.write("### 📅 Spaced Day-Wise Itinerary")
    st.markdown("<p style='color: #94a3b8; margin-top:-10px;'>Your scheduled daily plan, restricted to 2 attractions per day to avoid congestion.</p>", unsafe_allow_html=True)
    
    for day_num, day_info in itinerary.items():
        with st.expander(f"🌅 Day {day_num} Overview", expanded=(day_num == 1)):
            place_am = day_info["AM_Place"]
            place_pm = day_info["PM_Place"]
            
            # Breakfast
            st.markdown(
                f"""
                <div class='timeline-card' style='border-left-color: #64748b; border-left-style: dashed;'>
                    <div style='display:flex; align-items:center;'>
                        <div class='timeline-time-col' style='color:#94a3b8;'>09:00 AM</div>
                        <div>
                            <strong style='font-size:1.1rem; color:#e2e8f0;'>Breakfast / Departure</strong>
                            <p style='color:#64748b; font-size:0.85rem; margin-top:2px;'>Fuel up at your hotel or local cafe near {place_am['Place']}.</p>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # AM Attraction Info and Button
            am_link = get_google_images_link(place_am['Place'], place_am.get('City', ''))
            st.markdown(
                f"""
                <div class='timeline-card'>
                    <div style='display:flex; justify-content:space-between; align-items:center; width:100%;'>
                        <div style='display:flex; align-items:start;'>
                            <div class='timeline-time-col'>10:00 AM</div>
                            <div style='flex-grow:1;'>
                                <strong style='font-size:1.15rem; color:#f8fafc;'>Visit: {place_am['Place']}</strong>
                                <p style='color:#94a3b8; font-size:0.85rem; margin:2px 0;'>🎟️ Fee: ₹{place_am['Entrance_Fee']} | ⭐ {place_am['Rating']} | {place_am['Category']}</p>
                                <p style='color:#cbd5e1; font-size:0.9rem; margin-top:6px; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden;'>{place_am.get('Description', '')}</p>
                            </div>
                        </div>
                        <div class='card-hover-button-wrapper-timeline' style='margin-left: 20px;'>
                            <a href='{am_link}' target='_blank' class='view-photos-btn' style='width: auto !important; padding: 6px 14px !important; white-space: nowrap;'>🖼️ View Photos</a>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
                
            # Lunch
            st.markdown(
                f"""
                <div class='timeline-card' style='border-left-color: #64748b; border-left-style: dashed;'>
                    <div style='display:flex; align-items:center;'>
                        <div class='timeline-time-col' style='color:#94a3b8;'>01:00 PM</div>
                        <div>
                            <strong style='font-size:1.1rem; color:#e2e8f0;'>Lunch Break: {day_info['Lunch_Spot']}</strong>
                            <p style='color:#64748b; font-size:0.85rem; margin-top:2px;'>Sample regional specialties highly rated by travelers.</p>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # PM Attraction Info and Button
            pm_link = get_google_images_link(place_pm['Place'], place_pm.get('City', ''))
            st.markdown(
                f"""
                <div class='timeline-card'>
                    <div style='display:flex; justify-content:space-between; align-items:center; width:100%;'>
                        <div style='display:flex; align-items:start;'>
                            <div class='timeline-time-col'>03:00 PM</div>
                            <div style='flex-grow:1;'>
                                <strong style='font-size:1.15rem; color:#f8fafc;'>Visit: {place_pm['Place']}</strong>
                                <p style='color:#94a3b8; font-size:0.85rem; margin:2px 0;'>🎟️ Fee: ₹{place_pm['Entrance_Fee']} | ⭐ {place_pm['Rating']} | {place_pm['Category']}</p>
                                <p style='color:#cbd5e1; font-size:0.9rem; margin-top:6px; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden;'>{place_pm.get('Description', '')}</p>
                            </div>
                        </div>
                        <div class='card-hover-button-wrapper-timeline' style='margin-left: 20px;'>
                            <a href='{pm_link}' target='_blank' class='view-photos-btn' style='width: auto !important; padding: 6px 14px !important; white-space: nowrap;'>🖼️ View Photos</a>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
                
            # Evening activity
            st.markdown(
                f"""
                <div class='timeline-card' style='border-left-color: #64748b; border-left-style: dashed;'>
                    <div style='display:flex; align-items:center;'>
                        <div class='timeline-time-col' style='color:#94a3b8;'>06:00 PM</div>
                        <div>
                            <strong style='font-size:1.1rem; color:#e2e8f0;'>Evening Activity: {day_info['Evening_Spot']}</strong>
                            <p style='color:#64748b; font-size:0.85rem; margin-top:2px;'>Relax, shop at the local market, and enjoy a traditional dinner.</p>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

# =====================================================================
# TAB 3: NEARBY ATTRACTIONS
# =====================================================================
with tab_nearby:
    st.write("### 🔍 Surrounds Explorer")
    st.markdown("<p style='color: #94a3b8; margin-top:-10px;'>Map local cafes, viewpoints, and markets near your stops. Replaced table lists with modern interactive cards.</p>", unsafe_allow_html=True)
    
    inspect_spot = st.selectbox(
        "📍 Choose destination to map surrounding spots",
        selected_places,
        key="nearby_select"
    )
    
    spot_info = top_destinations[top_destinations["Place"] == inspect_spot].iloc[0]
    local_spots = attractions_df[attractions_df["Nearby_Place"] == inspect_spot]
    
    if len(local_spots) == 0:
        st.info("No surrounding spots matched in the radius index.")
    else:
        col_spots_list, col_spots_map = st.columns([1.1, 1])
        
        with col_spots_list:
            cats = local_spots["Category"].unique()
            for cat in sorted(cats):
                cat_df = local_spots[local_spots["Category"] == cat].sort_values(by="Rating", ascending=False)
                st.write(f"#### {cat}")
                
                # Card-based layout for nearby attractions
                for idx, row in cat_df.iterrows():
                    g_link = get_google_images_link(row['Attraction_Name'], inspect_spot)
                    
                    card_html = f"""
                    <div class='premium-card' style='height: 220px; margin-bottom: 20px;'>
                        <div class='card-content'>
                            <div>
                                <strong style='font-size: 1.15rem; color: #f8fafc; font-weight: 700;'>{row['Attraction_Name']}</strong>
                                <div style='color: #94a3b8; font-size: 0.85rem; margin: 4px 0;'>📍 Near {row['Nearby_Place']}</div>
                                <div style='margin: 8px 0;'>
                                    <span class='custom-tag'>{row['Category']}</span>
                                    <span class='custom-tag-sec'>⭐ {row['Rating']}</span>
                                </div>
                                <div style='color: #cbd5e1; font-size: 0.85rem;'>🏃 Distance: {row['Distance_KM']} KM</div>
                            </div>
                            <div class='card-hover-button-wrapper'>
                                <a href='{g_link}' target='_blank' class='view-photos-btn'>🖼️ View Photos</a>
                            </div>
                        </div>
                    </div>
                    """
                    st.markdown(card_html, unsafe_allow_html=True)
                    st.link_button("🖼️ View Photos", g_link, use_container_width=True)
                    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
                    
        with col_spots_map:
            # Radial GPS offsets
            map_rows = [{"Name": inspect_spot, "lat": spot_info["Latitude"], "lon": spot_info["Longitude"], "Category": "Primary Spot", "Rating": spot_info["Rating"], "r": 45, "g": 212, "b": 191, "size": 150}]
            
            COLORS_LOOKUP = {
                "Food & Dining": [239, 68, 68], "Shopping": [236, 72, 153], "Local Market": [245, 158, 11],
                "Activity": [168, 85, 247], "Viewpoint": [34, 197, 94], "Transit": [100, 116, 139]
            }
            
            for idx, row in local_spots.iterrows():
                h_val = int(hashlib.md5(row["Attraction_Name"].encode('utf-8')).hexdigest(), 16)
                angle = (h_val % 360) * (np.pi / 180.0)
                lat_off = (row["Distance_KM"] / 111.0) * np.cos(angle)
                lon_off = (row["Distance_KM"] / (111.0 * np.cos(spot_info["Latitude"] * np.pi / 180.0))) * np.sin(angle)
                
                rgb = COLORS_LOOKUP.get(row["Category"], [45, 212, 191])
                map_rows.append({
                    "Name": row["Attraction_Name"],
                    "lat": spot_info["Latitude"] + lat_off,
                    "lon": spot_info["Longitude"] + lon_off,
                    "Category": row["Category"],
                    "Rating": row["Rating"],
                    "r": rgb[0], "g": rgb[1], "b": rgb[2],
                    "size": 80
                })
                
            map_df = pd.DataFrame(map_rows)
            layer = pdk.Layer(
                "ScatterplotLayer", map_df,
                get_position=["lon", "lat"],
                get_color=["r", "g", "b", 220],
                get_radius="size",
                radius_scale=1.5,
                pickable=True
            )
            st.pydeck_chart(pdk.Deck(
                layers=[layer],
                initial_view_state=pdk.ViewState(latitude=spot_info["Latitude"], longitude=spot_info["Longitude"], zoom=14.0, pitch=0),
                tooltip={"html": "<b>{Name}</b><br/>Category: {Category}<br/>Rating: ⭐ {Rating}"}
            ))

# =====================================================================
# TAB 4: BUDGET SUMMARY
# =====================================================================
with tab_budget:
    st.write("### 💳 Financial Breakdown Summary")
    st.markdown("<p style='color: #94a3b8; margin-top:-10px;'>Estimated budget projections categorized by lodging, transportation, entrance fees, and emergency buffers.</p>", unsafe_allow_html=True)
    
    breakdown = st.session_state["budget_breakdown"]
    h_cost = breakdown["Hotel_Cost"]
    t_cost = breakdown["Travel_Cost"]
    e_fees = breakdown["Entry_Fees"]
    f_cost = breakdown["Food_Cost"]
    m_cost = breakdown["Misc_Cost"]
    t_est = breakdown["Total_Estimated"]
    w_bud = breakdown["Within_Budget"]
    budget_limit = st.session_state["budget"]
    
    variance = budget_limit - t_est
    abs_variance = abs(variance)
    
    # Financial indicators
    if w_bud:
        st.markdown(
            f"""
            <div class='glass-card' style='background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(45, 212, 191, 0.15) 100%); border-color: rgba(16, 185, 129, 0.3);'>
                <h3 style='color: #34d399; margin-top: 0; display: flex; align-items: center;'>🎉 Within Budget Limit</h3>
                <p style='color: #cbd5e1; margin-bottom: 0;'>
                    Fantastic! Your estimated trip cost is <b>₹{t_est:,.2f}</b>, which is <b>₹{abs_variance:,.2f}</b> under your target ceiling of ₹{budget_limit:,.2f}.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"""
            <div class='glass-card' style='background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(249, 115, 22, 0.15) 100%); border-color: rgba(239, 68, 68, 0.3);'>
                <h3 style='color: #f87171; margin-top: 0;'>⚠️ Over Budget Limit</h3>
                <p style='color: #cbd5e1; margin-bottom: 0;'>
                    Your estimated trip cost of <b>₹{t_est:,.2f}</b> exceeds your target ceiling of ₹{budget_limit:,.2f} by <b>₹{abs_variance:,.2f}</b>. Consider switching hotels or styles.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_f_m1, col_f_m2, col_f_m3, col_f_m4 = st.columns(4)
    with col_f_m1:
        st.markdown(f"<div class='glass-card' style='text-align:center;'><div class='metric-label'>Total Budget Limit</div><div class='metric-value'>₹{budget_limit:,.2f}</div></div>", unsafe_allow_html=True)
    with col_f_m2:
        st.markdown(f"<div class='glass-card' style='text-align:center;'><div class='metric-label'>Number of People</div><div class='metric-value'>{number_of_people}</div></div>", unsafe_allow_html=True)
    with col_f_m3:
        st.markdown(f"<div class='glass-card' style='text-align:center;'><div class='metric-label'>Cost Per Person</div><div class='metric-value'>₹{(t_est / number_of_people):,.2f}</div></div>", unsafe_allow_html=True)
    with col_f_m4:
        st.markdown(f"<div class='glass-card' style='text-align:center;'><div class='metric-label'>Total Estimated Cost</div><div class='metric-value' style='color:{'#2dd4bf' if w_bud else '#ef4444'};'>₹{t_est:,.2f}</div></div>", unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_chart_left, col_chart_right = st.columns(2)
    with col_chart_left:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.write("#### 🍰 Cost Allocation Pie Chart")
        cost_df = pd.DataFrame({
            "Category": ["Lodging (Hotel)", "Transportation", "Attraction Fees", "Food & Meals", "Emergency Buffer (15%)"],
            "Cost": [h_cost, t_cost, e_fees, f_cost, m_cost]
        })
        fig_p = px.pie(cost_df, values='Cost', names='Category', color_discrete_sequence=['#2dd4bf', '#06b6d4', '#3b82f6', '#8b5cf6', '#64748b'], template='plotly_dark')
        fig_p.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=10,r=10,t=10,b=10), legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5))
        st.plotly_chart(fig_p, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_chart_right:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.write("#### 🧭 Budget Utilization Gauge")
        max_r = max(budget_limit, t_est) * 1.25
        fig_g = go.Figure(go.Indicator(
            mode="gauge+number", value=t_est, domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [None, max_r], 'tickwidth': 1, 'tickcolor': "#f8fafc"},
                'bar': {'color': '#2dd4bf'}, 'bgcolor': 'rgba(0,0,0,0)', 'borderwidth': 2, 'bordercolor': '#475569',
                'steps': [
                    {'range': [0, budget_limit * 0.8], 'color': 'rgba(16, 185, 129, 0.15)'},
                    {'range': [budget_limit * 0.8, budget_limit], 'color': 'rgba(245, 158, 11, 0.15)'},
                    {'range': [budget_limit, max_r], 'color': 'rgba(239, 68, 68, 0.15)'}
                ],
                'threshold': {'line': {'color': "#ef4444", 'width': 4}, 'thickness': 0.75, 'value': budget_limit}
            }
        ))
        fig_g.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color': "#f8fafc", 'family': "sans-serif"}, margin=dict(l=10,r=10,t=10,b=10))
        st.plotly_chart(fig_g, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    # Save Trip Summary Button
    st.markdown("<div class='glass-card' style='text-align: center; border-color: rgba(45, 212, 191, 0.4); background: rgba(45, 212, 191, 0.04);'>", unsafe_allow_html=True)
    st.write("#### 💾 Export Trip Plan Summary")
    st.write("Export your fully generated itinerary, budget allocations, hotel bookings, and checklists into a text file.")
    
    summary_lines = [
        "==============================================",
        "          SMARTTRIP AI - TRIP PLAN SUMMARY    ",
        "==============================================",
        f"Travel Interests: {interests}",
        f"Target City: {primary_city}, {primary_state}",
        f"Duration: {days} Days",
        f"Travel Style: {travel_style}",
        f"Number of People: {number_of_people}",
        f"Total Budget Limit: INR {budget_limit:,.2f}",
        f"Total Estimated Cost: INR {t_est:,.2f}",
        f"Status: {'WITHIN BUDGET' if w_bud else 'OVER BUDGET'}",
        "----------------------------------------------",
        "🛎️ LODGING INFORMATION",
        f"Selected Hotel: {selected_hotel['Hotel_Name'] if selected_hotel else 'None'}",
        f"Rooms Allocated: {breakdown.get('Rooms', 1)} room(s)",
        f"Price Per Night: INR {selected_hotel['Hotel_Price'] if selected_hotel else 0:,.2f}",
        f"Total Hotel Cost: INR {h_cost:,.2f}",
        "----------------------------------------------",
        "📅 DAY-WISE ITINERARY"
    ]
    for d_num, d_info in itinerary.items():
        summary_lines.extend([
            f"\nDay {d_num}:",
            f"  09:00 AM - Breakfast / Departure",
            f"  10:00 AM - Visit: {d_info['AM_Place']['Place']} ({d_info['AM_Place']['Category']})",
            f"             Description: {d_info['AM_Place'].get('Description', '')}",
            f"             Entrance Fee: INR {d_info['AM_Place']['Entrance_Fee']}",
            f"  01:00 PM - Lunch Break at {d_info['Lunch_Spot']}",
            f"  03:00 PM - Visit: {d_info['PM_Place']['Place']} ({d_info['PM_Place']['Category']})",
            f"             Description: {d_info['PM_Place'].get('Description', '')}",
            f"             Entrance Fee: INR {d_info['PM_Place']['Entrance_Fee']}",
            f"  06:00 PM - Evening Activity: {d_info['Evening_Spot']}"
        ])
        
    summary_lines.extend([
        "\n----------------------------------------------",
        "💡 TRAVEL TIPS & PACKING CHECKLIST",
        f"Best Time to Visit: {top_destinations.iloc[0]['Best_Time']}",
        f"Local Food Specialties: {', '.join(get_local_food_recommendations(primary_state))}",
        "Packing Checklist:",
    ])
    for item in get_packing_checklist(top_destinations["Category"].tolist()):
        summary_lines.append(f"  [ ] {item}")
        
    summary_lines.extend([
        "----------------------------------------------",
        "🚨 EMERGENCY CONTACT INFO",
        "  - National Emergency Number: 112",
        "  - Police Helpline: 100",
        "  - Ambulance / Medical: 102 / 108",
        "  - Tourist Helpline: 1363",
        "=============================================="
    ])
    trip_summary_text = "\n".join(summary_lines)
    
    st.download_button(
        "💾 Save Trip Summary",
        data=trip_summary_text,
        file_name=f"SmartTrip_{primary_city}_Itinerary.txt",
        mime="text/plain",
        use_container_width=True
    )
    st.markdown("</div>", unsafe_allow_html=True)
