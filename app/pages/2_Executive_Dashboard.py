import streamlit as st
import pandas as pd
import plotly.express as px

from styles import load_css
from utils import load_data
st.set_page_config(
    page_title="Executive Dashboard",
    page_icon="📊",
    layout="wide"
)

load_css("light")
if st.button("⬅️ Back to Home"):
    st.switch_page("pages/1_Home.py")

df = load_data()
st.markdown("""
<div class="dashboard-title">🚀 RetailPulse AI Platform</div>
<div class="dashboard-subtitle">Executive Dashboard</div>
""", unsafe_allow_html=True)

st.header("📊 Executive Dashboard")
# ==========================================================
# 🎛️ POWER BI STYLE TOP FILTERS
# ==========================================================

st.markdown("### 🎛️ Filters")

f1, f2, f3 = st.columns(3)

with f1:
    if "Country" in df.columns:
        selected_country = st.multiselect(
            "🌍 Country",
            sorted(df["Country"].dropna().unique())
        )
    else:
        selected_country = []

with f2:
    if "InvoiceDate" in df.columns:
        df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
        date_range = st.date_input(
            "📅 Date Range",
            [df["InvoiceDate"].min(), df["InvoiceDate"].max()]
        )
    else:
        date_range = None

with f3:
    if "Description" in df.columns:
        selected_products = st.multiselect(
            "📦 Product",
            sorted(df["Description"].dropna().unique())[:50]
        )
    else:
        selected_products = []

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
# KPI CALCULATION
# ==========================================================

# Revenue
if "TotalPrice" in filtered_df.columns:
    total_sales = filtered_df["TotalPrice"].sum()
elif "Sales" in filtered_df.columns:
    total_sales = filtered_df["Sales"].sum()
else:
    total_sales = 0

# Orders
order_col = None
for col in ["InvoiceNo", "Invoice", "OrderID"]:
    if col in filtered_df.columns:
        order_col = col
        break

if order_col:
    total_orders = filtered_df[order_col].dropna().nunique()
else:
    total_orders = len(filtered_df)

# Customers
customer_col = None
for col in ["CustomerID", "Customer ID"]:
    if col in filtered_df.columns:
        customer_col = col
        break

if customer_col:
    total_customers = filtered_df[customer_col].dropna().nunique()
else:
    total_customers = 0

# Products
product_col = None
for col in ["StockCode", "ProductID", "Description"]:
    if col in filtered_df.columns:
        product_col = col
        break

if product_col:
    total_products = filtered_df[product_col].dropna().nunique()
else:
    total_products = 0

# Average Order Value
avg_order_value = (
    total_sales / total_orders
    if total_orders > 0
    else 0
)

# ==========================================================
# KPI CARDS
# ==========================================================

def kpi_card(title, value, icon, c1, c2):
    return f'<div style="background: linear-gradient(135deg,{c1},{c2}); padding:22px; border-radius:16px; color:white; box-shadow:0 4px 10px rgba(0,0,0,.15); text-align:center;"><div style="font-size:18px;">{icon} {title}</div><div style="font-size:34px; font-weight:bold; margin-top:10px;">{value}</div></div>'

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
        "Customers",
        f"{total_customers:,}",
        "👥",
        "#f59e0b",
        "#92400e"
    ),
    unsafe_allow_html=True
)

k4.markdown(
    kpi_card(
        "Products",
        f"{total_products:,}",
        "📦",
        "#db2777",
        "#7e22ce"
    ),
    unsafe_allow_html=True
)
# ==========================================================
# EXECUTIVE PERFORMANCE BANNER
# ==========================================================

st.markdown("---")

if not filtered_df.empty:

    best_product = (
        filtered_df.groupby("Description")["TotalPrice"]
        .sum()
        .idxmax()
        if "Description" in filtered_df.columns
        else "N/A"
    )

    best_country = (
        filtered_df.groupby("Country")["TotalPrice"]
        .sum()
        .idxmax()
        if "Country" in filtered_df.columns
        else "N/A"
    )

