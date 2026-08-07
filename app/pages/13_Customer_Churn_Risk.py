import streamlit as st
import pandas as pd
import plotly.express as px
from styles import load_css
from utils import load_data

st.set_page_config(page_title="Customer Churn Risk", page_icon="⚠️", layout="wide")
load_css("light")

st.markdown("""
<div class="dashboard-title">⚠️ RetailPulse AI</div>
<div class="dashboard-subtitle">Customer Churn Prediction & Risk Analysis</div>
""", unsafe_allow_html=True)

df = load_data()

st.markdown("## 🎯 Customer Churn Risk Overview")

# Dynamically find the correct column names from the dataset
customer_col = next((col for col in df.columns if "customer" in col.lower() or "client" in col.lower() or "id" in col.lower()), None)
date_col = next((col for col in df.columns if "date" in col.lower()), None)
price_col = next((col for col in df.columns if "price" in col.lower() or "total" in col.lower() or "amount" in col.lower()), None)
invoice_col = next((col for col in df.columns if "invoice" in col.lower() or "order" in col.lower() or "transaction" in col.lower()), customer_col)

if customer_col and date_col:
    # Ensure date column is datetime
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    max_date = df[date_col].max()
    
    # Aggregate data per customer
    agg_dict = {
        date_col: ("max", "max"),
    }
    if price_col:
        agg_dict["Total_Spent"] = (price_col, "sum")
    if invoice_col:
        agg_dict["Order_Count"] = (invoice_col, "nunique")

    churn_df = df.groupby(customer_col).agg(**agg_dict).reset_index()
    churn_df.rename(columns={date_col: "Last_Purchase"}, inplace=True)
    
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
    st.error(f"Could not automatically detect required columns. Found columns: {list(df.columns)}")