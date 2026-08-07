import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from styles import load_css
from utils import load_data

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Advanced Predictive Analytics",
    page_icon="⚡",
    layout="wide"
)

load_css("light")
if st.button("⬅️ Back to Home"):
    st.switch_page("pages/1_Home.py")
    

# ==========================================================
# LOAD DATA
# ==========================================================

df = load_data()

# ==========================================================
# PAGE TITLE
# ==========================================================

st.markdown("""
<div class="dashboard-title">⚡ RetailPulse AI</div>
<div class="dashboard-subtitle">Advanced Machine Learning, Cohort Dynamics & Predictive Customer Analytics</div>
""", unsafe_allow_html=True)

st.header("⚡ Advanced Analytics")

# ==========================================================
# DATA PREPARATION & COLUMN STANDARDIZATION
# ==========================================================

# Clean whitespace from all column names
df.columns = df.columns.str.strip()

# Comprehensive column mapping
column_mapping = {
    "Invoice Date": "InvoiceDate",
    "invoice_date": "InvoiceDate",
    "Invoice_Date": "InvoiceDate",
    "Total Price": "TotalPrice",
    "total_price": "TotalPrice",
    "Total_Price": "TotalPrice",
    "Sales": "TotalPrice",
    "sales": "TotalPrice",
    "Unit Price": "UnitPrice",
    "unit_price": "UnitPrice",
    "Price": "UnitPrice",
    "Quantity": "Quantity",
    "quantity": "Quantity",
    "Description": "Description",
    "description": "Description",
    "Country": "Country",
    "country": "Country",
    "Customer ID": "CustomerID",
    "customer_id": "CustomerID",
    "CustomerID": "CustomerID",
    "Invoice": "InvoiceNo",
    "InvoiceNo": "InvoiceNo",
    "invoice_no": "InvoiceNo"
}
df = df.rename(columns=column_mapping)

# Remove duplicate column names
df = df.loc[:, ~df.columns.duplicated(keep='first')].copy()

if "InvoiceDate" not in df.columns:
    st.error("❌ Dataset missing 'InvoiceDate' column.")
    st.stop()

df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

if "Quantity" not in df.columns:
    df["Quantity"] = 1

if "UnitPrice" not in df.columns and "TotalPrice" in df.columns:
    df["UnitPrice"] = df["TotalPrice"] / df["Quantity"].replace(0, 1)
elif "UnitPrice" not in df.columns:
    df["UnitPrice"] = 0.0

if "TotalPrice" not in df.columns:
    df["TotalPrice"] = df["Quantity"] * df["UnitPrice"]

if "InvoiceNo" not in df.columns:
    df["InvoiceNo"] = df.index

if "CustomerID" not in df.columns:
    df["CustomerID"] = df.index.astype(str)

# Clean out null or unassigned Customer IDs
valid_df = df[df["CustomerID"].notna() & (df["CustomerID"].astype(str).str.strip() != "Guest")].copy()

if valid_df.empty:
    valid_df = df.copy()
    valid_df["CustomerID"] = "Cust_" + valid_df.index.astype(str)

# ==========================================================
# 🎛️ CONTROLS & SLICERS
# ==========================================================

st.markdown("### 🎛️ Advanced Analytics Controls")

c1, c2, c3 = st.columns(3)

with c1:
    countries = sorted(valid_df["Country"].dropna().unique()) if "Country" in valid_df.columns else []
    selected_country = st.multiselect("🌍 Geographic Segment", countries)

with c2:
    churn_threshold_days = st.slider("⌛ Churn Inactivity Threshold (Days)", min_value=30, max_value=180, value=90, step=5)

with c3:
    analysis_focus = st.selectbox("🎯 Modeling Focus Area", ["All Metrics", "RFM Segmentation", "Price Elasticity", "Churn Risk"])

# ==========================================================
# APPLY SLICERS
# ==========================================================

filtered_df = valid_df.copy()

if selected_country and "Country" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["Country"].isin(selected_country)]

filtered_df = filtered_df.loc[:, ~filtered_df.columns.duplicated(keep='first')].copy()

# ==========================================================
# RFM & PREDICTIVE ANALYTICS CALCULATIONS
# ==========================================================

snapshot_date = filtered_df["InvoiceDate"].max() + pd.Timedelta(days=1)

rfm_df = (
    filtered_df.groupby("CustomerID")
    .agg(
        RecencyDays=("InvoiceDate", lambda x: (snapshot_date - x.max()).days),
        Frequency=("InvoiceNo", "nunique"),
        MonetaryValue=("TotalPrice", "sum"),
        AvgBasketSize=("Quantity", "mean")
    )
    .reset_index()
)

