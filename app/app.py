import streamlit as st

st.set_page_config(page_title="RetailPulse AI", layout="wide")

st.title("⚡ RetailPulse AI Platform")
st.markdown("### Select a Dashboard to Open:")

# Use buttons instead of automatic switch_page to prevent API load errors
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🏠 Home"):
        st.switch_page("pages/1_Home.py")
    if st.button("📊 Executive Dashboard"):
        st.switch_page("pages/2_Executive_Dashboard.py")
    if st.button("💰 Sales Analytics"):
        st.switch_page("pages/3_Sales_Analytics.py")
    if st.button("📦 Product Analytics"):
        st.switch_page("pages/4_Product_Analytics.py")

with col2:
    if st.button("👥 Customer Analysis"):
        st.switch_page("pages/5_customer_analysis.py")
    if st.button("🌍 Country Insights"):
        st.switch_page("pages/6_Country_Insights.py")
    if st.button("⏳ Time Analysis"):
        st.switch_page("pages/7_Time_Analysis.py")
    if st.button("📈 Profit Analysis"):
        st.switch_page("pages/8_Profit_Analysis.py")

with col3:
    if st.button("⚠️ Inventory Risk"):
        st.switch_page("pages/9_Inventory_Risk.py")
    if st.button("💡 Business Insights"):
        st.switch_page("pages/10_Business_Insights.py")
    if st.button("🔬 Advanced Analytics"):
        st.switch_page("pages/11_Advanced_Analytics.py")
    if st.button("📋 KPI Summary"):
        st.switch_page("pages/12_KPI_Summary.py")

if st.button("✨ Thank You"):
    st.switch_page("pages/13_Thank_You.py")