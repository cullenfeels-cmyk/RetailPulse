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
    page_title="Advanced Time Analytics",
    page_icon="⏰",
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
<div class="dashboard-title">⏰ RetailPulse AI</div>
<div class="dashboard-subtitle">Advanced Time Series, Hourly Peaks & Temporal Behavior Analytics</div>
""", unsafe_allow_html=True)

st.header("⏰ Advanced Time Analytics")

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
    "Quantity": "Quantity",
    "quantity": "Quantity",
    "Country": "Country",
    "country": "Country",
    "Invoice": "InvoiceNo",
    "InvoiceNo": "InvoiceNo",
    "invoice_no": "InvoiceNo"
}
df = df.rename(columns=column_mapping)

# 3. CRITICAL FIX: Remove duplicate columns if multiple source columns mapped to the same name
df = df.loc[:, ~df.columns.duplicated(keep='first')].copy()

if "InvoiceDate" not in df.columns:
    st.error("❌ Dataset missing 'InvoiceDate' column.")
    st.stop()

df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

if "Quantity" not in df.columns:
    df["Quantity"] = 1

if "TotalPrice" not in df.columns and "Quantity" in df.columns and "UnitPrice" in df.columns:
    df["TotalPrice"] = df["Quantity"] * df["UnitPrice"]
elif "TotalPrice" not in df.columns:
    df["TotalPrice"] = 0.0

if "InvoiceNo" not in df.columns:
    df["InvoiceNo"] = df.index

# ==========================================================
# EXTRACT TEMPORAL FEATURES
# ==========================================================

df["Year"] = df["InvoiceDate"].dt.year
df["Quarter"] = "Q" + df["InvoiceDate"].dt.quarter.astype(str)
df["Month"] = df["InvoiceDate"].dt.strftime("%b")
df["MonthNum"] = df["InvoiceDate"].dt.month
df["DayOfWeek"] = df["InvoiceDate"].dt.day_name()
df["Hour"] = df["InvoiceDate"].dt.hour

month_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# ==========================================================
# FILTERS
# ==========================================================

st.markdown("### 🎛️ Temporal Filters")

f1, f2, f3 = st.columns(3)

with f1:
    available_years = sorted(df["Year"].dropna().unique())
    selected_years = st.multiselect("📅 Select Years", available_years, default=available_years)

with f2:
    countries = sorted(df["Country"].dropna().unique()) if "Country" in df.columns else []
    selected_country = st.multiselect("🌍 Country", countries)

with f3:
    time_granularity = st.selectbox("📊 Trend Granularity", ["Daily", "Weekly", "Monthly"])

# ==========================================================
# APPLY FILTERS
# ==========================================================

filtered_df = df.copy()

if selected_years:
    filtered_df = filtered_df[filtered_df["Year"].isin(selected_years)]

if selected_country and "Country" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["Country"].isin(selected_country)]

# Ensure unique columns in filtered DataFrame as well
filtered_df = filtered_df.loc[:, ~filtered_df.columns.duplicated(keep='first')].copy()

# ==========================================================
# KPI CALCULATIONS (SAFE SCALAR CONVERSIONS)
# ==========================================================

revenue_raw = filtered_df["TotalPrice"].sum() if not filtered_df.empty else 0.0
total_revenue = float(revenue_raw.iloc[0] if isinstance(revenue_raw, pd.Series) else revenue_raw)

orders_raw = filtered_df["InvoiceNo"].nunique() if not filtered_df.empty else 0
total_orders = int(orders_raw.iloc[0] if isinstance(orders_raw, pd.Series) else orders_raw)

if not filtered_df.empty and filtered_df["InvoiceDate"].max() > filtered_df["InvoiceDate"].min():
    total_days = max(1, (filtered_df["InvoiceDate"].max() - filtered_df["InvoiceDate"].min()).days)
else:
    total_days = 1

daily_avg_revenue = total_revenue / total_days
daily_avg_orders = total_orders / total_days

# Safe Peak Hour extraction
if not filtered_df.empty:
    hourly_agg = filtered_df.groupby("Hour")["TotalPrice"].sum()
    peak_raw = hourly_agg.idxmax()
    peak_hour_val = int(peak_raw.iloc[0] if isinstance(peak_raw, pd.Series) else peak_raw)
    peak_hour_str = f"{peak_hour_val:02d}:00"
else:
    peak_hour_str = "00:00"

# Safe Peak Day extraction
if not filtered_df.empty:
    daily_agg = filtered_df.groupby("DayOfWeek", observed=False)["TotalPrice"].sum()
    peak_day_raw = daily_agg.idxmax()
    peak_day_str = str(peak_day_raw.iloc[0] if isinstance(peak_day_raw, pd.Series) else peak_day_raw)
else:
    peak_day_str = "N/A"

# ==========================================================
# KPI CARDS
# ==========================================================

def kpi_card(title, value, icon, c1, c2):
    return f'<div style="background:linear-gradient(135deg,{c1},{c2}); padding:22px; border-radius:18px; color:white; text-align:center; box-shadow:0 4px 12px rgba(0,0,0,.15);"><div style="font-size:18px;">{icon} {title}</div><div style="font-size:32px; font-weight:bold; margin-top:10px;">{value}</div></div>'

k1, k2, k3, k4 = st.columns(4)

k1.markdown(kpi_card("Daily Avg Revenue", f"${daily_avg_revenue:,.0f}", "💵", "#2563eb", "#1e3a8a"), unsafe_allow_html=True)
k2.markdown(kpi_card("Daily Avg Orders", f"{daily_avg_orders:,.1f}", "🧾", "#16a34a", "#065f46"), unsafe_allow_html=True)
k3.markdown(kpi_card("Peak Shopping Hour", peak_hour_str, "⏰", "#d97706", "#92400e"), unsafe_allow_html=True)
k4.markdown(kpi_card("Peak Shopping Day", peak_day_str, "📅", "#db2777", "#7e22ce"), unsafe_allow_html=True)

# ==========================================================
# ADVANCED RESAMPLED TIME SERIES TREND
# ==========================================================

st.markdown("---")
st.header("📈 Time Series Sales Trend & Rolling Average")

if not filtered_df.empty:
    price_series = filtered_df[["InvoiceDate", "TotalPrice"]].copy()
    if isinstance(price_series["TotalPrice"], pd.DataFrame):
        price_series = price_series.iloc[:, [0, 1]]
        price_series.columns = ["InvoiceDate", "TotalPrice"]

    ts_df = price_series.set_index("InvoiceDate")
    
    if time_granularity == "Daily":
        resampled = ts_df["TotalPrice"].resample("D").sum().reset_index()
        x_col = "InvoiceDate"
        window = 7
    elif time_granularity == "Weekly":
        resampled = ts_df["TotalPrice"].resample("W").sum().reset_index()
        x_col = "InvoiceDate"
        window = 4
    else:
        resampled = ts_df["TotalPrice"].resample("ME").sum().reset_index()
        x_col = "InvoiceDate"
        window = 3

    total_price_series = resampled["TotalPrice"].squeeze()
    if isinstance(total_price_series, pd.DataFrame):
        total_price_series = total_price_series.iloc[:, 0]

    resampled["RollingAvg"] = total_price_series.rolling(window=window, min_periods=1).mean()

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=resampled[x_col],
        y=resampled["TotalPrice"],
        mode="lines",
        name="Actual Revenue",
        line=dict(color="#2563eb", width=1.5),
        opacity=0.6
    ))

    fig.add_trace(go.Scatter(
        x=resampled[x_col],
        y=resampled["RollingAvg"],
        mode="lines",
        name=f"{window}-{time_granularity[:1]} Rolling Average",
        line=dict(color="#16a34a", width=3)
    ))

    fig.update_layout(
        height=450,
        template="plotly_white",
        xaxis_title="Date",
        yaxis_title="Revenue ($)",
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# HOURLY & DAY OF WEEK INTRA-DAY DYNAMICS
# ==========================================================

st.markdown("---")
left, right = st.columns(2)

with left:
    st.subheader("⏰ Revenue & Order Volume by Hour of Day")
    
    hourly_df = (
        filtered_df.groupby("Hour")
        .agg(Revenue=("TotalPrice", "sum"), Orders=("InvoiceNo", "nunique"))
        .reset_index()
    )

    fig = px.bar(
        hourly_df,
        x="Hour",
        y="Revenue",
        color="Revenue",
        text_auto=".2s",
        color_continuous_scale="Blues",
        template="plotly_white"
    )
    fig.update_layout(height=450, xaxis=dict(tickmode="linear", tick0=0, dtick=1))
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("📅 Sales Distribution by Day of Week")
    
    dow_df = (
        filtered_df.groupby("DayOfWeek", observed=False)
        .agg(Revenue=("TotalPrice", "sum"), Orders=("InvoiceNo", "nunique"))
        .reset_index()
    )
    
    dow_df["DayOfWeek"] = pd.Categorical(dow_df["DayOfWeek"], categories=weekday_order, ordered=True)
    dow_df = dow_df.sort_values("DayOfWeek")

    fig = px.bar(
        dow_df,
        x="DayOfWeek",
        y="Revenue",
        color="Revenue",
        text_auto=".2s",
        color_continuous_scale="Teal",
        template="plotly_white"
    )
    fig.update_layout(height=450)
    st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# HEATMAP: HOUR OF DAY VS DAY OF WEEK
# ==========================================================

st.markdown("---")
st.header("🔥 Peak Activity Matrix (Hour x Day of Week)")

if not filtered_df.empty:
    matrix_df = (
        filtered_df.groupby(["DayOfWeek", "Hour"], observed=False)["TotalPrice"]
        .sum()
        .reset_index()
    )
    
    # Ensure column names in matrix_df are clean and unique before plotting
    matrix_df = matrix_df.loc[:, ~matrix_df.columns.duplicated(keep='first')].copy()

    matrix_df["DayOfWeek"] = pd.Categorical(matrix_df["DayOfWeek"], categories=weekday_order, ordered=True)
    matrix_df = matrix_df.sort_values(["DayOfWeek", "Hour"])

    fig = px.density_heatmap(
        matrix_df,
        x="Hour",
        y="DayOfWeek",
        z="TotalPrice",
        color_continuous_scale="Viridis",
        template="plotly_white",
        labels={"TotalPrice": "Revenue ($)"}
    )

    fig.update_layout(
        height=480,
        xaxis=dict(tickmode="linear", tick0=0, dtick=1),
        yaxis_title="Day of Week",
        xaxis_title="Hour of Day"
    )

    st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# YEAR-OVER-YEAR (YoY) MONTHLY COMPARISON
# ==========================================================

st.markdown("---")
st.header("📊 Year-over-Year (YoY) Monthly Comparison")

if len(available_years) > 1:
    yoy_df = (
        filtered_df.groupby(["Year", "Month", "MonthNum"], observed=False)["TotalPrice"]
        .sum()
        .reset_index()
    )
    
    yoy_df = yoy_df.loc[:, ~yoy_df.columns.duplicated(keep='first')].copy()
    yoy_df["Month"] = pd.Categorical(yoy_df["Month"], categories=month_order, ordered=True)
    yoy_df = yoy_df.sort_values(["MonthNum", "Year"])

    fig = px.line(
        yoy_df,
        x="Month",
        y="TotalPrice",
        color=yoy_df["Year"].astype(str),
        markers=True,
        template="plotly_white",
        labels={"color": "Year", "TotalPrice": "Revenue ($)"}
    )

    fig.update_layout(height=480, hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("ℹ️ Load multi-year data to enable Year-over-Year comparison curves.")

# ==========================================================
# AI TEMPORAL INSIGHTS
# ==========================================================

st.markdown("---")
st.header("🤖 AI Operational Insights")

insights = []

insights.append(f"Peak transactional traffic occurs around **{peak_hour_str}**. Schedule server maintenance and marketing deployments outside this window.")
insights.append(f"**{peak_day_str}** generates highest weekly order revenue.")

if not hourly_df.empty:
    min_row = hourly_df.loc[hourly_df["Revenue"].idxmin()]["Hour"]
    off_peak_val = int(min_row.iloc[0] if isinstance(min_row, pd.Series) else min_row)
    insights.append(f"Lowest purchasing activity observed at hour **{off_peak_val:02d}:00**. Ideal for background data processing.")

for ins in insights:
    st.info("💡 " + ins)

# ==========================================================
# FOOTER
# ==========================================================

st.markdown("---")
st.caption("""
RetailPulse AI • Advanced Time Analytics Dashboard

Powered by Streamlit • Plotly • Python

© 2026
""")