import streamlit as st

st.set_page_config(page_title="RetailPulse AI", layout="wide")

st.title("⚡ RetailPulse AI Platform")

# Manual dropdown switcher that guarantees page switching works
page = st.selectbox(
    "Select Dashboard View",
    [
        "Home",
        "Executive Dashboard",
        "Sales Analytics",
        "Product Analytics",
        "Customer Analysis",
        "Country Insights",
        "Time Analysis",
        "Profit Analysis",
        "Inventory Risk",
        "Business Insights",
        "Advanced Analytics",
        "KPI Summary",
        "Thank You"
    ]
)

if page == "Home":
    st.switch_page("pages/1_Home.py")
elif page == "Executive Dashboard":
    st.switch_page("pages/2_Executive_Dashboard.py")
elif page == "Sales Analytics":
    st.switch_page("pages/3_Sales_Analytics.py")
# ...and so on for your pages