else:
    best_product = "N/A"
    best_country = "N/A"

st.info(
    f"""
### 📈 Executive Highlights

💰 Revenue: **${total_sales:,.0f}**

🧾 Orders: **{total_orders:,}**

👥 Customers: **{total_customers:,}**

🏆 Best Product: **{best_product}**

🌍 Best Country: **{best_country}**

📦 Average Order Value: **${avg_order_value:,.2f}**
"""
)

# ==========================================================
# REVENUE TREND
# ==========================================================

st.markdown("## 📈 Revenue Trend")

if "InvoiceDate" in filtered_df.columns:

    trend = (
        filtered_df
        .groupby(filtered_df["InvoiceDate"].dt.to_period("M"))["TotalPrice"]
        .sum()
        .reset_index()
    )

    trend["InvoiceDate"] = trend["InvoiceDate"].astype(str)

    fig = px.line(
        trend,
        x="InvoiceDate",
        y="TotalPrice",
        markers=True,
        template="plotly_white"
    )

    fig.update_layout(
        height=450,
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# REVENUE vs ORDERS
# ==========================================================

st.markdown("## 💰 Revenue vs Orders")

if (
    "InvoiceDate" in filtered_df.columns
    and "InvoiceNo" in filtered_df.columns
):

    revenue_orders = (
        filtered_df
        .groupby(filtered_df["InvoiceDate"].dt.to_period("M"))
        .agg(
            Revenue=("TotalPrice", "sum"),
            Orders=("InvoiceNo", "nunique")
        )
        .reset_index()
    )

    revenue_orders["InvoiceDate"] = (
        revenue_orders["InvoiceDate"].astype(str)
    )

    fig = px.bar(
        revenue_orders,
        x="InvoiceDate",
        y="Revenue",
        color="Revenue",
        text_auto=".2s",
        template="plotly_white"
    )

    fig.add_scatter(
        x=revenue_orders["InvoiceDate"],
        y=revenue_orders["Orders"],
        mode="lines+markers",
        name="Orders",
        yaxis="y2"
    )

    fig.update_layout(
        height=450,
        yaxis_title="Revenue",
        yaxis2=dict(
            title="Orders",
            overlaying="y",
            side="right"
        )
    )

    st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# MONTHLY GROWTH
# ==========================================================

st.markdown("## 📈 Monthly Growth")

if "revenue_orders" in locals():

    growth = revenue_orders.copy()

    growth["Growth %"] = (
        growth["Revenue"].pct_change() * 100
    ).fillna(0)

    fig = px.line(
        growth,
        x="InvoiceDate",
        y="Growth %",
        markers=True,
        text="Growth %",
        template="plotly_white"
    )

    fig.update_traces(
        texttemplate="%{y:.1f}%"
    )

    fig.update_layout(
        height=450
    )

    st.plotly_chart(fig, use_container_width=True)
    # ==========================================================
# TOP PRODUCTS & TOP COUNTRIES
# ==========================================================

left, right = st.columns(2)

with left:

    st.markdown("## 🏆 Top 10 Products")

    if "Description" in filtered_df.columns:

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
            yaxis=dict(categoryorder="total ascending"),
            height=500
        )

        st.plotly_chart(fig, use_container_width=True)

with right:

    st.markdown("## 🌍 Top 10 Countries")

    if "Country" in filtered_df.columns:

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

        fig.update_layout(height=500)

        st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# REVENUE HEATMAP
# ==========================================================

st.markdown("## 🔥 Revenue Heatmap")

