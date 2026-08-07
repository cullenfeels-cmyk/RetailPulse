import streamlit as st
import pandas as pd
import plotly.express as px
from styles import load_css
from utils import load_data

st.set_page_config(page_title="Demand Explorer", page_icon="📈", layout="wide")
load_css("light")

if st.button("⬅️ Back to Home"):
    st.switch_page("pages/1_Home.py")

st.markdown("""
<div class="dashboard-title">📈 RetailPulse AI</div>
<div class="dashboard-subtitle">Product Demand & Forecasting Explorer</div>
""", unsafe_allow_html=True)

df = load_data()

st.markdown("## 🔍 Product Demand Explorer")

product_list = sorted(df["Description"].dropna().unique())
selected_product = st.selectbox("Select Product to Analyze Demand", product_list)

product_df = df[df["Description"] == selected_product]
product_monthly = product_df.groupby(product_df["InvoiceDate"].dt.to_period("M"))["Quantity"].sum().reset_index()
product_monthly["InvoiceDate"] = product_monthly["InvoiceDate"].astype(str)

fig = px.line(product_monthly, x="InvoiceDate", y="Quantity", markers=True, title=f"Historical Demand Trend for: {selected_product}", template="plotly_white")
fig.update_layout(height=450, xaxis_title="Month", yaxis_title="Units Demanded")
st.plotly_chart(fig, use_container_width=True)

st.markdown("### 📊 Demand Statistics")
c1, c2, c3 = st.columns(3)
c1.metric("Total Units Sold", f"{product_df['Quantity'].sum():,}")
c2.metric("Total Revenue Generated", f"${product_df['TotalPrice'].sum():,.2f}")
c3.metric("Total Orders Featuring Item", f"{product_df['Invoice'].nunique():,}")