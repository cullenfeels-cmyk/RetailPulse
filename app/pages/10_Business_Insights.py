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
    page_title="Business Insights",
    page_icon="🧠",
    layout="wide"
)

load_css("light")


# ==========================================================
# LOAD DATA
# ==========================================================

df = load_data()

# ==========================================================
# PAGE TITLE
# ==========================================================

st.markdown("""
<div class="dashboard-title">🧠 RetailPulse AI</div>
<div class="dashboard-subtitle">Executive Strategic Insights, Portfolio Performance & Commercial Dynamics</div>
""", unsafe_allow_html=True)

st.header("🧠 Business Insights")

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
    df["CustomerID"] = "Guest"

# ==========================================================
# 🎛️ SLICERS / FILTERS (3 Interactive Slicers)
# ==========================================================

st.markdown("### 🎛️ Strategic Filters & Slicers")

slicer1, slicer2, slicer3 = st.columns(3)

with slicer1:
    countries = sorted(df["Country"].dropna().unique()) if "Country" in df.columns else []
    selected_country = st.multiselect("🌍 Geographic Market Slicer", countries)

with slicer2:
    if "InvoiceDate" in df.columns and not df["InvoiceDate"].isna().all():
        min_date = df["InvoiceDate"].min().date()
        max_date = df["InvoiceDate"].max().date()
        date_range = st.date_input("📅 Date Range Slicer", (min_date, max_date))
    else:
        date_range = None

with slicer3:
    max_rev = int(df["TotalPrice"].max()) if not df.empty and df["TotalPrice"].max() > 0 else 1000
    min_order_value = st.slider("💰 Minimum Order Value Slicer ($)", 0, max_rev, 0, step=10)

# ==========================================================
# APPLY SLICERS
# ==========================================================

filtered_df = df.copy()

if selected_country and "Country" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["Country"].isin(selected_country)]

if date_range and isinstance(date_range, tuple) and len(date_range) == 2:
    filtered_df = filtered_df[
        (filtered_df["InvoiceDate"] >= pd.to_datetime(date_range[0])) &
        (filtered_df["InvoiceDate"] <= pd.to_datetime(date_range[1]) + pd.Timedelta(days=1))
    ]

if min_order_value > 0:
    filtered_df = filtered_df[filtered_df["TotalPrice"] >= min_order_value]

filtered_df = filtered_df.loc[:, ~filtered_df.columns.duplicated(keep='first')].copy()

# ==========================================================
# KPI CALCULATIONS (4 KPI Cards with Scalar Safety)
# ==========================================================

revenue_raw = filtered_df["TotalPrice"].sum() if not filtered_df.empty else 0.0
total_revenue = float(revenue_raw.iloc[0] if isinstance(revenue_raw, pd.Series) else revenue_raw)

orders_raw = filtered_df["InvoiceNo"].nunique() if not filtered_df.empty else 0
total_orders = int(orders_raw.iloc[0] if isinstance(orders_raw, pd.Series) else orders_raw)

customers_raw = filtered_df["CustomerID"].dropna().nunique() if not filtered_df.empty else 0
total_customers = int(customers_raw.iloc[0] if isinstance(customers_raw, pd.Series) else customers_raw)

avg_order_value = total_revenue / total_orders if total_orders > 0 else 0.0

# ==========================================================
# 🎴 KPI CARDS (4 Cards)
# ==========================================================

def kpi_card(title, value, icon, c1, c2):
    return f'<div style="background:linear-gradient(135deg,{c1},{c2}); padding:22px; border-radius:18px; color:white; text-align:center; box-shadow:0 4px 12px rgba(0,0,0,.15);"><div style="font-size:18px;">{icon} {title}</div><div style="font-size:32px; font-weight:bold; margin-top:10px;">{value}</div></div>'

k1, k2, k3, k4 = st.columns(4)

k1.markdown(kpi_card("Commercial Revenue", f"${total_revenue:,.0f}", "💰", "#2563eb", "#1e3a8a"), unsafe_allow_html=True)
k2.markdown(kpi_card("Total Orders", f"{total_orders:,}", "🧾", "#16a34a", "#065f46"), unsafe_allow_html=True)
k3.markdown(kpi_card("Active Client Base", f"{total_customers:,}", "👥", "#f59e0b", "#92400e"), unsafe_allow_html=True)
k4.markdown(kpi_card("Avg Order Value", f"${avg_order_value:,.2f}", "🎯", "#db2777", "#7e22ce"), unsafe_allow_html=True)

# ==========================================================
# CHART 1 & CHART 2 (Top Markets & Product Revenue Concentration)
# ==========================================================

st.markdown("---")
col_c1, col_c2 = st.columns(2)

with col_c1:
    st.subheader("📊 Chart 1: Market Share Concentration (Top 10 Countries)")
    
    country_summary = (
        filtered_df.groupby("Country")["TotalPrice"]
        .sum()
        .nlargest(10)
        .reset_index()
    )
    
    fig1 = px.pie(
        country_summary,
        values="TotalPrice",
        names="Country",
        hole=0.55,
        color_discrete_sequence=px.colors.qualitative.Set3,
        template="plotly_white"
    )
    fig1.update_layout(height=450)
    st.plotly_chart(fig1, use_container_width=True)

