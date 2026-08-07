import streamlit as st
import pandas as pd
import plotly.express as px


from styles import load_css
from utils import load_data

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Sales Analysis",
    page_icon="💰",
    layout="wide"
)

load_css("light")


df = load_data()

# ==========================================================
# HEADER
# ==========================================================

st.markdown("""
<div class="dashboard-title">💰 RetailPulse AI</div>
<div class="dashboard-subtitle">Sales Analysis Dashboard</div>
""", unsafe_allow_html=True)

st.header("💰 Sales Analysis")

# ==========================================================
# FILTERS
# ==========================================================

f1, f2, f3 = st.columns(3)

with f1:
    countries = sorted(df["Country"].dropna().unique())
    selected_country = st.multiselect(
        "🌍 Country",
        countries
    )

with f2:
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

    date_range = st.date_input(
        "📅 Date Range",
        [
            df["InvoiceDate"].min(),
            df["InvoiceDate"].max()
        ]
    )

with f3:
    products = sorted(
        df["Description"].dropna().unique()
    )[:50]

    selected_products = st.multiselect(
        "📦 Product",
        products
    )

# ==========================================================
# APPLY FILTERS
# ==========================================================

filtered_df = df.copy()

if selected_country:
    filtered_df = filtered_df[
        filtered_df["Country"].isin(selected_country)
    ]

if date_range and len(date_range) == 2:
    filtered_df = filtered_df[
        (filtered_df["InvoiceDate"] >= pd.to_datetime(date_range[0])) &
        (filtered_df["InvoiceDate"] <= pd.to_datetime(date_range[1]))
    ]

if selected_products:
    filtered_df = filtered_df[
        filtered_df["Description"].isin(selected_products)
    ]

# ==========================================================
# SALES KPIs
# ==========================================================

total_sales = filtered_df["TotalPrice"].sum()

total_orders = (
    filtered_df["Invoice"]
    .nunique()
)

avg_order = (
    total_sales / total_orders
    if total_orders > 0
    else 0
)

total_qty = (
    filtered_df["Quantity"]
    .sum()
)
# ==========================================================
# KPI CARDS
# ==========================================================

def kpi_card(title, value, icon, c1, c2):
    return f"""
    <div style="
        background:linear-gradient(135deg,{c1},{c2});
        padding:22px;
        border-radius:18px;
        color:white;
        text-align:center;
        box-shadow:0 4px 12px rgba(0,0,0,.15);
    ">
        <div style="font-size:18px;">{icon} {title}</div>

        <div style="
            font-size:32px;
            font-weight:bold;
            margin-top:10px;
        ">
            {value}
        </div>
    </div>
    """

k1, k2, k3, k4 = st.columns(4)

k1.markdown(
    kpi_card(
        "Revenue",
        f"${total_sales:,.0f}",
        "💰",
        "#2563eb",
        "#1e3a8a"
    ),
    unsafe_allow_html=True
)

k2.markdown(
    kpi_card(
        "Orders",
        f"{total_orders:,}",
        "🧾",
        "#16a34a",
        "#065f46"
    ),
    unsafe_allow_html=True
)

k3.markdown(
    kpi_card(
        "Units Sold",
        f"{total_qty:,}",
        "📦",
        "#d97706",
        "#92400e"
    ),
    unsafe_allow_html=True
)

k4.markdown(
    kpi_card(
        "Avg Order",
        f"${avg_order:,.2f}",
        "🛒",
        "#db2777",
        "#7e22ce"
    ),
    unsafe_allow_html=True
)

# ==========================================================
# MONTHLY SALES DATA
# ==========================================================

monthly_sales = (
    filtered_df
    .groupby(filtered_df["InvoiceDate"].dt.to_period("M"))
    ["TotalPrice"]
    .sum()
    .reset_index()
)

monthly_sales["InvoiceDate"] = (
    monthly_sales["InvoiceDate"]
    .astype(str)
)

# ==========================================================
# REVENUE TREND
# ==========================================================

st.markdown("## 📈 Revenue Trend")

fig = px.line(
    monthly_sales,
    x="InvoiceDate",
    y="TotalPrice",
    markers=True,
    template="plotly_white"
)

