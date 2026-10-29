import streamlit as st
from utils.helper import init_session_state, inject_styles

# Set page configuration - must be the first Streamlit command
st.set_page_config(
    page_title="SmartTrip AI - Intelligent Tourism Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables and inject custom styles
init_session_state()
inject_styles()

# Sidebar branding
st.sidebar.markdown(
    """
    <div style='text-align: center; margin-bottom: 20px;'>
        <h2 style='color: #2dd4bf; font-weight: 800; margin-bottom: 0;'>SmartTrip AI</h2>
        <span style='color: #64748b; font-size: 0.85rem;'>Intelligent Tourism Planner</span>
    </div>
    """,
    unsafe_allow_html=True
)

# Define the five distinct navigation pages
home_page = st.Page("pages/1_Home.py", title="Home", icon="🏠", default=True)
explore_page = st.Page("pages/2_Explore_Trip.py", title="Explore Trip", icon="🧭")
hotels_page = st.Page("pages/3_Hotels.py", title="Hotels", icon="🏨")
tips_page = st.Page("pages/4_Travel_Tips.py", title="Travel Tips", icon="💡")
# Render page navigation menu
pg = st.navigation([home_page, explore_page, hotels_page, tips_page])

# Run the selected page
pg.run()
