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
    page_title="Country Insights",
    page_icon="🌍",
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
<div class="dashboard-title">🌍 RetailPulse AI</div>
<div class="dashboard-subtitle">Geographic Sales & Country Performance Analytics</div>
""", unsafe_allow_html=True)

st.header("🌍 Country Insights")

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

if "Country" not in df.columns:
    st.error("❌ The dataset is missing a 'Country' column.")
    st.stop()

# Drop rows missing country data
df = df[df["Country"].notna() & (df["Country"].astype(str).str.strip() != "")]

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

if "InvoiceNo" not in df.columns:
    df["InvoiceNo"] = df.index

# ==========================================================
# FILTERS
# ==========================================================

st.markdown("### 🎛️ Geographic Filters")

f1, f2 = st.columns(2)

with f1:
    countries = sorted(df["Country"].unique())
    selected_country = st.multiselect("🌍 Select Countries (Leave blank for All)", countries)

with f2:
    if "InvoiceDate" in df.columns and not df["InvoiceDate"].isna().all():
        min_date = df["InvoiceDate"].min().date()
        max_date = df["InvoiceDate"].max().date()
        date_range = st.date_input("📅 Date Range", (min_date, max_date))
    else:
        date_range = None

# ==========================================================
# APPLY FILTERS
# ==========================================================

filtered_df = df.copy()

if selected_country:
    filtered_df = filtered_df[filtered_df["Country"].isin(selected_country)]

if date_range and isinstance(date_range, tuple) and len(date_range) == 2:
    filtered_df = filtered_df[
        (filtered_df["InvoiceDate"] >= pd.to_datetime(date_range[0])) &
        (filtered_df["InvoiceDate"] <= pd.to_datetime(date_range[1]) + pd.Timedelta(days=1))
    ]

# ==========================================================
# KPI CALCULATIONS (SCALAR FIX)
# ==========================================================

total_countries = int(filtered_df["Country"].nunique())

revenue_raw = filtered_df["TotalPrice"].sum() if not filtered_df.empty else 0.0
total_revenue = float(revenue_raw.iloc[0] if isinstance(revenue_raw, pd.Series) else revenue_raw)

orders_raw = filtered_df["InvoiceNo"].nunique() if not filtered_df.empty else 0
total_orders = int(orders_raw.iloc[0] if isinstance(orders_raw, pd.Series) else orders_raw)

units_raw = filtered_df["Quantity"].sum() if not filtered_df.empty else 0
total_units = int(units_raw.iloc[0] if isinstance(units_raw, pd.Series) else units_raw)

# ==========================================================
# KPI CARDS
# ==========================================================

def kpi_card(title, value, icon, c1, c2):
    return f'<div style="background:linear-gradient(135deg,{c1},{c2}); padding:22px; border-radius:18px; color:white; text-align:center; box-shadow:0 4px 12px rgba(0,0,0,.15);"><div style="font-size:18px;">{icon} {title}</div><div style="font-size:32px; font-weight:bold; margin-top:10px;">{value}</div></div>'

k1, k2, k3, k4 = st.columns(4)

k1.markdown(kpi_card("Active Markets", f"{total_countries:,}", "🌍", "#2563eb", "#1e3a8a"), unsafe_allow_html=True)
k2.markdown(kpi_card("Global Revenue", f"${total_revenue:,.0f}", "💰", "#16a34a", "#065f46"), unsafe_allow_html=True)
k3.markdown(kpi_card("Total Orders", f"{total_orders:,}", "🧾", "#d97706", "#92400e"), unsafe_allow_html=True)
k4.markdown(kpi_card("Units Exported", f"{total_units:,}", "📦", "#db2777", "#7e22ce"), unsafe_allow_html=True)

# ==========================================================
# COUNTRY AGGREGATION
# ==========================================================

country_summary = (
    filtered_df.groupby("Country")
    .agg(
        Revenue=("TotalPrice", "sum"),
        Orders=("InvoiceNo", "nunique"),
        UnitsSold=("Quantity", "sum")
    )
    .reset_index()
)

country_summary["AvgOrderValue"] = (
    country_summary["Revenue"] / country_summary["Orders"].replace(0, 1)
)

country_summary["RevenueShare"] = (
    (country_summary["Revenue"] / total_revenue * 100) if total_revenue > 0 else 0
)

# ==========================================================
# GLOBAL CHOROPLETH MAP
# ==========================================================

st.markdown("---")
st.header("🗺️ Global Revenue Heatmap")

if not country_summary.empty:
    fig = px.choropleth(
        country_summary,
        locations="Country",
        locationmode="country names",
        color="Revenue",
        hover_name="Country",
        hover_data=["Orders", "UnitsSold", "AvgOrderValue"],
        color_continuous_scale="Blues",
        template="plotly_white"
    )

    fig.update_layout(
        height=550,
        geo=dict(showframe=False, showcoastlines=True, projection_type="natural earth")
    )

    st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# TOP COUNTRIES & REVENUE SHARE
# ==========================================================

st.markdown("---")
left, right = st.columns(2)

with left:
    st.subheader("🏆 Top 10 Countries by Revenue")
    top_countries = country_summary.nlargest(10, "Revenue")

    fig = px.bar(
        top_countries,
        x="Revenue",
        y="Country",
        orientation="h",
        color="Revenue",
        text_auto=".2s",
        color_continuous_scale="Viridis",
        template="plotly_white"
    )
    fig.update_layout(height=450, yaxis=dict(categoryorder="total ascending"))
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("🥧 Geographic Revenue Share")

    fig = px.pie(
        top_countries,
        values="Revenue",
        names="Country",
        hole=0.5,
        template="plotly_white"
    )
    fig.update_layout(height=450)
    st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# COUNTRY PERFORMANCE METRICS TABLE
# ==========================================================

st.markdown("---")
st.header("📋 Detailed Country Performance Breakdown")

display_table = country_summary.sort_values("Revenue", ascending=False).copy()
display_table["Revenue"] = display_table["Revenue"].round(2)
display_table["AvgOrderValue"] = display_table["AvgOrderValue"].round(2)
display_table["RevenueShare"] = display_table["RevenueShare"].round(2)

st.dataframe(
    display_table,
    use_container_width=True,
    hide_index=True
)

# ==========================================================
# COUNTRY MARKET DIVERSITY SCORE
# ==========================================================

st.markdown("---")
st.header("❤️ Market Concentration & Diversity Score")

diversity_score = 0

top_market_share = top_countries.iloc[0]["RevenueShare"] if not top_countries.empty else 100

if top_market_share < 50:
    diversity_score += 40  # Well balanced global sales
elif top_market_share < 75:
    diversity_score += 25
else:
    diversity_score += 10  # Heavily dependent on single country

if total_countries > 20:
    diversity_score += 30
elif total_countries > 10:
    diversity_score += 20
else:
    diversity_score += 10

if total_orders > 1000:
    diversity_score += 30
else:
    diversity_score += 15

st.progress(diversity_score / 100)
st.metric("Geographic Diversification Score", f"{diversity_score}/100")

# ==========================================================
# AI GEOGRAPHIC INSIGHTS
# ==========================================================

st.markdown("---")
st.header("🤖 AI Geographic Insights")

recs = []

if not top_countries.empty:
    primary_market = top_countries.iloc[0]["Country"]
    recs.append(f"Primary Revenue Source: **{primary_market}** generates **{top_market_share:.1f}%** of total sales.")

if top_market_share > 70:
    recs.append("High market dependence detected! Consider expanding targeted ad campaigns in secondary international markets.")

if total_countries > 10:
    recs.append(f"Active international presence confirmed across **{total_countries}** different countries.")

for r in recs:
    st.info("💡 " + r)

# ==========================================================
# FOOTER
# ==========================================================

st.markdown("---")
st.caption("""
RetailPulse AI • Country Insights Dashboard

Powered by Streamlit • Plotly • Python

© 2026
""")