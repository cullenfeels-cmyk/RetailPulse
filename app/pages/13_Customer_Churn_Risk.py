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

# Load churn predictions if available, else simulate/calculate based on recency
st.markdown("## 🎯 Customer Churn Risk Overview")

if "CustomerID" in df.columns:
    # Calculate Recency to determine churn risk proxy
    max_date = df["InvoiceDate"].max()
    churn_df = df.groupby("CustomerID").agg(
        Last_Purchase=("InvoiceDate", "max"),
        Total_Spent=("TotalPrice", "sum"),
        Order_Count=("Invoice", "nunique")
    ).reset_index()
    
    churn_df["Days_Inactive"] = (max_date - churn_df["Last_Purchase"]).dt.days
    churn_df["Churn_Risk"] = churn_df["Days_Inactive"].apply(lambda x: "High Risk" if x > 90 else ("Medium Risk" if x > 60 else "Low Risk"))

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
    high_risk_table = churn_df[churn_df["Churn_Risk"] == "High Risk"].sort_values(by="Total_Spent", ascending=False).head(10)
    st.dataframe(high_risk_table, use_container_width=True)
else:
    st.warning("Customer ID data not found for churn analytics.")