import streamlit as st
from utils.helper import (
    init_session_state, inject_styles, get_local_food_recommendations,
    get_packing_checklist, get_emergency_info, inject_banner_style
)

# Initialize state and inject custom CSS
init_session_state()
inject_styles()

# Safety check
if not st.session_state["plan_generated"]:
    st.warning("⚠️ No active trip plan has been generated yet. Please go to the Home page to specify your interests and generate a plan.")
    if st.button("✈️ Go to Home Page", type="primary"):
        st.switch_page("pages/1_Home.py")
    st.stop()

# Retrieve state values
top_destinations = st.session_state["recommended_destinations"]
primary_city = top_destinations.iloc[0]["City"]
primary_state = top_destinations.iloc[0]["State"]
best_time = top_destinations.iloc[0].get("Best_Time", "October to March")
categories = top_destinations["Category"].tolist()

# Premium Travel Hero Banner
inject_banner_style("hero-tips", "tips_banner.jpg")
st.markdown(
    """
    <div class="hero-section hero-tips">
        <div class="hero-overlay">
            <h1 class="hero-title">Travel Tips & Guidance</h1>
            <p class="hero-subtitle">Essential tips, regional packing lists, culinary recommendations, and cultural safety guidelines for your destination</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.write(f"### 💡 Custom Guidance for *{primary_city}, {primary_state}*")
st.markdown("<p style='color: #94a3b8; margin-top:-10px;'>Browse specific sections below to prepare for your journey.</p>", unsafe_allow_html=True)

# Redesigned Layout using Tabs
tab_food, tab_pack, tab_time, tab_etiquette, tab_emergency = st.tabs([
    "🍛 Local Food", "🎒 Packing Checklist", "📅 Best Time to Visit", "🕌 Cultural Etiquette", "🚨 Emergency Contacts"
])

# =====================================================================
# TAB 1: LOCAL FOOD
# =====================================================================
with tab_food:
    st.write("#### 🍛 Regional Culinary Specialties")
    st.write("We highly recommend trying these traditional local delicacies during your stay:")
    
    foods = get_local_food_recommendations(primary_state)
    
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        food_list_html = "<ul>" + "".join([f"<li style='color:#f8fafc; font-size:1.05rem; margin-bottom:8px;'>🍛 <b>{f}</b></li>" for f in foods[:2]]) + "</ul>"
        st.markdown(food_list_html, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_r:
        if len(foods) > 2:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            food_list_html = "<ul>" + "".join([f"<li style='color:#f8fafc; font-size:1.05rem; margin-bottom:8px;'>🍛 <b>{f}</b></li>" for f in foods[2:]]) + "</ul>"
            st.markdown(food_list_html, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

# =====================================================================
# TAB 2: PACKING CHECKLIST
# =====================================================================
with tab_pack:
    st.write("#### 🎒 Suggested Packing Checklist")
    st.write("Check items off as you pack them based on destination styles:")
    
    checklist = get_packing_checklist(categories)
    
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    for index, item in enumerate(checklist):
        st.checkbox(item, key=f"tips_pack_{index}_{item.replace(' ', '_')}")
    st.markdown("</div>", unsafe_allow_html=True)

# =====================================================================
# TAB 3: BEST TIME TO VISIT
# =====================================================================
with tab_time:
    st.write("#### 📅 Seasonal Overview")
    st.write("Planning around regional weather shifts ensures optimal outdoor sightseeing:")
    
    st.markdown(
        f"""
        <div class='glass-card' style='border-left: 5px solid #2dd4bf; background: rgba(45, 212, 191, 0.04);'>
            <h4 style='color:#2dd4bf; margin:0;'>✨ Best Season: {best_time}</h4>
            <p style='color:#cbd5e1; margin-top:8px; line-height:1.5; font-size:1rem;'>
                Traveling to <b>{primary_city}</b> during the <b>{best_time}</b> offers the most pleasant conditions, 
                minimizing extreme rainfall or excessive summer heat. Perfect for exploring monuments, 
                gardens, and market lanes.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

# =====================================================================
# TAB 4: CULTURAL ETIQUETTE
# =====================================================================
with tab_etiquette:
    st.write("#### 🕌 Local Customs & Etiquette")
    st.write("Observe these respect guidelines to ensure positive interactions with communities:")
    
    st.markdown(
        """
        <div class='glass-card'>
            <ul style='color:#cbd5e1; font-size:1rem; line-height:1.6; padding-left:20px;'>
                <li style='margin-bottom:8px;'><b>Dress Modestly:</b> Cover shoulders and knees when visiting temples, mosques, and historical shrines.</li>
                <li style='margin-bottom:8px;'><b>Footwear:</b> Remove footwear before entering homes and religious buildings. Look for designated shoe racks.</li>
                <li style='margin-bottom:8px;'><b>Photography:</b> Always seek permission before photographing local inhabitants or inside active religious monuments.</li>
                <li style='margin-bottom:8px;'><b>Greeting:</b> A traditional 'Namaste' (folding hands) is widely appreciated as a respectful gesture.</li>
                <li style='margin-bottom:8px;'><b>Dining:</b> Eat traditional meals using your right hand, as it is considered clean and customary.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

# =====================================================================
# TAB 5: EMERGENCY CONTACTS
# =====================================================================
with tab_emergency:
    st.write("#### 🚨 Emergency Response Details")
    st.write("Keep these essential contacts saved in your mobile device:")
    
    emergency_contacts = get_emergency_info()
    
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    for label, num in emergency_contacts.items():
        st.markdown(
            f"""
            <div style='display:flex; justify-content:space-between; padding:10px 0; border-bottom:1px solid rgba(255,255,255,0.05);'>
                <span style='color:#cbd5e1;'>☎️ {label}</span>
                <strong style='color:#2dd4bf; font-family:monospace; font-size:1.05rem;'>{num}</strong>
            </div>
            """,
            unsafe_allow_html=True
        )
    st.markdown("</div>", unsafe_allow_html=True)
