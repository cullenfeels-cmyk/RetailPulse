import streamlit as st
import pandas as pd
import plotly.express as px
from styles import load_css
from utils import load_data

st.set_page_config(page_title="Customer Churn Risk", page_icon="⚠️", layout="wide")
load_css("light")

# ==========================================================
# BACK TO HOME NAVIGATION BUTTON
# ==========================================================
if st.button("⬅️ Back to Home"):
    st.switch_page("pages/1_Home.py")

st.markdown("""
<div class="dashboard-title">⚠️ RetailPulse AI</div>
<div class="dashboard-subtitle">Customer Churn Prediction & Risk Analysis</div>
""", unsafe_allow_html=True)

df = load_data()

st.markdown("## 🎯 Customer Churn Risk Overview")

# Dynamically search for columns safely
cols = list(df.columns)
customer_col = next((c for c in cols if "customer" in c.lower() or "client" in c.lower() or "id" in c.lower()), None)
date_col = next((c for c in cols if "date" in c.lower()), None)
price_col = next((c for c in cols if "price" in c.lower() or "total" in c.lower() or "amount" in c.lower()), None)
invoice_col = next((c for c in cols if "invoice" in c.lower() or "order" in c.lower()), None)

if customer_col and date_col:
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    max_date = df[date_col].max()
    
    # Build safe dynamic aggregation dictionary
    agg_rules = {date_col: "max"}
    if price_col and price_col in df.columns:
        agg_rules[price_col] = "sum"
    if invoice_col and invoice_col in df.columns:
        agg_rules[invoice_col] = "nunique"

    churn_df = df.groupby(customer_col).agg(agg_rules).reset_index()
    
    # Rename columns safely based on what was aggregated
    rename_mapping = {date_col: "Last_Purchase"}
    if price_col in agg_rules:
        rename_mapping[price_col] = "Total_Spent"
    if invoice_col in agg_rules:
        rename_mapping[invoice_col] = "Order_Count"
    
    churn_df.rename(columns=rename_mapping, inplace=True)
    
    churn_df["Days_Inactive"] = (max_date - churn_df["Last_Purchase"]).dt.days
    churn_df["Churn_Risk"] = churn_df["Days_Inactive"].apply(
        lambda x: "High Risk" if x > 90 else ("Medium Risk" if x > 60 else "Low Risk")
    )

    risk_counts = churn_df["Churn_Risk"].value_counts().reset_index()
    risk_counts.columns = ["Risk Level", "Count"]

    col1, col2 = st.columns(2)
    with col1:
        fig = px.pie(risk_counts, values="Count", names="Risk Level", title="Customer Churn Risk Distribution", hole=0.4, template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig_bar = px.bar(risk_counts, x="Risk Level", y="Count", color="Risk Level", title="Customers per Risk Category", template="plotly_white")
        st.plotly_chart(fig_bar, use_container_width=True)
        
    st.markdown("### 📋 High-Risk Customer Accounts")
    sort_col = "Total_Spent" if "Total_Spent" in churn_df.columns else "Days_Inactive"
    high_risk_table = churn_df[churn_df["Churn_Risk"] == "High Risk"].sort_values(by=sort_col, ascending=False).head(10)
    st.dataframe(high_risk_table, use_container_width=True)
else:
    st.error(f"Could not locate Customer ID or Date columns. Available columns: {cols}")