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
    page_title="Profitability Analytics",
    page_icon="💹",
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
<div class="dashboard-title">💹 RetailPulse AI</div>
<div class="dashboard-subtitle">Advanced Profitability, Margin Analysis & COGS Decomposition</div>
""", unsafe_allow_html=True)

st.header("💹 Profit Analysis")

# ==========================================================
# DATA PREPARATION & COLUMN STANDARDIZATION
# ==========================================================

df.columns = df.columns.str.strip()

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
    "Cost": "UnitCost",
    "unit_cost": "UnitCost",
    "Unit Cost": "UnitCost"
}
df = df.rename(columns=column_mapping)

# Remove duplicate column names if mapping produced duplicates
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

# Estimate UnitCost if not explicitly present in dataset (Standard retail baseline ~60% COGS)
if "UnitCost" not in df.columns:
    df["UnitCost"] = df["UnitPrice"] * 0.60

df["TotalCost"] = df["Quantity"] * df["UnitCost"]
df["GrossProfit"] = df["TotalPrice"] - df["TotalCost"]

# ==========================================================
# FILTERS
# ==========================================================

st.markdown("### 🎛️ Profitability Filters")

f1, f2, f3 = st.columns(3)

with f1:
    countries = sorted(df["Country"].dropna().unique()) if "Country" in df.columns else []
    selected_country = st.multiselect("🌍 Country", countries)

with f2:
    if "InvoiceDate" in df.columns and not df["InvoiceDate"].isna().all():
        min_date = df["InvoiceDate"].min().date()
        max_date = df["InvoiceDate"].max().date()
        date_range = st.date_input("📅 Date Range", (min_date, max_date))
    else:
        date_range = None

with f3:
    cogs_margin_adjustment = st.slider(
        "⚙️ Assumed COGS Ratio (%)",
        min_value=30,
        max_value=80,
        value=60,
        step=5,
        help="Simulate profit impact by dynamically adjusting estimated COGS percentage."
    )

# ==========================================================
# APPLY FILTERS & SIMULATION
# ==========================================================

filtered_df = df.copy()

# Recalculate dynamic simulation based on user COGS slider
filtered_df["TotalCost"] = filtered_df["Quantity"] * (filtered_df["UnitPrice"] * (cogs_margin_adjustment / 100.0))
filtered_df["GrossProfit"] = filtered_df["TotalPrice"] - filtered_df["TotalCost"]

if selected_country and "Country" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["Country"].isin(selected_country)]

if date_range and isinstance(date_range, tuple) and len(date_range) == 2:
    filtered_df = filtered_df[
        (filtered_df["InvoiceDate"] >= pd.to_datetime(date_range[0])) &
        (filtered_df["InvoiceDate"] <= pd.to_datetime(date_range[1]) + pd.Timedelta(days=1))
    ]

filtered_df = filtered_df.loc[:, ~filtered_df.columns.duplicated(keep='first')].copy()

# ==========================================================
# KPI CALCULATIONS (SAFE SCALAR CONVERSIONS)
# ==========================================================

revenue_raw = filtered_df["TotalPrice"].sum() if not filtered_df.empty else 0.0
total_revenue = float(revenue_raw.iloc[0] if isinstance(revenue_raw, pd.Series) else revenue_raw)

cost_raw = filtered_df["TotalCost"].sum() if not filtered_df.empty else 0.0
total_cost = float(cost_raw.iloc[0] if isinstance(cost_raw, pd.Series) else cost_raw)

profit_raw = filtered_df["GrossProfit"].sum() if not filtered_df.empty else 0.0
total_gross_profit = float(profit_raw.iloc[0] if isinstance(profit_raw, pd.Series) else profit_raw)

profit_margin_pct = (total_gross_profit / total_revenue * 100) if total_revenue > 0 else 0.0

# ==========================================================
# KPI CARDS
# ==========================================================

def kpi_card(title, value, icon, c1, c2):
    return f'<div style="background:linear-gradient(135deg,{c1},{c2}); padding:22px; border-radius:18px; color:white; text-align:center; box-shadow:0 4px 12px rgba(0,0,0,.15);"><div style="font-size:18px;">{icon} {title}</div><div style="font-size:32px; font-weight:bold; margin-top:10px;">{value}</div></div>'

k1, k2, k3, k4 = st.columns(4)

k1.markdown(kpi_card("Total Revenue", f"${total_revenue:,.0f}", "💵", "#2563eb", "#1e3a8a"), unsafe_allow_html=True)
k2.markdown(kpi_card("Total Cost (COGS)", f"${total_cost:,.0f}", "🏷️", "#dc2626", "#991b1b"), unsafe_allow_html=True)
k3.markdown(kpi_card("Gross Profit", f"${total_gross_profit:,.0f}", "💹", "#16a34a", "#065f46"), unsafe_allow_html=True)
k4.markdown(kpi_card("Profit Margin", f"{profit_margin_pct:.1f}%", "📊", "#d97706", "#92400e"), unsafe_allow_html=True)

# ==========================================================
# REVENUE vs COST vs PROFIT TREND
# ==========================================================

st.markdown("---")
st.header("📈 Monthly Revenue, Cost & Profit Waterfall")

if not filtered_df.empty and "InvoiceDate" in filtered_df.columns:
    monthly_profit = (
        filtered_df.groupby(filtered_df["InvoiceDate"].dt.to_period("M"))
        .agg(
            Revenue=("TotalPrice", "sum"),
            Cost=("TotalCost", "sum"),
            Profit=("GrossProfit", "sum")
        )
        .reset_index()
    )
    
    monthly_profit["InvoiceDate"] = monthly_profit["InvoiceDate"].astype(str)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=monthly_profit["InvoiceDate"],
        y=monthly_profit["Revenue"],
        name="Revenue",
        marker_color="#2563eb"
    ))

    fig.add_trace(go.Bar(
        x=monthly_profit["InvoiceDate"],
        y=monthly_profit["Cost"],
        name="COGS",
        marker_color="#ef4444"
    ))

    fig.add_trace(go.Scatter(
        x=monthly_profit["InvoiceDate"],
        y=monthly_profit["Profit"],
        name="Gross Profit",
        line=dict(color="#16a34a", width=3, shape="spline")
    ))

    fig.update_layout(
        height=480,
        barmode="group",
        template="plotly_white",
        xaxis_title="Month",
        yaxis_title="Amount ($)",
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# PROFIT BY COUNTRY & TOP PROFITABLE PRODUCTS
# ==========================================================

st.markdown("---")
left, right = st.columns(2)

with left:
    st.subheader("🌍 Top 10 Most Profitable Markets")
    if "Country" in filtered_df.columns:
        country_profit = (
            filtered_df.groupby("Country")
            .agg(Profit=("GrossProfit", "sum"))
            .nlargest(10, "Profit")
            .reset_index()
        )

        fig = px.bar(
            country_profit,
            x="Profit",
            y="Country",
            orientation="h",
            color="Profit",
            text_auto=".2s",
            color_continuous_scale="Greens",
            template="plotly_white"
        )
        fig.update_layout(height=450, yaxis=dict(categoryorder="total ascending"))
        st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("🏆 Top 10 High-Margin Products")
    if "Description" in filtered_df.columns:
        product_profit = (
            filtered_df.groupby("Description")
            .agg(
                Revenue=("TotalPrice", "sum"),
                Profit=("GrossProfit", "sum")
            )
            .nlargest(10, "Profit")
            .reset_index()
        )

        fig = px.bar(
            product_profit,
            x="Profit",
            y="Description",
            orientation="h",
            color="Profit",
            text_auto=".2s",
            color_continuous_scale="Viridis",
            template="plotly_white"
        )
        fig.update_layout(height=450, yaxis=dict(categoryorder="total ascending"))
        st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# MARGIN DISTRIBUTION MATRIX
# ==========================================================

st.markdown("---")
st.header("🎯 Revenue vs. Gross Profit Margin Matrix")

if "Description" in filtered_df.columns:
    prod_matrix = (
        filtered_df.groupby("Description")
        .agg(
            Revenue=("TotalPrice", "sum"),
            Profit=("GrossProfit", "sum")
        )
        .reset_index()
    )
    
    prod_matrix["MarginPct"] = (prod_matrix["Profit"] / prod_matrix["Revenue"].replace(0, 1)) * 100

    fig = px.scatter(
        prod_matrix,
        x="Revenue",
        y="MarginPct",
        size="Profit",
        color="MarginPct",
        hover_name="Description",
        log_x=True,
        color_continuous_scale="Blugrn",
        template="plotly_white"
    )

    fig.update_layout(
        height=500,
        xaxis_title="Total Revenue ($ - Log Scale)",
        yaxis_title="Gross Profit Margin (%)"
    )

    st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# AI PROFITABILITY RECOMMENDATIONS
# ==========================================================

st.markdown("---")
st.header("🤖 AI Profitability Recommendations")

recs = []

if profit_margin_pct >= 40:
    recs.append(f"Healthy gross profit margin of **{profit_margin_pct:.1f}%**. Continue current pricing strategy.")
else:
    recs.append(f"Profit margin is **{profit_margin_pct:.1f}%**. Explore cost-optimization or price adjustment on low-margin items.")

if "Description" in filtered_df.columns and not product_profit.empty:
    top_p = product_profit.iloc[0]["Description"]
    recs.append(f"Primary profit generator: **{top_p}**. Focus marketing efforts on driving volume for this item.")

for r in recs:
    st.success("✅ " + r)

# ==========================================================
# FOOTER
# ==========================================================

st.markdown("---")
st.caption("""
RetailPulse AI • Profitability Analytics Dashboard

Powered by Streamlit • Plotly • Python

© 2026
""")