if "InvoiceDate" in filtered_df.columns:

    heat = filtered_df.copy()

    heat["Month"] = heat["InvoiceDate"].dt.strftime("%b")
    heat["Weekday"] = heat["InvoiceDate"].dt.day_name()

    month_order = [
        "Jan","Feb","Mar","Apr","May","Jun",
        "Jul","Aug","Sep","Oct","Nov","Dec"
    ]

    weekday_order = [
        "Monday","Tuesday","Wednesday",
        "Thursday","Friday","Saturday","Sunday"
    ]

    heatmap = (
        heat.groupby(["Weekday", "Month"])["TotalPrice"]
        .sum()
        .reset_index()
    )

    heatmap["Month"] = pd.Categorical(
        heatmap["Month"],
        categories=month_order,
        ordered=True
    )

    heatmap["Weekday"] = pd.Categorical(
        heatmap["Weekday"],
        categories=weekday_order,
        ordered=True
    )

    fig = px.density_heatmap(
        heatmap,
        x="Month",
        y="Weekday",
        z="TotalPrice",
        color_continuous_scale="Blues",
        template="plotly_white"
    )

    fig.update_layout(height=500)

    st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# BUSINESS HEALTH SCORE
# ==========================================================

st.markdown("## ❤️ Business Health")

score = 0

score += 30 if total_sales > 500000 else 20
score += 25 if avg_order_value > 250 else 15
score += 25 if total_customers > 3000 else 15
score += 20 if total_products > 100 else 10

st.progress(score / 100)

st.metric(
    "Overall Business Health",
    f"{score}/100"
)

# ==========================================================
# EXECUTIVE SUMMARY
# ==========================================================

st.markdown("## 📋 Executive Summary")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Revenue", f"${total_sales:,.0f}")
c2.metric("Orders", f"{total_orders:,}")
c3.metric("Customers", f"{total_customers:,}")
c4.metric("Avg Order Value", f"${avg_order_value:,.2f}")

# ==========================================================
# AI RECOMMENDATIONS
# ==========================================================

st.markdown("## 🤖 AI Recommendations")

recommendations = []

if avg_order_value < 300:
    recommendations.append(
        "Increase Average Order Value using bundles and cross-selling."
    )
else:
    recommendations.append(
        "Average Order Value is healthy. Maintain the premium product mix."
    )

if total_customers < total_orders:
    recommendations.append(
        "Launch loyalty and retention campaigns for repeat customers."
    )
else:
    recommendations.append(
        "Focus marketing on acquiring new customers."
    )

if "country_sales" in locals() and not country_sales.empty:
    recommendations.append(
        f"Highest revenue market: {country_sales.iloc[0]['Country']}."
    )

if "top_products" in locals() and not top_products.empty:
    recommendations.append(
        f"Ensure inventory availability for '{top_products.iloc[0]['Description']}'."
    )

recommendations.append(
    "Monitor monthly sales trends and investigate any revenue decline."
)

for rec in recommendations:
    st.success("✅ " + rec)

# ==========================================================
# SALES FORECAST
# ==========================================================

st.markdown("## 🔮 Sales Forecast")

if "trend" in locals():

    forecast_df = trend.copy()

    forecast_df["Forecast"] = (
        forecast_df["TotalPrice"]
        .rolling(window=3, min_periods=1)
        .mean()
    )

    fig = px.line(
        forecast_df,
        x="InvoiceDate",
        y=["TotalPrice", "Forecast"],
        markers=True,
        template="plotly_white"
    )

    fig.update_layout(
        height=500,
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# AI INSIGHTS
# ==========================================================

st.markdown("## 🧠 AI Insights")

i1, i2 = st.columns(2)

with i1:
    st.info(
        f"Top {min(10, total_products)} products contribute significantly to total revenue."
    )

with i2:
    st.success(
        f"Average Order Value: ${avg_order_value:,.2f}"
    )

# ==========================================================
# FOOTER
# ==========================================================

st.markdown("---")

st.caption(
    """
RetailPulse AI • Executive Dashboard

Powered by Streamlit • Plotly • Python

© 2026
"""
)