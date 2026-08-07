import os
import streamlit as st
from styles import load_css

# ==========================================================
# PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="RetailPulse AI Platform",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
load_css("light")

# HIDE 'app' NAVIGATION ITEM FROM SIDEBAR
st.markdown("""
<style>
/* Hide the top 'app' link in Streamlit sidebar */
[data-testid="stSidebarNav"] ul li:first-child {
    display: none !important;
}

.badge-tag-secondary {
    display: inline-block;
    background: linear-gradient(135deg, #1e3a8a, #2563eb);
    color: #ffffff;
    padding: 6px 18px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.tech-pill {
    display: inline-block;
    background-color: #1e293b;
    color: #38bdf8;
    padding: 6px 14px;
    border-radius: 8px;
    font-size: 12px;
    font-weight: 700;
    margin-right: 8px;
    margin-top: 8px;
}

/* Styled Action Buttons */
div.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #1e3a8a, #2563eb);
    color: #ffffff !important;
    font-weight: 700 !important;
    border-radius: 10px;
    border: none;
    padding: 10px 16px;
    transition: all 0.3s ease;
    box-shadow: 0 4px 10px rgba(37, 99, 235, 0.2);
}

div.stButton > button:hover {
    background: linear-gradient(135deg, #2563eb, #1d4ed8);
    color: #ffffff !important;
    box-shadow: 0 6px 16px rgba(37, 99, 235, 0.4);
    transform: translateY(-1px);
}
</style>
""", unsafe_allow_html=True)

# ==========================================================
# SAFE NAVIGATION HELPER FUNCTION
# ==========================================================

def navigate_to_module(possible_filenames):
    """
    Dynamically finds the exact file name in pages/ directory
    and switches to it safely without throwing PageNotFoundError.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    pages_dir = current_dir if os.path.basename(current_dir) == "pages" else os.path.join(current_dir, "pages")
    
    # Try finding exact filename match on disk
    if os.path.exists(pages_dir):
        files = os.listdir(pages_dir)
        for target in possible_filenames:
            for file in files:
                if file.lower() == target.lower():
                    st.switch_page(f"pages/{file}")
                    return
    
    # Fallback default
    st.switch_page(f"pages/{possible_filenames[0]}")

# ==========================================================
# HIGH-TECH HERO SECTION
# ==========================================================

st.markdown("""
<div>
    <span class="badge-tag-secondary">⚡ Enterprise Data Science Solution</span>
</div>
""", unsafe_allow_html=True)

st.title("Retail Pulse AI-Powered Customer Analytics & Demand Forecasting Platform")
st.subheader("Predictive Demand, Customer Segmentation, Churn Analysis & Inventory Optimization")

st.caption("🚀 End-to-End Data Science and Analytics Solution for Retail Demand and Prediction Customer Insights")

st.markdown("""
An advanced, multi-dimensional decision intelligence platform engineered for enterprise retail analytics. Leverages machine learning, statistical forecasting, and cohort dynamics to optimize revenue, customer retention, inventory replenishment, and cross-border expansion.
""")

st.markdown("""
<div>
    <span class="tech-pill">📊 Power BI</span>
    <span class="tech-pill">🐍 Python / Pandas</span>
    <span class="tech-pill">🗄️ SQL Querying</span>
    <span class="tech-pill">📈 Machine Learning</span>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ==========================================================
# BASELINE PORTFOLIO HIGHLIGHTS
# ==========================================================

st.markdown("### 📌 Baseline Performance Highlights")

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.metric("Total Sales Revenue", "$10.27M", "Sum of Gross Revenue")

with m2:
    st.metric("Orders Fulfilled", "21K+", "Total Transactions")

with m3:
    st.metric("Active Customers", "4.3K+", "Unique Client Accounts")

with m4:
    st.metric("Global Reach", "40 Markets", "International Footprint")

st.markdown("---")

# ==========================================================
# ANALYTICS MODULE DIRECTORY (ALL 15 MODULES)
# ==========================================================

st.markdown("### 🧭 Analytics Module Directory")
st.markdown("Select a functional module below to navigate directly:")

# ROW 1
r1_c1, r1_c2, r1_c3, r1_c4 = st.columns(4)

with r1_c1:
    with st.container(border=True):
        st.markdown("**📊 Executive Dashboard**")
        st.caption("C-Suite KPIs, performance banners, YoY revenue trends, and growth indicators.")
        if st.button("Launch Hub ➔", key="btn_exec"):
            navigate_to_module(["2_Executive_Dashboard.py", "2_executive_dashboard.py"])

with r1_c2:
    with st.container(border=True):
        st.markdown("**💰 Sales Analytics**")
        st.caption("Revenue trends, monthly growth %, seasonal patterns, and order size distributions.")
        if st.button("Launch Hub ➔", key="btn_sales"):
            navigate_to_module(["3_Sales_Analytics.py", "3_sales_analytics.py"])

with r1_c3:
    with st.container(border=True):
        st.markdown("**📦 Product Analytics**")
        st.caption("Pareto 80/20 analysis, product contribution charts, and price vs volume matrix.")
        if st.button("Launch Hub ➔", key="btn_product"):
            navigate_to_module(["4_Product_Analytics.py", "4_product_analytics.py"])

with r1_c4:
    with st.container(border=True):
        st.markdown("**👥 Customer Analysis**")
        st.caption("Customer Lifetime Value (CLV), RFM segmentation, and retention dynamics.")
        if st.button("Launch Hub ➔", key="btn_cust"):
            navigate_to_module(["5_customer_analysis.py", "5_Customer_Analysis.py"])

