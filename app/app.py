import streamlit as st
import os

st.set_page_config(
    page_title="RetailPulse AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Verify if data path exists so metrics don't display blank fields
data_path = "data/retail_data.csv" # Update this to match your actual dataset filename if different
data_exists = os.path.exists(data_path)

if not data_exists:
    st.sidebar.warning("⚠️ Data file path needs verification. Check 'data/' folder.")

# Define all 13 pages explicitly for the sidebar router
pages = [
    st.Page("pages/1_Home.py", title="Home", default=True),
    st.Page("pages/2_Executive_Dashboard.py", title="Executive Dashboard"),
    st.Page("pages/3_Sales_Analytics.py", title="Sales Analytics"),
    st.Page("pages/4_Product_Analytics.py", title="Product Analytics"),
    st.Page("pages/5_customer_analysis.py", title="Customer Analysis"),
    st.Page("pages/6_Country_Insights.py", title="Country Insights"),
    st.Page("pages/7_Time_Analysis.py", title="Time Analysis"),
    st.Page("pages/8_Profit_Analysis.py", title="Profit Analysis"),
    st.Page("pages/9_Inventory_Risk.py", title="Inventory Risk"),
    st.Page("pages/10_Business_Insights.py", title="Business Insights"),
    st.Page("pages/11_Advanced_Analytics.py", title="Advanced Analytics"),
    st.Page("pages/12_KPI_Summary.py", title="KPI Summary"),
    st.Page("pages/13_Thank_You.py", title="Thank You"),
]

pg = st.navigation(pages, position="sidebar")
pg.run()