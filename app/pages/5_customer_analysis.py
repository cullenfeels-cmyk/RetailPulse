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
    page_title="Customer Analysis",
    page_icon="👥",
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
<div class="dashboard-title">
👥 Customer Analysis Dashboard
</div>

<div class="dashboard-subtitle">
Customer Lifetime Value • RFM Analysis • Retention Analytics
</div>
""", unsafe_allow_html=True)

# ==========================================================
# DATA PREPARATION
# ==========================================================

# 1. Clean whitespace from all column names
df.columns = df.columns.str.strip()

# 2. Standardize potential variations of column names
column_mapping = {
    "Customer ID": "CustomerID",
    "customer_id": "CustomerID",
    "Customer_ID": "CustomerID",
    "customerid": "CustomerID",
    "Invoice Date": "InvoiceDate",
    "invoice_date": "InvoiceDate",
    "Invoice_Date": "InvoiceDate",
    "Total Price": "TotalPrice",
    "total_price": "TotalPrice",
    "Total_Price": "TotalPrice",
    "Invoice": "InvoiceNo",
    "invoice_no": "InvoiceNo",
    "Invoice_No": "InvoiceNo",
    "invoiceno": "InvoiceNo",
    "Invoice Number": "InvoiceNo",
    "Quantity": "Quantity",
    "quantity": "Quantity",
    "UnitPrice": "UnitPrice",
    "unit_price": "UnitPrice",
    "Unit Price": "UnitPrice",
    "Country": "Country",
    "country": "Country"
}
df = df.rename(columns=column_mapping)

# 3. Handle missing essential columns gracefully
if "CustomerID" not in df.columns:
    st.error("❌ The dataset is missing a 'CustomerID' column. Please check your source file.")
    st.write("Available columns in dataset:", list(df.columns))
    st.stop()

# Fallback for InvoiceNo if missing: create dummy sequential ID per row
if "InvoiceNo" not in df.columns:
    df["InvoiceNo"] = df.index

# Fallback for Quantity if missing
if "Quantity" not in df.columns:
    df["Quantity"] = 1

# Drop rows with null CustomerIDs
df = df[df["CustomerID"].notna()]

if "InvoiceDate" in df.columns:
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

if "TotalPrice" not in df.columns and "Quantity" in df.columns and "UnitPrice" in df.columns:
    df["TotalPrice"] = df["Quantity"] * df["UnitPrice"]
elif "TotalPrice" not in df.columns:
    df["TotalPrice"] = 0.0

# ==========================================================
# FILTERS
# ==========================================================

st.markdown("## 🎛 Customer Filters")

f1, f2, f3 = st.columns(3)

with f1:
    countries = sorted(df["Country"].dropna().unique()) if "Country" in df.columns else []
    selected_country = st.multiselect(
        "🌍 Country",
        countries
    )

with f2:
    if "InvoiceDate" in df.columns and not df["InvoiceDate"].isna().all():
        min_date = df["InvoiceDate"].min().date()
        max_date = df["InvoiceDate"].max().date()
        date_range = st.date_input("📅 Date Range", (min_date, max_date))
        if isinstance(date_range, tuple) and len(date_range) == 2:
            start_date, end_date = date_range
        else:
            start_date, end_date = min_date, max_date
    else:
        start_date, end_date = None, None

with f3:
    max_rev = int(df["TotalPrice"].max()) if not df.empty and df["TotalPrice"].max() > 0 else 100
    min_purchase = st.slider(
        "💰 Minimum Customer Revenue",
        0,
        max_rev,
        0
    )

# ==========================================================
# APPLY FILTERS
# ==========================================================

filtered_df = df.copy()

if selected_country and "Country" in filtered_df.columns:
    filtered_df = filtered_df[
        filtered_df["Country"].isin(selected_country)
    ]

if start_date and end_date and "InvoiceDate" in filtered_df.columns:
    filtered_df = filtered_df[
        (filtered_df["InvoiceDate"] >= pd.to_datetime(start_date)) &
        (filtered_df["InvoiceDate"] <= pd.to_datetime(end_date) + pd.Timedelta(days=1))
    ]

# ==========================================================
# CUSTOMER SUMMARY TABLE
# ==========================================================

customer_summary = (
    filtered_df
    .groupby("CustomerID")
    .agg(
        Revenue=("TotalPrice", "sum"),
        Orders=("InvoiceNo", "nunique"),
        Quantity=("Quantity", "sum"),
        LastPurchase=("InvoiceDate", "max"),
        FirstPurchase=("InvoiceDate", "min")
    )
    .reset_index()
)

customer_summary = customer_summary[
    customer_summary["Revenue"] >= min_purchase
]

customer_summary["Customer Lifetime (Days)"] = (
    customer_summary["LastPurchase"] -
    customer_summary["FirstPurchase"]
).dt.days + 1

customer_summary["Customer Lifetime (Days)"] = (
    customer_summary["Customer Lifetime (Days)"]
    .fillna(1)
    .clip(lower=1)
)

# ==========================================================
# KPI CALCULATIONS
# ==========================================================

total_customers = customer_summary.shape[0]

total_revenue = customer_summary["Revenue"].sum()

total_orders = customer_summary["Orders"].sum()

avg_order_value = (
    total_revenue / total_orders
    if total_orders > 0
    else 0
)

average_customer_value = (
    total_revenue / total_customers
    if total_customers > 0
    else 0
)

repeat_customers = customer_summary[
    customer_summary["Orders"] > 1
].shape[0]

repeat_customer_rate = (
    repeat_customers /
    total_customers * 100
    if total_customers > 0
    else 0
)

average_basket_size = (
    customer_summary["Quantity"].sum() /
    total_orders
    if total_orders > 0
    else 0
)

customer_summary["CLV"] = (
    customer_summary["Revenue"] /
    customer_summary["Customer Lifetime (Days)"]
) * 365

customer_summary["Customer Rank"] = (
    customer_summary["Revenue"]
    .rank(
        ascending=False,
        method="dense"
    )
)

# ==========================================================
# KPI CARDS
# ==========================================================

def metric_card(title, value, color1, color2):
    return f"""
    <div style="
        background:linear-gradient(135deg,{color1},{color2});
        padding:18px;
        border-radius:18px;
        color:white;
        text-align:center;
    ">
        <h4>{title}</h4>
        <h2>{value}</h2>
    </div>
    """

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(
        metric_card(
            "👥 Customers",
            f"{total_customers:,}",
            "#2563eb",
            "#1e3a8a"
        ),
        unsafe_allow_html=True
    )

with k2:
    st.markdown(
        metric_card(
            "💰 Avg CLV",
            f"${customer_summary['CLV'].mean():,.0f}" if not customer_summary.empty else "$0",
            "#059669",
            "#065f46"
        ),
        unsafe_allow_html=True
    )

with k3:
    st.markdown(
        metric_card(
            "🔁 Repeat Rate",
            f"{repeat_customer_rate:.1f}%",
            "#f59e0b",
            "#92400e"
        ),
        unsafe_allow_html=True
    )

with k4:
    st.markdown(
        metric_card(
            "🛒 Basket Size",
            f"{average_basket_size:.1f}",
            "#7c3aed",
            "#581c87"
        ),
        unsafe_allow_html=True
    )

# ==========================================================
# CUSTOMER VALUE ANALYTICS
# ==========================================================

st.markdown("---")
st.header("💎 Customer Value Analytics")

left, right = st.columns(2)

# ==========================================================
# CUSTOMER LIFETIME VALUE
# ==========================================================

with left:
    st.subheader("💰 Customer Lifetime Value (Top 20)")

    top_clv = (
        customer_summary
        .sort_values("CLV", ascending=False)
        .head(20)
    )

    fig = px.bar(
        top_clv,
        x=top_clv["CustomerID"].astype(str),
        y="CLV",
        color="CLV",
        text_auto=".2s",
        color_continuous_scale="Blues",
        template="plotly_white"
    )

    fig.update_layout(
        height=500,
        xaxis_title="Customer",
        yaxis_title="Customer Lifetime Value",
        coloraxis_showscale=False
    )

    st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# REPEAT CUSTOMER RATE
# ==========================================================

with right:
    st.subheader("🔁 Repeat Customer Rate")

    repeat = repeat_customers
    new = total_customers - repeat_customers

    repeat_df = pd.DataFrame({
        "Customer Type": [
            "Repeat",
            "New"
        ],
        "Count": [
            repeat,
            new
        ]
    })

    fig = px.pie(
        repeat_df,
        values="Count",
        names="Customer Type",
        hole=0.60,
        color="Customer Type",
        color_discrete_map={
            "Repeat": "#16a34a",
            "New": "#2563eb"
        },
        template="plotly_white"
    )

    fig.update_layout(height=500)

    st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# AVERAGE BASKET SIZE
# ==========================================================

st.markdown("---")
st.subheader("🛒 Average Basket Size")

basket = (
    filtered_df
    .groupby("InvoiceNo")
    .agg(
        BasketValue=("TotalPrice", "sum"),
        Items=("Quantity", "sum")
    )
    .reset_index()
)

fig = px.scatter(
    basket,
    x="Items",
    y="BasketValue",
    size="BasketValue",
    color="BasketValue",
    color_continuous_scale="Viridis",
    template="plotly_white"
)

fig.update_layout(
    height=500,
    xaxis_title="Items Purchased",
    yaxis_title="Basket Value"
)

st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# CUSTOMER RANKING
# ==========================================================

st.markdown("---")
st.header("🏅 Customer Ranking")

ranking = (
    customer_summary
    .sort_values("Revenue", ascending=False)
    .head(25)
)

fig = px.bar(
    ranking,
    x="Revenue",
    y=ranking["CustomerID"].astype(str),
    orientation="h",
    color="Revenue",
    text_auto=".2s",
    color_continuous_scale="Plasma",
    template="plotly_white"
)

fig.update_layout(
    height=650,
    yaxis=dict(categoryorder="total ascending"),
    xaxis_title="Revenue",
    yaxis_title="Customer ID",
    coloraxis_showscale=False
)

st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# CUSTOMER PERFORMANCE SUMMARY
# ==========================================================

st.markdown("---")
st.subheader("📋 Customer Performance Summary")

c1, c2, c3, c4 = st.columns(4)

highest_clv = customer_summary["CLV"].max() if not customer_summary.empty else 0
median_revenue = customer_summary["Revenue"].median() if not customer_summary.empty else 0
highest_orders = customer_summary["Orders"].max() if not customer_summary.empty else 0
avg_revenue = customer_summary["Revenue"].mean() if not customer_summary.empty else 0

c1.metric(
    "Highest CLV",
    f"${highest_clv:,.0f}"
)

c2.metric(
    "Median Revenue",
    f"${median_revenue:,.0f}"
)

c3.metric(
    "Highest Orders",
    f"{highest_orders:,}"
)

c4.metric(
    "Avg Revenue / Customer",
    f"${avg_revenue:,.0f}"
)

# ==========================================================
# AI CUSTOMER INSIGHTS
# ==========================================================

st.markdown("## 🤖 AI Customer Insights")

if repeat_customer_rate >= 60:
    st.success(
        "Excellent customer loyalty detected. Repeat purchase rate is very strong."
    )
elif repeat_customer_rate >= 40:
    st.info(
        "Customer retention is healthy but has room for improvement."
    )
else:
    st.warning(
        "Low repeat purchase rate detected. Consider loyalty programs."
    )

if average_basket_size >= 20:
    st.success(
        "Customers typically purchase many items per order."
    )
else:
    st.info(
        "Upselling and cross-selling could increase basket size."
    )

if not customer_summary.empty and customer_summary["CLV"].mean() > average_customer_value:
    st.success(
        "Customer Lifetime Value is growing positively."
    )
else:
    st.warning(
        "Increase customer engagement to improve lifetime value."
    )

# ==========================================================
# TOP 20 CUSTOMERS
# ==========================================================

st.markdown("---")
st.header("🏆 Top 20 Customers")

top20 = (
    customer_summary
    .sort_values("Revenue", ascending=False)
    .head(20)
)

show_table = top20[
    [
        "CustomerID",
        "Revenue",
        "Orders",
        "Quantity",
        "CLV",
        "Customer Rank"
    ]
].copy()

show_table["Revenue"] = show_table["Revenue"].round(2)
show_table["CLV"] = show_table["CLV"].round(2)

st.dataframe(
    show_table,
    use_container_width=True,
    hide_index=True
)

# ==========================================================
# TOP 20 CUSTOMER REVENUE
# ==========================================================

fig = px.bar(
    top20,
    x=top20["CustomerID"].astype(str),
    y="Revenue",
    color="Revenue",
    text_auto=".2s",
    template="plotly_white",
    color_continuous_scale="Turbo"
)

fig.update_layout(
    height=500,
    xaxis_title="Customer ID",
    yaxis_title="Revenue",
    coloraxis_showscale=False
)

st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# CUSTOMER SPENDING DISTRIBUTION
# ==========================================================

st.markdown("---")
st.header("💳 Customer Spending Distribution")

left, right = st.columns(2)

with left:
    fig = px.histogram(
        customer_summary,
        x="Revenue",
        nbins=30,
        color_discrete_sequence=["#2563eb"],
        template="plotly_white"
    )

    fig.update_layout(
        height=450,
        xaxis_title="Customer Revenue",
        yaxis_title="Number of Customers"
    )

    st.plotly_chart(fig, use_container_width=True)

with right:
    fig = px.box(
        customer_summary,
        y="Revenue",
        points="outliers",
        template="plotly_white"
    )

    fig.update_layout(
        height=450
    )

    st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# CUSTOMER RETENTION KPIs
# ==========================================================

st.markdown("---")
st.header("📈 Customer Retention KPIs")

active_customers = customer_summary[
    customer_summary["Orders"] > 1
].shape[0]

one_time_customers = customer_summary[
    customer_summary["Orders"] == 1
].shape[0]

retention_rate = (
    active_customers /
    total_customers * 100
    if total_customers > 0 else 0
)

k1, k2, k3 = st.columns(3)

k1.metric(
    "Retention Rate",
    f"{retention_rate:.1f}%"
)

k2.metric(
    "Repeat Customers",
    f"{active_customers:,}"
)

k3.metric(
    "One-Time Customers",
    f"{one_time_customers:,}"
)

retention_df = pd.DataFrame({
    "Type": [
        "Repeat",
        "One-Time"
    ],
    "Customers": [
        active_customers,
        one_time_customers
    ]
})

fig = px.bar(
    retention_df,
    x="Type",
    y="Customers",
    color="Type",
    text_auto=True,
    template="plotly_white"
)

fig.update_layout(height=450)

st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# RFM ANALYSIS
# ==========================================================

st.markdown("---")
st.header("⭐ RFM Analysis")

if not filtered_df.empty:
    snapshot_date = filtered_df["InvoiceDate"].max() + pd.Timedelta(days=1)

    rfm = (
        filtered_df
        .groupby("CustomerID")
        .agg(
            Recency=("InvoiceDate",
                     lambda x: (snapshot_date - x.max()).days),
            Frequency=("InvoiceNo", "nunique"),
            Monetary=("TotalPrice", "sum")
        )
        .reset_index()
    )

    rfm["R"] = pd.qcut(
        rfm["Recency"].rank(method="first"),
        4,
        labels=[4, 3, 2, 1]
    )

    rfm["F"] = pd.qcut(
        rfm["Frequency"].rank(method="first"),
        4,
        labels=[1, 2, 3, 4]
    )

    rfm["M"] = pd.qcut(
        rfm["Monetary"].rank(method="first"),
        4,
        labels=[1, 2, 3, 4]
    )

    rfm["RFM Score"] = (
        rfm["R"].astype(str) +
        rfm["F"].astype(str) +
        rfm["M"].astype(str)
    )

    # ==========================================================
    # RFM SUMMARY TABLE
    # ==========================================================

    st.subheader("📋 RFM Summary")

    st.dataframe(
        rfm.head(20),
        use_container_width=True,
        hide_index=True
    )

    # ==========================================================
    # RFM VISUALIZATION
    # ==========================================================

    fig = px.scatter(
        rfm,
        x="Frequency",
        y="Monetary",
        color="Recency",
        size="Monetary",
        hover_data=["CustomerID", "RFM Score"],
        template="plotly_white",
        color_continuous_scale="Viridis"
    )

    fig.update_layout(
        height=550
    )

    st.plotly_chart(fig, use_container_width=True)

    # ==========================================================
    # RFM SCORE DISTRIBUTION
    # ==========================================================

    score_count = (
        rfm["RFM Score"]
        .value_counts()
        .reset_index()
    )

    score_count.columns = [
        "RFM Score",
        "Customers"
    ]

    fig = px.bar(
        score_count,
        x="RFM Score",
        y="Customers",
        color="Customers",
        template="plotly_white",
        text_auto=True
    )

    fig.update_layout(
        height=450,
        coloraxis_showscale=False
    )

    st.plotly_chart(fig, use_container_width=True)

    # ==========================================================
    # CUSTOMER SEGMENTS
    # ==========================================================

    st.markdown("---")
    st.header("👥 Customer Segments")

    rfm["Segment"] = "Regular"

    rfm.loc[
        (rfm["R"].astype(int) >= 3) &
        (rfm["F"].astype(int) >= 3) &
        (rfm["M"].astype(int) >= 3),
        "Segment"
    ] = "Champions"

    rfm.loc[
        (rfm["R"].astype(int) <= 2) &
        (rfm["F"].astype(int) >= 3),
        "Segment"
    ] = "At Risk"

    rfm.loc[
        (rfm["F"].astype(int) == 1),
        "Segment"
    ] = "New Customers"

    segment_summary = (
        rfm["Segment"]
        .value_counts()
        .reset_index()
    )

    segment_summary.columns = [
        "Segment",
        "Customers"
    ]

    fig = px.pie(
        segment_summary,
        values="Customers",
        names="Segment",
        hole=0.55,
        template="plotly_white"
    )

    fig.update_layout(height=500)

    st.plotly_chart(fig, use_container_width=True)

    # ==========================================================
    # CUSTOMER INSIGHTS
    # ==========================================================

    st.markdown("---")
    st.header("🧠 Customer Insights")

    champions = (
        segment_summary.loc[
            segment_summary["Segment"] == "Champions",
            "Customers"
        ].sum()
    )

    at_risk = (
        segment_summary.loc[
            segment_summary["Segment"] == "At Risk",
            "Customers"
        ].sum()
    )

    new_customers = (
        segment_summary.loc[
            segment_summary["Segment"] == "New Customers",
            "Customers"
        ].sum()
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.success(f"🏆 Champions: {champions}")

    with c2:
        st.warning(f"⚠️ At Risk: {at_risk}")

    with c3:
        st.info(f"🆕 New Customers: {new_customers}")

else:
    st.warning("No data available for RFM Analysis given current filter settings.")
    champions, at_risk, new_customers = 0, 0, 0

# ==========================================================
# EXECUTIVE SUMMARY
# ==========================================================

st.markdown("---")
st.header("📋 Executive Summary")

m1, m2, m3, m4 = st.columns(4)

m1.metric(
    "Customers",
    f"{total_customers:,}"
)

m2.metric(
    "Repeat Rate",
    f"{repeat_customer_rate:.1f}%"
)

m3.metric(
    "Average CLV",
    f"${customer_summary['CLV'].mean():,.2f}" if not customer_summary.empty else "$0.00"
)

m4.metric(
    "Average Basket",
    f"{average_basket_size:.2f}"
)

# ==========================================================
# AI RECOMMENDATIONS
# ==========================================================

st.markdown("---")
st.header("🤖 AI Recommendations")

recommendations = []

if repeat_customer_rate < 50:
    recommendations.append(
        "Launch loyalty programs to improve repeat customer rate."
    )
else:
    recommendations.append(
        "Repeat customer rate is healthy. Maintain loyalty campaigns."
    )

if not customer_summary.empty and customer_summary["CLV"].mean() < customer_summary["Revenue"].mean():
    recommendations.append(
        "Increase Customer Lifetime Value using personalized offers."
    )

if at_risk > champions:
    recommendations.append(
        "Run win-back campaigns for at-risk customers."
    )

recommendations.append(
    "Promote premium products to high-value customers."
)

recommendations.append(
    "Cross-sell products based on customer purchase history."
)

recommendations.append(
    "Reward Champions with exclusive discounts."
)

recommendations.append(
    "Monitor RFM segments every month."
)

for rec in recommendations:
    st.success("✅ " + rec)

# ==========================================================
# AI BUSINESS INSIGHTS
# ==========================================================

st.markdown("---")
st.header("📈 AI Business Insights")

insights = []

if not customer_summary.empty:
    top_customer = customer_summary.sort_values("Revenue", ascending=False).iloc[0]
    insights.append(
        f"Highest spending customer is {top_customer['CustomerID']} with revenue ${top_customer['Revenue']:,.2f}."
    )
    insights.append(
        f"Average customer spends ${customer_summary['Revenue'].mean():,.2f}."
    )
    insights.append(
        f"Average customer lifetime value is ${customer_summary['CLV'].mean():,.2f}."
    )

insights.append(
    f"Repeat purchase rate is {repeat_customer_rate:.1f}%."
)

insights.append(
    f"Average basket size is {average_basket_size:.2f} products."
)

for item in insights:
    st.info(item)

# ==========================================================
# CUSTOMER HEALTH SCORE
# ==========================================================

st.markdown("---")
st.header("❤️ Customer Health Score")

health_score = 0

if repeat_customer_rate >= 60:
    health_score += 30
elif repeat_customer_rate >= 40:
    health_score += 20
else:
    health_score += 10

avg_clv_val = customer_summary["CLV"].mean() if not customer_summary.empty else 0
if avg_clv_val >= 1000:
    health_score += 30
elif avg_clv_val >= 500:
    health_score += 20
else:
    health_score += 10

if champions >= at_risk:
    health_score += 20
else:
    health_score += 10

if average_basket_size >= 10:
    health_score += 20
else:
    health_score += 10

st.progress(health_score / 100)

st.metric(
    "Overall Customer Health",
    f"{health_score}/100"
)

# ==========================================================
# DASHBOARD FOOTER
# ==========================================================

st.markdown("---")

st.caption("""
RetailPulse AI • Customer Analysis Dashboard

Powered by Streamlit • Plotly • Python

© 2026
""")