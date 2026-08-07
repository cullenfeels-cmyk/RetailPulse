import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from styles import load_css
from utils import load_data

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Product Analytics",
    page_icon="📦",
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
<div class="dashboard-title">📦 RetailPulse AI</div>
<div class="dashboard-subtitle">Product Performance & Portfolio Analytics</div>
""", unsafe_allow_html=True)

st.header("📦 Product Analytics")

# ==========================================================
# DATA PREPARATION & COLUMN STANDARDIZATION
# ==========================================================

# 1. Clean whitespace from all column names
df.columns = df.columns.str.strip()

# 2. Comprehensive column mapping for all possible name variations
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
    "Unit_Price": "UnitPrice",
    "Price": "UnitPrice",
    "price": "UnitPrice",
    "Quantity": "Quantity",
    "quantity": "Quantity",
    "Description": "Description",
    "description": "Description",
    "Product": "Description",
    "product": "Description",
    "StockCode": "StockCode",
    "stock_code": "StockCode",
    "Stock Code": "StockCode",
    "Country": "Country",
    "country": "Country"
}
df = df.rename(columns=column_mapping)

# 3. Handle missing essential columns with safe fallbacks
if "Description" not in df.columns:
    st.error("❌ Dataset missing product 'Description' column.")
    st.stop()

# Drop missing/blank descriptions
df = df[df["Description"].notna() & (df["Description"].astype(str).str.strip() != "")]

if "InvoiceDate" in df.columns:
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

if "Quantity" not in df.columns:
    df["Quantity"] = 1

if "UnitPrice" not in df.columns and "TotalPrice" in df.columns and "Quantity" in df.columns:
    df["UnitPrice"] = df["TotalPrice"] / df["Quantity"].replace(0, 1)
elif "UnitPrice" not in df.columns:
    df["UnitPrice"] = 0.0

if "TotalPrice" not in df.columns and "Quantity" in df.columns and "UnitPrice" in df.columns:
    df["TotalPrice"] = df["Quantity"] * df["UnitPrice"]
elif "TotalPrice" not in df.columns:
    df["TotalPrice"] = 0.0

# ==========================================================
# FILTERS
# ==========================================================

st.markdown("### 🎛️ Product Filters")

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
    all_products = sorted(df["Description"].astype(str).unique())
    selected_products = st.multiselect("📦 Select Specific Products (Optional)", all_products)

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

if selected_products:
    filtered_df = filtered_df[filtered_df["Description"].isin(selected_products)]

# ==========================================================
# KPI CALCULATIONS (SCALAR CONVERSION FIX)
# ==========================================================

total_products = int(filtered_df["Description"].nunique())

units_raw = filtered_df["Quantity"].sum() if not filtered_df.empty else 0
total_units_sold = int(units_raw.iloc[0] if isinstance(units_raw, pd.Series) else units_raw)

revenue_raw = filtered_df["TotalPrice"].sum() if not filtered_df.empty else 0.0
total_product_revenue = float(revenue_raw.iloc[0] if isinstance(revenue_raw, pd.Series) else revenue_raw)

price_raw = filtered_df["UnitPrice"].mean() if not filtered_df.empty else 0.0
avg_price = float(price_raw.iloc[0] if isinstance(price_raw, pd.Series) else price_raw)

# ==========================================================
# KPI CARDS
# ==========================================================

def kpi_card(title, value, icon, c1, c2):
    return f'<div style="background:linear-gradient(135deg,{c1},{c2}); padding:22px; border-radius:18px; color:white; text-align:center; box-shadow:0 4px 12px rgba(0,0,0,.15);"><div style="font-size:18px;">{icon} {title}</div><div style="font-size:32px; font-weight:bold; margin-top:10px;">{value}</div></div>'

k1, k2, k3, k4 = st.columns(4)

k1.markdown(kpi_card("Total Products", f"{total_products:,}", "📦", "#2563eb", "#1e3a8a"), unsafe_allow_html=True)
k2.markdown(kpi_card("Units Sold", f"{total_units_sold:,}", "🛒", "#16a34a", "#065f46"), unsafe_allow_html=True)
k3.markdown(kpi_card("Product Revenue", f"${total_product_revenue:,.0f}", "💰", "#d97706", "#92400e"), unsafe_allow_html=True)
k4.markdown(kpi_card("Avg Unit Price", f"${avg_price:,.2f}", "🏷️", "#db2777", "#7e22ce"), unsafe_allow_html=True)

# ==========================================================
# PRODUCT SUMMARY AGGREGATION
# ==========================================================

product_summary = (
    filtered_df.groupby("Description")
    .agg(
        Revenue=("TotalPrice", "sum"),
        UnitsSold=("Quantity", "sum"),
        AvgPrice=("UnitPrice", "mean")
    )
    .reset_index()
)

# ==========================================================
# TOP PERFORMING PRODUCTS
# ==========================================================

st.markdown("---")
left, right = st.columns(2)

with left:
    st.subheader("🏆 Top 10 Revenue Generating Products")
    top_10 = product_summary.nlargest(10, "Revenue")
    
    fig = px.bar(
        top_10,
        x="Revenue",
        y="Description",
        orientation="h",
        color="Revenue",
        text_auto=".2s",
        color_continuous_scale="Viridis",
        template="plotly_white"
    )
    fig.update_layout(height=450, yaxis=dict(categoryorder="total ascending"))
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("📦 Top 10 Products by Volume (Units)")
    top_10_units = product_summary.nlargest(10, "UnitsSold")
    
    fig = px.bar(
        top_10_units,
        x="UnitsSold",
        y="Description",
        orientation="h",
        color="UnitsSold",
        text_auto=".2s",
        color_continuous_scale="Plasma",
        template="plotly_white"
    )
    fig.update_layout(height=450, yaxis=dict(categoryorder="total ascending"))
    st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# PARETO ANALYSIS (80/20 RULE)
# ==========================================================

st.markdown("---")
st.header("⚖️ Pareto Revenue Analysis (80/20 Rule)")

if not product_summary.empty and total_product_revenue > 0:
    pareto_df = product_summary.sort_values("Revenue", ascending=False).copy()
    pareto_df["CumulativeRevenue"] = pareto_df["Revenue"].cumsum()
    pareto_df["CumulativePercentage"] = (pareto_df["CumulativeRevenue"] / total_product_revenue) * 100
    pareto_df["ProductRank"] = range(1, len(pareto_df) + 1)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=pareto_df["ProductRank"],
        y=pareto_df["Revenue"],
        name="Revenue",
        marker_color="#2563eb"
    ))

    fig.add_trace(go.Scatter(
        x=pareto_df["ProductRank"],
        y=pareto_df["CumulativePercentage"],
        name="Cumulative Revenue %",
        yaxis="y2",
        line=dict(color="#dc2626", width=3)
    ))

    fig.update_layout(
        height=500,
        template="plotly_white",
        xaxis_title="Product Rank",
        yaxis=dict(title="Revenue ($)"),
        yaxis2=dict(title="Cumulative Revenue %", overlaying="y", side="right", range=[0, 105]),
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)

    top_20_percent_count = max(1, int(len(pareto_df) * 0.2))
    top_20_revenue_share = float((pareto_df.head(top_20_percent_count)["Revenue"].sum() / total_product_revenue) * 100)

    st.info(f"💡 **Pareto Insight:** The top **20%** of products ({top_20_percent_count:,} items) generate **{top_20_revenue_share:.1f}%** of total revenue.")
else:
    top_20_revenue_share = 0.0
    st.warning("No revenue data available for Pareto analysis under current filters.")

# ==========================================================
# PRICE VS VOLUME ANALYSIS
# ==========================================================

st.markdown("---")
st.header("🎯 Price vs. Volume Matrix")

if not product_summary.empty:
    fig = px.scatter(
        product_summary,
        x="AvgPrice",
        y="UnitsSold",
        size="Revenue",
        color="Revenue",
        hover_name="Description",
        log_x=True,
        log_y=True,
        template="plotly_white",
        color_continuous_scale="Turbo"
    )

    fig.update_layout(
        height=500,
        xaxis_title="Avg Price ($ - Log Scale)",
        yaxis_title="Units Sold (Log Scale)"
    )

    st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# PRODUCT HEALTH SCORE
# ==========================================================

st.markdown("---")
st.header("❤️ Product Portfolio Health Score")

health_score = 0

if top_20_revenue_share <= 85:
    health_score += 30
else:
    health_score += 15

if total_products > 500:
    health_score += 25
elif total_products > 100:
    health_score += 20
else:
    health_score += 10

if total_units_sold > 50000:
    health_score += 25
else:
    health_score += 15

if avg_price > 5:
    health_score += 20
else:
    health_score += 10

st.progress(health_score / 100)
st.metric("Product Portfolio Health Score", f"{health_score}/100")

# ==========================================================
# AI PRODUCT RECOMMENDATIONS
# ==========================================================

st.markdown("---")
st.header("🤖 AI Product Recommendations")

recs = []

if top_20_revenue_share > 80:
    recs.append("High revenue concentration detected. Diversify catalog marketing to support mid-tier products.")
else:
    recs.append("Balanced portfolio distribution across revenue classes.")

low_performers = product_summary[product_summary["Revenue"] < 100].shape[0] if not product_summary.empty else 0
if low_performers > 0:
    recs.append(f"Review or clear inventory for {low_performers} underperforming products generating < $100 in revenue.")

best_seller = top_10.iloc[0]["Description"] if not product_summary.empty and not top_10.empty else "N/A"
recs.append(f"Ensure priority supply chain fulfillment for primary revenue driver: '{best_seller}'.")

for r in recs:
    st.success("✅ " + r)

# ==========================================================
# FOOTER
# ==========================================================

st.markdown("---")
st.caption("""
RetailPulse AI • Product Analytics Dashboard

Powered by Streamlit • Plotly • Python

© 2026
""")