with col_c2:
    st.subheader("🏆 Chart 2: Top 10 Product Revenue Drivers")
    
    product_summary = (
        filtered_df.groupby("Description")["TotalPrice"]
        .sum()
        .nlargest(10)
        .reset_index()
    )
    
    fig2 = px.bar(
        product_summary,
        x="TotalPrice",
        y="Description",
        orientation="h",
        color="TotalPrice",
        text_auto=".2s",
        color_continuous_scale="Blues",
        template="plotly_white"
    )
    fig2.update_layout(height=450, yaxis=dict(categoryorder="total ascending"), xaxis_title="Revenue ($)")
    st.plotly_chart(fig2, use_container_width=True)

# ==========================================================
# CHART 3 & CHART 4 (Order Size Segmentation & Country Efficiency)
# ==========================================================

st.markdown("---")
col_c3, col_c4 = st.columns(2)

with col_c3:
    st.subheader("🛒 Chart 3: Order Size Tier Distribution")
    
    # Calculate order values per invoice
    invoice_values = filtered_df.groupby("InvoiceNo")["TotalPrice"].sum().reset_index()
    
    bins = [0, 50, 150, 500, 1000, np.inf]
    labels = ["< $50", "$50 - $150", "$150 - $500", "$500 - $1k", "> $1k"]
    invoice_values["OrderTier"] = pd.cut(invoice_values["TotalPrice"], bins=bins, labels=labels)
    
    tier_summary = invoice_values["OrderTier"].value_counts().reset_index()
    tier_summary.columns = ["OrderTier", "OrderCount"]
    
    fig3 = px.bar(
        tier_summary,
        x="OrderTier",
        y="OrderCount",
        color="OrderCount",
        text_auto=True,
        color_continuous_scale="Teal",
        template="plotly_white"
    )
    fig3.update_layout(height=450, xaxis_title="Order Value Tier", yaxis_title="Number of Orders")
    st.plotly_chart(fig3, use_container_width=True)

with col_c4:
    st.subheader("🌍 Chart 4: Market Efficiency Matrix (Orders vs. Revenue)")
    
    market_perf = (
        filtered_df.groupby("Country")
        .agg(
            Revenue=("TotalPrice", "sum"),
            Orders=("InvoiceNo", "nunique"),
            Units=("Quantity", "sum")
        )
        .reset_index()
    )
    
    fig4 = px.scatter(
        market_perf,
        x="Orders",
        y="Revenue",
        size="Units",
        color="Revenue",
        hover_name="Country",
        log_x=True,
        log_y=True,
        color_continuous_scale="Turbo",
        template="plotly_white"
    )
    fig4.update_layout(height=450, xaxis_title="Orders (Log Scale)", yaxis_title="Revenue ($ - Log Scale)")
    st.plotly_chart(fig4, use_container_width=True)

# ==========================================================
# CHART 5 (Customer Value vs Frequency Scatter Quadrant)
# ==========================================================

st.markdown("---")
st.subheader("🎯 Chart 5: Customer Value Matrix (Monetary Value vs Order Frequency)")

customer_matrix = (
    filtered_df[filtered_df["CustomerID"] != "Guest"]
    .groupby("CustomerID")
    .agg(
        TotalSpend=("TotalPrice", "sum"),
        OrderFrequency=("InvoiceNo", "nunique"),
        TotalItems=("Quantity", "sum")
    )
    .reset_index()
)

if not customer_matrix.empty:
    fig5 = px.scatter(
        customer_matrix,
        x="OrderFrequency",
        y="TotalSpend",
        size="TotalItems",
        color="TotalSpend",
        hover_data=["CustomerID"],
        log_x=True,
        log_y=True,
        color_continuous_scale="Plasma",
        template="plotly_white"
    )
    
    # Add benchmark median lines
    fig5.add_hline(y=customer_matrix["TotalSpend"].median(), line_dash="dash", line_color="#dc2626", annotation_text="Median Spend")
    fig5.add_vline(x=customer_matrix["OrderFrequency"].median(), line_dash="dash", line_color="#2563eb", annotation_text="Median Frequency")
    
    fig5.update_layout(
        height=500,
        xaxis_title="Order Frequency (Log Scale)",
        yaxis_title="Total Spend ($ - Log Scale)"
    )
    
    st.plotly_chart(fig5, use_container_width=True)
else:
    st.info("ℹ️ No identifiable customer IDs available for value quadrant analysis under current filter selection.")

# ==========================================================
# AI STRATEGIC EXECUTIVE INSIGHTS
# ==========================================================

st.markdown("---")
st.header("🤖 AI Executive Business Insights")

insights = []

if not country_summary.empty:
    top_c = country_summary.iloc[0]["Country"]
    insights.append(f"Top Geographic Market: **{top_c}** leads gross sales. Focus localized expansion and fulfillment assets in this region.")

if not product_summary.empty:
    top_p = product_summary.iloc[0]["Description"]
    insights.append(f"Primary Commercial Revenue Driver: **'{top_p}'**. Maintain high stock availability to protect revenue baseline.")

insights.append(f"Average Commercial Order Value stands at **${avg_order_value:,.2f}**. Deploy cross-selling bundles to push transactions into higher tiers.")

for ins in insights:
    st.info("💡 " + ins)

# ==========================================================
# FOOTER
# ==========================================================

st.markdown("---")
st.caption("""
RetailPulse AI • Business Insights Dashboard

Powered by Streamlit • Plotly • Python

© 2026
""")