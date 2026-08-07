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
    page_title="KPI Summary",
    page_icon="📌",
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
<div class="dashboard-title">📌 RetailPulse AI</div>
<div class="dashboard-subtitle">Master Key Performance Indicator (KPI) Summary & Scorecard</div>
""", unsafe_allow_html=True)

st.header("📌 KPI Summary Scorecard")

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

if "InvoiceDate" in df.columns:
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

# ==========================================================
# 🎛️ FILTERS & SLICERS
# ==========================================================

st.markdown("### 🎛️ Global Slicers")

f1, f2 = st.columns(2)

with f1:
    countries = sorted(df["Country"].dropna().unique()) if "Country" in df.columns else []
    selected_country = st.multiselect("🌍 Market / Country Slicer", countries)

with f2:
    if "InvoiceDate" in df.columns and not df["InvoiceDate"].isna().all():
        min_date = df["InvoiceDate"].min().date()
        max_date = df["InvoiceDate"].max().date()
        date_range = st.date_input("📅 Date Range Slicer", (min_date, max_date))
    else:
        date_range = None

# ==========================================================
# APPLY FILTERS
# ==========================================================

filtered_df = df.copy()

if selected_country and "Country" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["Country"].isin(selected_country)]

if date_range and isinstance(date_range, tuple) and len(date_range) == 2:
    filtered_df = filtered_df[
        (filtered_df["InvoiceDate"] >= pd.to_datetime(date_range[0])) &
        (filtered_df["InvoiceDate"] <= pd.to_datetime(date_range[1]) + pd.Timedelta(days=1))
    ]

filtered_df = filtered_df.loc[:, ~filtered_df.columns.duplicated(keep='first')].copy()

# ==========================================================
# MASTER KPI CALCULATIONS (SCALAR SAFETY)
# ==========================================================

rev_raw = filtered_df["TotalPrice"].sum() if not filtered_df.empty else 0.0
total_revenue = float(rev_raw.iloc[0] if isinstance(rev_raw, pd.Series) else rev_raw)

orders_raw = filtered_df["InvoiceNo"].nunique() if not filtered_df.empty else 0
total_orders = int(orders_raw.iloc[0] if isinstance(orders_raw, pd.Series) else orders_raw)

units_raw = filtered_df["Quantity"].sum() if not filtered_df.empty else 0
total_units = int(units_raw.iloc[0] if isinstance(units_raw, pd.Series) else units_raw)

cust_raw = filtered_df[filtered_df["CustomerID"] != "Guest"]["CustomerID"].nunique() if not filtered_df.empty else 0
total_customers = int(cust_raw.iloc[0] if isinstance(cust_raw, pd.Series) else cust_raw)

products_raw = filtered_df["Description"].nunique() if not filtered_df.empty else 0
total_products = int(products_raw.iloc[0] if isinstance(products_raw, pd.Series) else products_raw)

markets_raw = filtered_df["Country"].nunique() if not filtered_df.empty else 0
total_markets = int(markets_raw.iloc[0] if isinstance(markets_raw, pd.Series) else markets_raw)

avg_order_value = total_revenue / total_orders if total_orders > 0 else 0.0
avg_items_per_order = total_units / total_orders if total_orders > 0 else 0.0

# Estimated Gross Margin (assuming 60% standard retail COGS baseline)
estimated_cogs = total_revenue * 0.60
estimated_gross_profit = total_revenue - estimated_cogs
estimated_margin_pct = (estimated_gross_profit / total_revenue * 100) if total_revenue > 0 else 0.0

# ==========================================================
# KPI CARDS ROW 1: FINANCIAL & COMMERCIAL
# ==========================================================

def kpi_card(title, value, icon, c1, c2):
    return f'<div style="background:linear-gradient(135deg,{c1},{c2}); padding:22px; border-radius:18px; color:white; text-align:center; box-shadow:0 4px 12px rgba(0,0,0,.15);"><div style="font-size:18px;">{icon} {title}</div><div style="font-size:32px; font-weight:bold; margin-top:10px;">{value}</div></div>'

st.markdown("### 💰 Financial & Commercial Metrics")
k1, k2, k3, k4 = st.columns(4)

k1.markdown(kpi_card("Total Revenue", f"${total_revenue:,.0f}", "💵", "#2563eb", "#1e3a8a"), unsafe_allow_html=True)
k2.markdown(kpi_card("Gross Profit (Est.)", f"${estimated_gross_profit:,.0f}", "💹", "#16a34a", "#065f46"), unsafe_allow_html=True)
k3.markdown(kpi_card("Profit Margin", f"{estimated_margin_pct:.1f}%", "📊", "#d97706", "#92400e"), unsafe_allow_html=True)
k4.markdown(kpi_card("Avg Order Value", f"${avg_order_value:,.2f}", "🛒", "#db2777", "#7e22ce"), unsafe_allow_html=True)

# ==========================================================
# KPI CARDS ROW 2: OPERATIONAL & PORTFOLIO
# ==========================================================

st.markdown("---")
st.markdown("### 📦 Operations & Portfolio Metrics")
k5, k6, k7, k8 = st.columns(4)

k5.markdown(kpi_card("Total Orders", f"{total_orders:,}", "🧾", "#2563eb", "#1d4ed8"), unsafe_allow_html=True)
k6.markdown(kpi_card("Units Delivered", f"{total_units:,}", "📦", "#059669", "#047857"), unsafe_allow_html=True)
k7.markdown(kpi_card("Active Client Base", f"{total_customers:,}", "👥", "#f59e0b", "#b45309"), unsafe_allow_html=True)
k8.markdown(kpi_card("Active Products", f"{total_products:,}", "🏷️", "#7c3aed", "#5b21b6"), unsafe_allow_html=True)

# ==========================================================
# EXECUTIVE SUMMARY SCORECARD TABLE
# ==========================================================

st.markdown("---")
st.header("📋 Master Executive Scorecard")

scorecard_data = {
    "Metric Domain": ["Financial", "Financial", "Financial", "Commercial", "Operations", "Operations", "Portfolio", "Geographic"],
    "Key Performance Indicator": [
        "Gross Sales Revenue",
        "Estimated Gross Profit",
        "Gross Margin %",
        "Average Order Value (AOV)",
        "Total Orders Fulfilled",
        "Total Units Shipped",
        "Active Product Catalog (SKUs)",
        "Active Geographic Markets"
    ],
    "Current Period Value": [
        f"${total_revenue:,.2f}",
        f"${estimated_gross_profit:,.2f}",
        f"{estimated_margin_pct:.1f}%",
        f"${avg_order_value:,.2f}",
        f"{total_orders:,}",
        f"{total_units:,}",
        f"{total_products:,}",
        f"{total_markets:,}"
    ],
    "Benchmark Status": [
        "🟢 Healthy",
        "🟢 Healthy",
        "🟡 Moderate",
        "🟢 Optimal",
        "🟢 Strong Volume",
        "🟢 High Throughput",
        "🟢 Diversified",
        "🟢 Broad Expansion"
    ]
}

scorecard_df = pd.DataFrame(scorecard_data)

st.dataframe(
    scorecard_df,
    use_container_width=True,
    hide_index=True
)

# ==========================================================
# VISUAL BREAKDOWN CHARTS
# ==========================================================

st.markdown("---")
left, right = st.columns(2)

with left:
    st.subheader("📊 Revenue Contribution by Market")
    
    if "Country" in filtered_df.columns:
        market_kpis = (
            filtered_df.groupby("Country")["TotalPrice"]
            .sum()
            .nlargest(10)
            .reset_index()
        )
        
        fig1 = px.bar(
            market_kpis,
            x="TotalPrice",
            y="Country",
            orientation="h",
            color="TotalPrice",
            text_auto=".2s",
            color_continuous_scale="Blues",
            template="plotly_white"
        )
        fig1.update_layout(height=450, yaxis=dict(categoryorder="total ascending"), xaxis_title="Revenue ($)")
        st.plotly_chart(fig1, use_container_width=True)

with right:
    st.subheader("📈 Monthly Performance Momentum")
    
    if "InvoiceDate" in filtered_df.columns:
        monthly_kpis = (
            filtered_df.groupby(filtered_df["InvoiceDate"].dt.to_period("M"))["TotalPrice"]
            .sum()
            .reset_index()
        )
        
        monthly_kpis["InvoiceDate"] = monthly_kpis["InvoiceDate"].astype(str)

        fig2 = px.line(
            monthly_kpis,
            x="InvoiceDate",
            y="TotalPrice",
            markers=True,
            template="plotly_white"
        )
        fig2.update_layout(height=450, xaxis_title="Month", yaxis_title="Revenue ($)", hovermode="x unified")
        st.plotly_chart(fig2, use_container_width=True)

# ==========================================================
# FOOTER
# ==========================================================

st.markdown("---")
st.caption("""
RetailPulse AI • Master KPI Summary Scorecard

Powered by Streamlit • Plotly • Python

© 2026
""")