# Quantile Scoring for RFM
try:
    rfm_df["R_Score"] = pd.qcut(rfm_df["RecencyDays"].rank(method="first"), 4, labels=[4, 3, 2, 1])
    rfm_df["F_Score"] = pd.qcut(rfm_df["Frequency"].rank(method="first"), 4, labels=[1, 2, 3, 4])
    rfm_df["M_Score"] = pd.qcut(rfm_df["MonetaryValue"].rank(method="first"), 4, labels=[1, 2, 3, 4])
except Exception:
    rfm_df["R_Score"] = 2
    rfm_df["F_Score"] = 2
    rfm_df["M_Score"] = 2

rfm_df["RFM_Composite"] = rfm_df["R_Score"].astype(int) + rfm_df["F_Score"].astype(int) + rfm_df["M_Score"].astype(int)

# Segment Classification
def segment_customer(row):
    r = int(row["R_Score"])
    f = int(row["F_Score"])
    m = int(row["M_Score"])
    
    if r >= 3 and f >= 3 and m >= 3:
        return "Champions"
    elif r >= 3 and f >= 2:
        return "Loyal Customers"
    elif r <= 2 and f >= 3:
        return "At Risk"
    elif r == 1:
        return "Churned / Dormant"
    else:
        return "Recent Advocates"

rfm_df["CustomerSegment"] = rfm_df.apply(segment_customer, axis=1)
rfm_df["IsAtRisk"] = rfm_df["RecencyDays"] >= churn_threshold_days

# ==========================================================
# KPI CALCULATIONS (SCALAR CONVERSIONS)
# ==========================================================

total_analyzed_customers = int(rfm_df["CustomerID"].nunique())

avg_recency_raw = rfm_df["RecencyDays"].mean() if not rfm_df.empty else 0
avg_recency = float(avg_recency_raw.iloc[0] if isinstance(avg_recency_raw, pd.Series) else avg_recency_raw)

champions_count = int(rfm_df[rfm_df["CustomerSegment"] == "Champions"].shape[0])
at_risk_count = int(rfm_df[rfm_df["IsAtRisk"]].shape[0])

churn_rate_pct = (at_risk_count / total_analyzed_customers * 100) if total_analyzed_customers > 0 else 0.0

# ==========================================================
# KPI CARDS
# ==========================================================

def kpi_card(title, value, icon, c1, c2):
    return f'<div style="background:linear-gradient(135deg,{c1},{c2}); padding:22px; border-radius:18px; color:white; text-align:center; box-shadow:0 4px 12px rgba(0,0,0,.15);"><div style="font-size:18px;">{icon} {title}</div><div style="font-size:32px; font-weight:bold; margin-top:10px;">{value}</div></div>'

k1, k2, k3, k4 = st.columns(4)

k1.markdown(kpi_card("Analyzed Cohort", f"{total_analyzed_customers:,}", "👥", "#2563eb", "#1e3a8a"), unsafe_allow_html=True)
k2.markdown(kpi_card("Avg Recency", f"{avg_recency:.0f} Days", "⏱️", "#16a34a", "#065f46"), unsafe_allow_html=True)
k3.markdown(kpi_card("Champion Clients", f"{champions_count:,}", "🏆", "#d97706", "#92400e"), unsafe_allow_html=True)
k4.markdown(kpi_card("At-Risk / Churn", f"{churn_rate_pct:.1f}%", "⚠️", "#dc2626", "#991b1b"), unsafe_allow_html=True)

# ==========================================================
# MODEL 1: RFM SEGMENTATION MATRIX & CLUSTER DISTRIBUTION
# ==========================================================

st.markdown("---")
left, right = st.columns(2)

with left:
    st.subheader("📊 Customer Segment Distribution (RFM)")
    
    seg_counts = rfm_df["CustomerSegment"].value_counts().reset_index()
    seg_counts.columns = ["Segment", "Count"]

    fig1 = px.pie(
        seg_counts,
        values="Count",
        names="Segment",
        hole=0.55,
        color_discrete_sequence=px.colors.qualitative.Set2,
        template="plotly_white"
    )
    fig1.update_layout(height=450)
    st.plotly_chart(fig1, use_container_width=True)

