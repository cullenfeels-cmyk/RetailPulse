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
    page_title="Inventory Risk Analytics",
    page_icon="⚠️",
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
<div class="dashboard-title">⚠️ RetailPulse AI</div>
<div class="dashboard-subtitle">High-Tech Inventory Risk, Stockout Forecasting & Capital Optimization</div>
""", unsafe_allow_html=True)

st.header("⚠️ Inventory Risk & Stock Analytics")

# ==========================================================
# DATA PREPARATION & COLUMN STANDARDIZATION
# ==========================================================

# 1. Clean whitespace from all column names
df.columns = df.columns.str.strip()

# 2. Comprehensive column mapping
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
    "Product": "Description",
    "StockCode": "StockCode",
    "stock_code": "StockCode",
    "Stock Code": "StockCode",
    "Country": "Country",
    "country": "Country"
}
df = df.rename(columns=column_mapping)

# Remove duplicate column names
df = df.loc[:, ~df.columns.duplicated(keep='first')].copy()

if "Description" not in df.columns:
    st.error("❌ Dataset missing product 'Description' column.")
    st.stop()

# Clean null/blank descriptions
df = df[df["Description"].notna() & (df["Description"].astype(str).str.strip() != "")]

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

# ==========================================================
# CONTROLS & PARAMETER SIMULATION
# ==========================================================

st.markdown("### 🎛️ Inventory Risk Control Panel")

c1, c2, c3, c4 = st.columns(4)

with c1:
    lead_time_days = st.number_input("📦 Supplier Lead Time (Days)", min_value=1, max_value=60, value=14, step=1)

with c2:
    safety_stock_days = st.number_input("🛡️ Safety Stock Cushion (Days)", min_value=1, max_value=30, value=7, step=1)

with c3:
    overstock_threshold_days = st.number_input("⚠️ Overstock Threshold (Days)", min_value=30, max_value=180, value=90, step=5)

with c4:
    simulated_stock_multiplier = st.slider("📊 Simulated On-Hand Multiplier", min_value=0.2, max_value=3.0, value=1.0, step=0.1, help="Simulates inventory levels relative to historical sales velocity.")

# ==========================================================
# INVENTORY RISK MODELING ENGINE
# ==========================================================

# Determine timeframe spanned by dataset
if "InvoiceDate" in df.columns and not df["InvoiceDate"].isna().all():
    total_days = max(1, (df["InvoiceDate"].max() - df["InvoiceDate"].min()).days)
else:
    total_days = 90

# Calculate sales velocity per product
inventory_df = (
    df.groupby("Description")
    .agg(
        TotalQuantitySold=("Quantity", "sum"),
        TotalRevenue=("TotalPrice", "sum"),
        AvgUnitPrice=("UnitPrice", "mean")
    )
    .reset_index()
)

# Remove non-positive quantity artifacts
inventory_df = inventory_df[inventory_df["TotalQuantitySold"] > 0]

# Compute Daily Velocity & Current Stock Estimation
inventory_df["DailyBurnRate"] = inventory_df["TotalQuantitySold"] / total_days

# Estimate Simulated On-Hand Inventory (using historical velocity * standard turnover buffer)
inventory_df["SimulatedOnHandStock"] = (inventory_df["DailyBurnRate"] * 45 * simulated_stock_multiplier).round().astype(int)

# Calculate Days of Inventory Remaining (DIR)
inventory_df["DaysOfInventoryRemaining"] = np.where(
    inventory_df["DailyBurnRate"] > 0,
    inventory_df["SimulatedOnHandStock"] / inventory_df["DailyBurnRate"],
    999
)

# Risk Threshold Boundaries
reorder_point_days = lead_time_days + safety_stock_days

def classify_risk(row):
    dir_val = row["DaysOfInventoryRemaining"]
    burn = row["DailyBurnRate"]
    
    if burn == 0:
        return "Dead Stock"
    elif dir_val <= reorder_point_days:
        return "Critical Stockout Risk"
    elif dir_val >= overstock_threshold_days:
        return "Overstocked / Capital Locked"
    else:
        return "Healthy / Optimal Stock"

inventory_df["RiskCategory"] = inventory_df.apply(classify_risk, axis=1)

# Calculate Reorder Recommendations
inventory_df["SuggestedReorderQty"] = np.where(
    inventory_df["DaysOfInventoryRemaining"] <= reorder_point_days,
    ((reorder_point_days + 30) * inventory_df["DailyBurnRate"] - inventory_df["SimulatedOnHandStock"]).clip(lower=0).round(),
    0
)

inventory_df["CapitalAtRisk"] = (inventory_df["SimulatedOnHandStock"] * inventory_df["AvgUnitPrice"]).round(2)

# Ensure unique column names
inventory_df = inventory_df.loc[:, ~inventory_df.columns.duplicated(keep='first')].copy()

# ==========================================================
# KPI CALCULATIONS (SAFE SCALARS)
# ==========================================================

total_skus = int(inventory_df["Description"].nunique())

critical_skus_raw = inventory_df[inventory_df["RiskCategory"] == "Critical Stockout Risk"].shape[0]
critical_skus = int(critical_skus_raw)

overstocked_skus_raw = inventory_df[inventory_df["RiskCategory"] == "Overstocked / Capital Locked"].shape[0]
overstocked_skus = int(overstocked_skus_raw)

locked_capital_raw = inventory_df[inventory_df["RiskCategory"] == "Overstocked / Capital Locked"]["CapitalAtRisk"].sum()
locked_capital = float(locked_capital_raw.iloc[0] if isinstance(locked_capital_raw, pd.Series) else locked_capital_raw)

# ==========================================================
# KPI CARDS
# ==========================================================

def kpi_card(title, value, icon, c1, c2):
    return f'<div style="background:linear-gradient(135deg,{c1},{c2}); padding:22px; border-radius:18px; color:white; text-align:center; box-shadow:0 4px 12px rgba(0,0,0,.15);"><div style="font-size:18px;">{icon} {title}</div><div style="font-size:32px; font-weight:bold; margin-top:10px;">{value}</div></div>'

k1, k2, k3, k4 = st.columns(4)

k1.markdown(kpi_card("Total Active SKUs", f"{total_skus:,}", "📦", "#2563eb", "#1e3a8a"), unsafe_allow_html=True)
k2.markdown(kpi_card("Critical Stockouts", f"{critical_skus:,}", "🚨", "#dc2626", "#991b1b"), unsafe_allow_html=True)
k3.markdown(kpi_card("Overstocked SKUs", f"{overstocked_skus:,}", "⚠️", "#d97706", "#92400e"), unsafe_allow_html=True)
k4.markdown(kpi_card("Capital At Risk", f"${locked_capital:,.0f}", "💵", "#7c3aed", "#4c1d95"), unsafe_allow_html=True)

# ==========================================================
# RISK CATEGORY BREAKDOWN & DISTRIBUTION
# ==========================================================

st.markdown("---")
left, right = st.columns(2)

with left:
    st.subheader("📊 Inventory Risk Category Breakdown")
    
    risk_counts = inventory_df["RiskCategory"].value_counts().reset_index()
    risk_counts.columns = ["RiskCategory", "Count"]

    color_map = {
        "Critical Stockout Risk": "#dc2626",
        "Overstocked / Capital Locked": "#f59e0b",
        "Healthy / Optimal Stock": "#16a34a",
        "Dead Stock": "#6b7280"
    }

    fig = px.pie(
        risk_counts,
        values="Count",
        names="RiskCategory",
        hole=0.55,
        color="RiskCategory",
        color_discrete_map=color_map,
        template="plotly_white"
    )
    fig.update_layout(height=450)
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("💰 Capital Allocation by Risk Status")
    
    capital_by_risk = inventory_df.groupby("RiskCategory", observed=False)["CapitalAtRisk"].sum().reset_index()

    fig = px.bar(
        capital_by_risk,
        x="RiskCategory",
        y="CapitalAtRisk",
        color="RiskCategory",
        color_discrete_map=color_map,
        text_auto=".2s",
        template="plotly_white"
    )
    fig.update_layout(
        height=450,
        xaxis_title="",
        yaxis_title="Capital Bound ($)",
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# INVENTORY HEALTH MATRIX (BURN RATE VS DAYS REMAINING)
# ==========================================================

st.markdown("---")
st.header("🎯 Inventory Health Matrix (Sales Velocity vs. Stock Coverage)")

fig = px.scatter(
    inventory_df,
    x="DailyBurnRate",
    y="DaysOfInventoryRemaining",
    size="CapitalAtRisk",
    color="RiskCategory",
    color_discrete_map=color_map,
    hover_name="Description",
    log_x=True,
    log_y=True,
    template="plotly_white"
)

# Add critical reorder threshold reference line
fig.add_hline(y=reorder_point_days, line_dash="dash", line_color="#dc2626", annotation_text=f"Reorder Line ({reorder_point_days} Days)")
fig.add_hline(y=overstock_threshold_days, line_dash="dash", line_color="#f59e0b", annotation_text=f"Overstock Line ({overstock_threshold_days} Days)")

fig.update_layout(
    height=520,
    xaxis_title="Daily Sales Velocity (Units/Day - Log Scale)",
    yaxis_title="Days of Inventory Remaining (DIR - Log Scale)"
)

st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# CRITICAL REORDER ACTION TABLE
# ==========================================================

st.markdown("---")
st.header("🚨 Priority Action Required: Stockout Risk Table")

critical_table = (
    inventory_df[inventory_df["RiskCategory"] == "Critical Stockout Risk"]
    .sort_values("DaysOfInventoryRemaining", ascending=True)
    .copy()
)

if not critical_table.empty:
    display_critical = critical_table[
        [
            "Description",
            "DailyBurnRate",
            "SimulatedOnHandStock",
            "DaysOfInventoryRemaining",
            "SuggestedReorderQty",
            "CapitalAtRisk"
        ]
    ].copy()

    display_critical["DailyBurnRate"] = display_critical["DailyBurnRate"].round(2)
    display_critical["DaysOfInventoryRemaining"] = display_critical["DaysOfInventoryRemaining"].round(1)

    st.dataframe(
        display_critical,
        use_container_width=True,
        hide_index=True
    )
else:
    st.success("✅ No SKUs currently at immediate risk of stockout under selected lead time parameters.")

# ==========================================================
# AI INVENTORY OPTIMIZATION RECOMMENDATIONS
# ==========================================================

st.markdown("---")
st.header("🤖 AI Supply Chain Recommendations")

recs = []

if critical_skus > 0:
    recs.append(f"Issue purchase orders immediately for **{critical_skus} SKUs** to prevent stockout within supplier lead time window ({lead_time_days} days).")

if overstocked_skus > 0:
    recs.append(f"Consider promotional discounting or bundling strategies for **{overstocked_skus} overstocked SKUs** to liberate **${locked_capital:,.0f}** in working capital.")

recs.append(f"Current safety stock parameters set to **{safety_stock_days} days** cushion. Review supplier reliability quarterly to optimize safety stock thresholds.")

for r in recs:
    st.warning("⚡ " + r)

# ==========================================================
# FOOTER
# ==========================================================

st.markdown("---")
st.caption("""
RetailPulse AI • Inventory Risk Analytics Dashboard

Powered by Streamlit • Plotly • Python

© 2026
""")