st.markdown("<br>", unsafe_allow_html=True)

# ROW 2
r2_c1, r2_c2, r2_c3, r2_c4 = st.columns(4)

with r2_c1:
    with st.container(border=True):
        st.markdown("**🌍 Country Insights**")
        st.caption("Geographic choropleth maps, global revenue contribution, and efficiency.")
        if st.button("Launch Hub ➔", key="btn_country"):
            navigate_to_module(["6_Country_Insights.py", "6_country_insights.py"])

with r2_c2:
    with st.container(border=True):
        st.markdown("**⏰ Time Analysis**")
        st.caption("Hour of day x day of week heatmaps, intra-day traffic peaks, and resampled trendlines.")
        if st.button("Launch Hub ➔", key="btn_time"):
            navigate_to_module(["7_Time_Analysis.py", "7_time_analysis.py"])

with r2_c3:
    with st.container(border=True):
        st.markdown("**💹 Profit Analysis**")
        st.caption("Gross profit margin waterfalls, COGS ratio simulation, and top margin drivers.")
        if st.button("Launch Hub ➔", key="btn_profit"):
            navigate_to_module(["8_Profit_Analysis.py", "8_profit_analysis.py"])

with r2_c4:
    with st.container(border=True):
        st.markdown("**⚠️ Inventory Risk**")
        st.caption("Stockout risk tables, Days of Inventory Remaining (DIR), and capital allocation.")
        if st.button("Launch Hub ➔", key="btn_inv"):
            navigate_to_module(["9_Inventory_Risk.py", "9_inventory_risk.py"])

st.markdown("<br>", unsafe_allow_html=True)

# ROW 3
r3_c1, r3_c2, r3_c3, r3_c4 = st.columns(4)

with r3_c1:
    with st.container(border=True):
        st.markdown("**💡 Business Insights**")
        st.caption("Strategic summaries, cross-selling potential, and performance anomalies.")
        if st.button("Launch Hub ➔", key="btn_bi"):
            navigate_to_module(["10_Business_Insights.py", "10_business_insights.py"])

with r3_c2:
    with st.container(border=True):
        st.markdown("**🔬 Advanced Analytics**")
        st.caption("Advanced statistical models, correlation matrices, and predictive drivers.")
        if st.button("Launch Hub ➔", key="btn_adv"):
            navigate_to_module(["11_Advanced_Analytics.py", "11_advanced_analytics.py"])

with r3_c3:
    with st.container(border=True):
        st.markdown("**📋 KPI Summary**")
        st.caption("Aggregated metric summaries, variance performance, and ledger reviews.")
        if st.button("Launch Hub ➔", key="btn_kpi"):
            navigate_to_module(["12_KPI_Summary.py", "12_kpi_summary.py"])

with r3_c4:
    with st.container(border=True):
        st.markdown("**⚠️ Churn Risk**")
        st.caption("Customer churn likelihood metrics, segmentation, and high-risk accounts.")
        if st.button("Launch Hub ➔", key="btn_churn"):
            navigate_to_module(["13_Customer_Churn_Risk.py", "13_customer_churn_risk.py"])

st.markdown("<br>", unsafe_allow_html=True)

# ROW 4
r4_c1, r4_c2, r4_c3 = st.columns(3)

with r4_c1:
    with st.container(border=True):
        st.markdown("**📈 Demand Explorer**")
        st.caption("Historical product demand tracking, units sold trends, and volume metrics.")
        if st.button("Launch Hub ➔", key="btn_demand"):
            navigate_to_module(["14_Demand_Explorer.py", "14_demand_explorer.py"])

with r4_c2:
    with st.container(border=True):
        st.markdown("**✨ Thank You**")
        st.caption("Project acknowledgments, contact info, and closing platform overview.")
        if st.button("Launch Hub ➔", key="btn_thx"):
            navigate_to_module(["15_Thank_You.py", "15_thank_you.py"])

with r4_c3:
    with st.container(border=True):
        st.markdown("**🏠 Home Dashboard**")
        st.caption("Return to the main overview control center.")
        if st.button("Launch Hub ➔", key="btn_home"):
            navigate_to_module(["1_Home.py", "1_home.py"])

st.markdown("---")

# ==========================================================
# KEY STRATEGIC FINDINGS
# ==========================================================

st.markdown("### 🧠 Key Strategic Findings")

col_ins1, col_ins2 = st.columns(2)

with col_ins1:
    st.info("""
    **💡 Market & Geographic Dominance**
    * **United Kingdom Primary Engine:** The UK generates over **85.8%** of total commercial revenue ($8.81M).
    * **European Growth Hubs:** Secondary markets led by EIRE ($380.9K), Netherlands ($268.8K), Germany ($202.0K), and France ($147.1K).
    * **Global Footprint:** Active transactions across **40 unique international markets**.
    """)

with col_ins2:
    st.success("""
    **📈 Commercial & Temporal Trends**
    * **Q4 Seasonal Peak:** Sales surge dramatically in November ($1.46M monthly peak) due to holiday demand.
    * **Product Concentration:** Revenue is highly concentrated in top revenue drivers such as *Manual*, *Regency Cakestand 3 Tier*, and *White Hanging Heart T-Light Holder*.
    * **Average Transaction Value:** Steady Average Order Value (AOV) benchmarked at **$490.28** per transaction.
    """)

# ==========================================================
# FOOTER
# ==========================================================

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #94a3b8; font-size: 14px; padding: 20px 0;">
    RetailPulse AI • Enterprise Analytics Platform<br>
    Developed by Gulafsha • © 2026
</div>
""", unsafe_allow_html=True)