fig.update_layout(
    height=450,
    hovermode="x unified",
    xaxis_title="Month",
    yaxis_title="Revenue"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ==========================================================
# MONTHLY GROWTH
# ==========================================================

growth = monthly_sales.copy()

growth["Growth %"] = (
    growth["TotalPrice"]
    .pct_change()
    * 100
)

growth["Growth %"] = (
    growth["Growth %"]
    .fillna(0)
)

st.markdown("## 📈 Monthly Growth %")

fig = px.bar(
    growth,
    x="InvoiceDate",
    y="Growth %",
    color="Growth %",
    text_auto=".1f",
    template="plotly_white"
)

fig.update_layout(
    height=430
)

st.plotly_chart(
    fig,
    use_container_width=True
)
# ==========================================================
# SALES BY COUNTRY
# ==========================================================

st.markdown("## 🌍 Sales by Country")

country_sales = (
    filtered_df
    .groupby("Country")["TotalPrice"]
    .sum()
    .nlargest(10)
    .reset_index()
)

fig = px.bar(
    country_sales,
    x="Country",
    y="TotalPrice",
    color="TotalPrice",
    text_auto=".2s",
    template="plotly_white"
)

fig.update_layout(
    height=450,
    xaxis_title="Country",
    yaxis_title="Revenue"
)

st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# TOP PRODUCTS
# ==========================================================

st.markdown("## 🏆 Top 10 Products")

top_products = (
    filtered_df
    .groupby("Description")["TotalPrice"]
    .sum()
    .nlargest(10)
    .reset_index()
)

fig = px.bar(
    top_products,
    x="TotalPrice",
    y="Description",
    orientation="h",
    color="TotalPrice",
    text_auto=".2s",
    template="plotly_white"
)

fig.update_layout(
    height=500,
    yaxis=dict(categoryorder="total ascending")
)

st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# REVENUE DISTRIBUTION
# ==========================================================

left, right = st.columns(2)

with left:

    st.markdown("### 📦 Product Revenue Share")

    fig = px.pie(
        top_products,
        values="TotalPrice",
        names="Description",
        hole=0.55,
        template="plotly_white"
    )

    fig.update_layout(height=450)

    st.plotly_chart(fig, use_container_width=True)

with right:

    st.markdown("### 🌍 Country Revenue Share")

    fig = px.pie(
        country_sales,
        values="TotalPrice",
        names="Country",
        hole=0.55,
        template="plotly_white"
    )

    fig.update_layout(height=450)

    st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# SEASONAL SALES
# ==========================================================

st.markdown("## 📅 Seasonal Sales")

season_df = filtered_df.copy()

season_df["Month"] = (
    season_df["InvoiceDate"]
    .dt.month_name()
)

month_order = [
    "January","February","March","April",
    "May","June","July","August",
    "September","October","November","December"
]

season_df["Month"] = pd.Categorical(
    season_df["Month"],
    categories=month_order,
    ordered=True
)

season_sales = (
    season_df
    .groupby("Month")["TotalPrice"]
    .sum()
    .reset_index()
)

fig = px.area(
    season_sales,
    x="Month",
    y="TotalPrice",
    markers=True,
    template="plotly_white"
)

fig.update_layout(
    height=450,
    xaxis_title="Month",
    yaxis_title="Revenue"
)

st.plotly_chart(fig, use_container_width=True)
# ==========================================================
# SALES HEALTH SCORE
# ==========================================================

st.markdown("## ❤️ Sales Health Score")

health_score = 0

# Revenue Score
if total_sales > 1000000:
    health_score += 30
elif total_sales > 500000:
    health_score += 25
else:
    health_score += 15

# Orders Score
if total_orders > 5000:
    health_score += 25
elif total_orders > 2000:
    health_score += 20
else:
    health_score += 10

# Average Order Score
if avg_order > 250:
    health_score += 25
elif avg_order > 150:
    health_score += 20
else:
    health_score += 10

# Quantity Score
if total_qty > 50000:
    health_score += 20
elif total_qty > 20000:
    health_score += 15
else:
    health_score += 10

st.progress(health_score / 100)

st.metric(
    "Overall Sales Health",
    f"{health_score}/100"
)

# ==========================================================
# SALES SUMMARY
# ==========================================================

st.markdown("## 📋 Sales Summary")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Revenue",
    f"${total_sales:,.0f}"
)

c2.metric(
    "Orders",
    f"{total_orders:,}"
)

c3.metric(
    "Units Sold",
    f"{total_qty:,}"
)

c4.metric(
    "Average Order",
    f"${avg_order:,.2f}"
)

# ==========================================================
# SALES FORECAST
# ==========================================================

st.markdown("## 🔮 Sales Forecast")

forecast = monthly_sales.copy()

forecast["Forecast"] = (
    forecast["TotalPrice"]
    .rolling(window=3, min_periods=1)
    .mean()
)

fig = px.line(
    forecast,
    x="InvoiceDate",
    y=["TotalPrice", "Forecast"],
    markers=True,
    template="plotly_white"
)

fig.update_layout(
    height=500,
    hovermode="x unified",
    legend_title=""
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ==========================================================
# AI SALES INSIGHTS
# ==========================================================

st.markdown("## 🧠 AI Sales Insights")

if not top_products.empty:
    best_product = top_products.iloc[0]["Description"]
else:
    best_product = "N/A"

if not country_sales.empty:
    best_country = country_sales.iloc[0]["Country"]
else:
    best_country = "N/A"

insight1, insight2 = st.columns(2)

with insight1:

    st.info(
        f"""
**Top Revenue Product**

{best_product}

This product contributes the highest revenue and should remain a priority for inventory planning.
"""
    )

with insight2:

    st.success(
        f"""
**Highest Revenue Market**

{best_country}

Focus promotional campaigns and inventory planning on this market.
"""
    )

# ==========================================================
# AI RECOMMENDATIONS
# ==========================================================

st.markdown("## 🤖 AI Recommendations")

recommendations = []

if avg_order < 250:
    recommendations.append(
        "Increase Average Order Value through bundles and cross-selling."
    )

if total_orders < total_qty / 10:
    recommendations.append(
        "Demand is strong. Ensure adequate inventory for fast-moving products."
    )

if not top_products.empty:
    recommendations.append(
        f"Increase stock availability for '{best_product}'."
    )

if not country_sales.empty:
    recommendations.append(
        f"Expand marketing efforts in {best_country}."
    )

recommendations.append(
    "Review monthly revenue trends to identify seasonal opportunities."
)

for rec in recommendations:
    st.success("✅ " + rec)

# ==========================================================
# FOOTER
# ==========================================================

st.markdown("---")

st.caption(
"""
RetailPulse AI • Sales Analysis Dashboard

Powered by Streamlit • Plotly • Python

© 2026
"""
)