with right:
    st.subheader("💰 Revenue Contribution by Customer Segment")
    
    seg_rev = rfm_df.groupby("CustomerSegment", observed=False)["MonetaryValue"].sum().reset_index()

    fig2 = px.bar(
        seg_rev,
        x="CustomerSegment",
        y="MonetaryValue",
        color="CustomerSegment",
        color_discrete_sequence=px.colors.qualitative.Set2,
        text_auto=".2s",
        template="plotly_white"
    )
    fig2.update_layout(
        height=450,
        xaxis_title="",
        yaxis_title="Total Lifetime Value ($)",
        showlegend=False
    )
    st.plotly_chart(fig2, use_container_width=True)

# ==========================================================
# MODEL 2: BEHAVIORAL CLUSTERING (FREQUENCY VS MONETARY VS RECENCY)
# ==========================================================

st.markdown("---")
st.header("🎯 Predictive Behavioral Clustering Matrix")

fig3 = px.scatter(
    rfm_df,
    x="Frequency",
    y="MonetaryValue",
    size="AvgBasketSize",
    color="CustomerSegment",
    hover_name="CustomerID",
    hover_data=["RecencyDays", "RFM_Composite"],
    log_x=True,
    log_y=True,
    color_discrete_sequence=px.colors.qualitative.Bold,
    template="plotly_white"
)

fig3.update_layout(
    height=500,
    xaxis_title="Order Frequency (Log Scale)",
    yaxis_title="Monetary Value ($ - Log Scale)"
)

st.plotly_chart(fig3, use_container_width=True)

# ==========================================================
# MODEL 3: PRICE ELASTICITY & VOLUME SENSITIVITY
# ==========================================================

st.markdown("---")
st.header("📈 Product Price Elasticity & Volume Demand Sensitivity")

if "Description" in filtered_df.columns:
    elasticity_df = (
        filtered_df.groupby("Description")
        .agg(
            AvgPrice=("UnitPrice", "mean"),
            VolumeSold=("Quantity", "sum"),
            TotalRevenue=("TotalPrice", "sum")
        )
        .reset_index()
    )
    
    # Filter valid non-zero prices
    elasticity_df = elasticity_df[(elasticity_df["AvgPrice"] > 0) & (elasticity_df["VolumeSold"] > 0)]

    fig4 = px.scatter(
        elasticity_df,
        x="AvgPrice",
        y="VolumeSold",
        size="TotalRevenue",
        color="TotalRevenue",
        hover_name="Description",
        log_x=True,
        log_y=True,
        color_continuous_scale="Viridis",
        template="plotly_white"
    )

    fig4.update_layout(
        height=480,
        xaxis_title="Average Unit Price ($ - Log Scale)",
        yaxis_title="Volume Demand Sold (Units - Log Scale)"
    )

    st.plotly_chart(fig4, use_container_width=True)

# ==========================================================
# HIGH-VALUE AT-RISK ACCOUNTS TABLE
# ==========================================================

st.markdown("---")
st.header("🚨 Priority Action Required: High-Value Churn Risk Table")

at_risk_table = (
    rfm_df[rfm_df["IsAtRisk"]]
    .sort_values("MonetaryValue", ascending=False)
    .head(15)
    .copy()
)

if not at_risk_table.empty:
    display_at_risk = at_risk_table[
        [
            "CustomerID",
            "CustomerSegment",
            "RecencyDays",
            "Frequency",
            "MonetaryValue"
        ]
    ].copy()

    display_at_risk["MonetaryValue"] = display_at_risk["MonetaryValue"].round(2)

    st.dataframe(
        display_at_risk,
        use_container_width=True,
        hide_index=True
    )
else:
    st.success("✅ No high-value customer churn risk identified under selected inactivity parameters.")

# ==========================================================
# AI PREDICTIVE INSIGHTS
# ==========================================================

st.markdown("---")
st.header("🤖 AI Predictive Strategy Recommendations")

recs = []

recs.append(f"Cohort churn risk is currently **{churn_rate_pct:.1f}%** (inactive for over {churn_threshold_days} days). Deploy automated win-back email sequences.")

if champions_count > 0:
    recs.append(f"Identify top **{champions_count} Champions** and enroll them in exclusive VIP loyalty previews to maximize lifetime advocacy.")

recs.append("Monitor price elasticity curves on top-tier revenue products before initiating site-wide discount promotions.")

for r in recs:
    st.info("⚡ " + r)

# ==========================================================
# FOOTER
# ==========================================================

st.markdown("---")
st.caption("""
RetailPulse AI • Advanced Predictive Analytics Dashboard

Powered by Streamlit • Plotly • Python

© 2026
""")