import sys

print("RUNNING PYTHON:")
print(sys.executable)

import streamlit as st
import pandas as pd

from auth import login
from styles import load_css
from utils import load_data

import sys
import os   # ✅ ADD THIS

print("RUNNING PYTHON:")
print(sys.executable)

import streamlit as st
import pandas as pd

from auth import login
from styles import load_css
from utils import load_data

# ✅ ADD THIS RIGHT HERE
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ==========================================================
# PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="RetailPulse AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================================
# LOAD CSS
# ==========================================================

load_css()

# ==========================================================
# LOGIN
# ==========================================================

if not login():
    st.stop()

# ==========================================================
# LOAD DATA
# ==========================================================

df = load_data()

# ==========================================================
# HEADER
# ==========================================================

st.markdown("""
<div class="dashboard-title">
    🚀 RetailPulse AI Platform
</div>
<div class="dashboard-subtitle">
    AI Powered Retail Sales Analytics & Business Intelligence
</div>
""", unsafe_allow_html=True)

# ==========================================================
# SIDEBAR
# ==========================================================

st.sidebar.image(
    "https://img.icons8.com/color/96/combo-chart.png",
    width=80
)

st.sidebar.title("RetailPulse AI")

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Executive Dashboard",
        "👥 Customer Analytics",
        "🎯 Customer Segmentation",
        "📈 Demand Forecast",
        "📦 Inventory Optimization",
        "🤖 AI Business Insights"
    ]
)

st.sidebar.markdown("---")

st.sidebar.success("Logged In")

# ==========================================================
# EXECUTIVE DASHBOARD
# ==========================================================

if page == "🏠 Executive Dashboard":

    st.header("📊 Executive Dashboard")

    total_sales = df["Sales"].sum()

    if "Invoice" in df.columns:
        total_orders = df["Invoice"].nunique()

    elif "InvoiceNo" in df.columns:
        total_orders = df["InvoiceNo"].nunique()

    else:
        total_orders = len(df)

    if "CustomerID" in df.columns:
        total_customers = df["CustomerID"].nunique()

    elif "Customer ID" in df.columns:
        total_customers = df["Customer ID"].nunique()

    else:
        total_customers = 0

    total_products = (
        df["Description"].nunique()
        if "Description" in df.columns
        else 0
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "💰 Revenue",
        f"${total_sales:,.2f}"
    )

    c2.metric(
        "📦 Orders",
        f"{total_orders:,}"
    )

    c3.metric(
        "👥 Customers",
        f"{total_customers:,}"
    )

    c4.metric(
        "🛒 Products",
        f"{total_products:,}"
    )

    st.divider()

    if "InvoiceDate" in df.columns:

        monthly = (
            df.groupby(
                df["InvoiceDate"].dt.to_period("M")
            )["Sales"]
            .sum()
            .reset_index()
        )

        monthly["InvoiceDate"] = (
            monthly["InvoiceDate"].astype(str)
        )

        st.line_chart(
            monthly.set_index("InvoiceDate")
        )

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("🏆 Top Products")

        if "Description" in df.columns:

            top_products = (
                df.groupby("Description")["Sales"]
                .sum()
                .sort_values(ascending=False)
                .head(10)
            )

            st.bar_chart(top_products)

    with col2:

        st.subheader("🌍 Top Countries")

        if "Country" in df.columns:

            top_country = (
                df.groupby("Country")["Sales"]
                .sum()
                .sort_values(ascending=False)
                .head(10)
            )

            st.bar_chart(top_country)

    with st.expander("📄 Dataset Preview"):

        st.dataframe(
            df.head(20),
            use_container_width=True
        )

# ==========================================================
# CUSTOMER ANALYTICS
# ==========================================================

elif page == "👥 Customer Analytics":

    st.header("👥 Customer Analytics")

    customer_col = None

    if "CustomerID" in df.columns:
        customer_col = "CustomerID"

    elif "Customer ID" in df.columns:
        customer_col = "Customer ID"

    if customer_col:

        customer_sales = (
            df.groupby(customer_col)["Sales"]
            .sum()
            .sort_values(ascending=False)
            .reset_index()
        )

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Customers",
            customer_sales.shape[0]
        )

        c2.metric(
            "Average Spend",
            f"${customer_sales['Sales'].mean():,.2f}"
        )

        c3.metric(
            "Highest Spend",
            f"${customer_sales['Sales'].max():,.2f}"
        )

        st.subheader("Customer Spending")

        st.bar_chart(
            customer_sales.head(20).set_index(customer_col)
        )

        st.subheader("Customer Table")

        st.dataframe(
            customer_sales.head(20),
            use_container_width=True
        )

    else:

        st.warning("Customer ID column not found.")

# ==========================================================
# CUSTOMER SEGMENTATION
# ==========================================================

elif page == "🎯 Customer Segmentation":

    st.header("🎯 Customer Segmentation")

    import sys
    st.write("Python:", sys.executable)

    try:
        import plotly
        st.success(f"Plotly Loaded: {plotly.__version__}")
        import plotly.express as px

    except Exception as e:
        st.error(f"Plotly Error: {e}")
        st.stop()

    # -----------------------------
    # Load Segmentation Data
    # -----------------------------
    seg_path = os.path.join(BASE_DIR, "data", "customer_segments.csv")
    seg_df = pd.read_csv(seg_path)

    # -----------------------------
    # KPI Cards
    # -----------------------------
    total_customers = seg_df["Customer ID"].nunique()
    total_segments = seg_df["Customer_Segment"].nunique()
    total_clusters = seg_df["Cluster"].nunique()

    avg_revenue = seg_df["Monetary"].mean()

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("👥 Customers", f"{total_customers:,}")
    c2.metric("🎯 Segments", total_segments)
    c3.metric("🧠 Clusters", total_clusters)
    c4.metric("💰 Avg Revenue", f"${avg_revenue:,.2f}")

    st.divider()

    # -----------------------------
    # Customer Segment Distribution
    # -----------------------------
    st.subheader("Customer Segment Distribution")

    segment_count = (
        seg_df["Customer_Segment"]
        .value_counts()
        .reset_index()
    )

    segment_count.columns = ["Segment", "Customers"]

    fig = px.bar(
        segment_count,
        x="Segment",
        y="Customers",
        color="Customers",
        text="Customers",
        title="Customer Segments"
    )

    st.plotly_chart(fig, use_container_width=True)

    # -----------------------------
    # Cluster Distribution
    # -----------------------------
    st.subheader("Cluster Distribution")

    cluster_count = (
        seg_df["Cluster"]
        .value_counts()
        .sort_index()
        .reset_index()
    )

    cluster_count.columns = ["Cluster", "Customers"]

    fig = px.pie(
        cluster_count,
        names="Cluster",
        values="Customers",
        hole=0.45
    )

    st.plotly_chart(fig, use_container_width=True)

    # -----------------------------
    # Revenue by Segment
    # -----------------------------
    st.subheader("Revenue by Customer Segment")

    revenue = (
        seg_df.groupby("Customer_Segment")["Monetary"]
        .mean()
        .reset_index()
    )

    fig = px.bar(
        revenue,
        x="Customer_Segment",
        y="Monetary",
        color="Monetary",
        text_auto=".2f"
    )

    st.plotly_chart(fig, use_container_width=True)

    # -----------------------------
    # Scatter Plot
    # -----------------------------
    st.subheader("Monetary vs Frequency")

    fig = px.scatter(
        seg_df,
        x="Frequency",
        y="Monetary",
        color="Customer_Segment",
        size="Total_Revenue",
        hover_data=[
            "Customer ID",
            "Recency",
            "Cluster"
        ]
    )

    st.plotly_chart(fig, use_container_width=True)

    # -----------------------------
    # Cluster Summary
    # -----------------------------
    st.subheader("Cluster Profile")

    cluster_summary = (
        seg_df.groupby("Customer_Segment")[
            [
                "Recency",
                "Frequency",
                "Monetary",
                "Average_Order_Value",
                "Unique_Products"
            ]
        ]
        .mean()
        .round(2)
        .reset_index()
    )

    st.dataframe(cluster_summary, use_container_width=True)

    # -----------------------------
    # Customer Table
    # -----------------------------
    st.subheader("Customer Details")

    st.dataframe(seg_df, use_container_width=True)

    # -----------------------------
    # Download Button
    # -----------------------------
    csv = seg_df.to_csv(index=False)

    st.download_button(
        "⬇ Download Customer Segments",
        csv,
        file_name="customer_segments.csv",
        mime="text/csv"
    )

    # -----------------------------
    # AI Business Insights
    # -----------------------------
    st.subheader("🤖 AI Business Insights")

    largest = seg_df["Customer_Segment"].value_counts().idxmax()

    highest = (
        seg_df.groupby("Customer_Segment")["Monetary"]
        .mean()
        .idxmax()
    )

    frequent = (
        seg_df.groupby("Customer_Segment")["Frequency"]
        .mean()
        .idxmax()
    )

    lost = (
        seg_df["Customer_Segment"] == "Lost Customers"
    ).sum()

    st.success(f"📌 Largest Segment : {largest}")

    st.success(f"💰 Highest Spending Segment : {highest}")

    st.success(f"🛒 Most Frequent Buyers : {frequent}")

    st.warning(f"⚠ Lost Customers : {lost}")

    st.info(
        """
### Recommendations

• Focus marketing campaigns on VIP Customers.

• Reward Loyal Customers with exclusive offers.

• Re-engage Lost Customers through discounts.

• Upsell Regular Customers to increase revenue.

• Monitor High Value Customers for retention.
"""
    )

# ==========================================================
# DEMAND FORECAST
# ==========================================================

elif page == "📈 Demand Forecast":

    import plotly.express as px

    st.header("📈 AI Demand Forecast")

    # ==========================================
    # Load Forecast
    # ==========================================

    forecast = pd.read_csv(
        r"D:\RetailPulse\outputs\demand_forecast.csv"
    )

    forecast["ds"] = pd.to_datetime(forecast["ds"])

    # ==========================================
    # KPI Cards
    # ==========================================

    total_days = len(forecast)

    avg_forecast = forecast["yhat"].mean()

    max_forecast = forecast["yhat"].max()

    min_forecast = forecast["yhat"].min()

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Forecast Days", total_days)

    c2.metric("Average Demand", f"{avg_forecast:,.0f}")

    c3.metric("Maximum Forecast", f"{max_forecast:,.0f}")

    c4.metric("Minimum Forecast", f"{min_forecast:,.0f}")

    st.divider()

    # ==========================================
    # Forecast Chart
    # ==========================================

    st.subheader("Demand Forecast")

    fig = px.line(
        forecast,
        x="ds",
        y="yhat",
        title="30-Day Demand Forecast"
    )

    fig.update_traces(line_width=3)

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # ==========================================
    # Confidence Interval
    # ==========================================

    if (
        "yhat_lower" in forecast.columns
        and "yhat_upper" in forecast.columns
    ):

        st.subheader("Forecast Confidence Interval")

        fig = px.line(
            forecast,
            x="ds",
            y=[
                "yhat_lower",
                "yhat",
                "yhat_upper"
            ]
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # ==========================================
    # Forecast Table
    # ==========================================

    st.subheader("Forecast Data")

    st.dataframe(
        forecast,
        use_container_width=True
    )

    # ==========================================
    # Download
    # ==========================================

    csv = forecast.to_csv(index=False)

    st.download_button(
        "⬇ Download Forecast",
        csv,
        "demand_forecast.csv",
        "text/csv"
    )

    # ==========================================
    # AI Insights
    # ==========================================

    st.subheader("🤖 AI Business Insights")

    trend = (
        "Increasing"
        if forecast["yhat"].iloc[-1] >
           forecast["yhat"].iloc[0]
        else "Decreasing"
    )

    peak_day = forecast.loc[
        forecast["yhat"].idxmax(),
        "ds"
    ]

    peak_value = forecast["yhat"].max()

    low_day = forecast.loc[
        forecast["yhat"].idxmin(),
        "ds"
    ]

    st.success(f"📈 Demand Trend : {trend}")

    st.success(
        f"🔥 Peak Demand : {peak_value:,.0f} units on {peak_day.date()}"
    )

    st.warning(
        f"📉 Lowest Demand : {low_day.date()}"
    )

    st.info("""
### Business Recommendations

• Increase inventory before peak demand periods.

• Reduce stock during low-demand periods.

• Plan marketing campaigns around forecast peaks.

• Use demand forecasting to optimize procurement.

• Continuously retrain the forecasting model with new sales data.
""")
# ==========================================================
# INVENTORY
# ==========================================================

elif page == "📦 Inventory Optimization":

    import plotly.express as px

    st.header("📦 Inventory Optimization")

    if "Description" not in df.columns or "Quantity" not in df.columns:
        st.error("Required columns (Description and Quantity) are missing.")
        st.stop()

    inventory = (
        df.groupby("Description", as_index=False)
          .agg(
              Total_Quantity=("Quantity", "sum"),
              Total_Sales=("Sales", "sum")
          )
    )

    inventory["Inventory_Status"] = inventory["Total_Quantity"].apply(
        lambda x: "Low Stock" if x < 100
        else "Medium Stock" if x < 500
        else "High Stock"
    )

    # ---------------- KPIs ----------------

    total_products = inventory["Description"].nunique()
    low_stock = (inventory["Inventory_Status"] == "Low Stock").sum()
    medium_stock = (inventory["Inventory_Status"] == "Medium Stock").sum()
    high_stock = (inventory["Inventory_Status"] == "High Stock").sum()

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("📦 Products", total_products)
    c2.metric("🔴 Low Stock", low_stock)
    c3.metric("🟠 Medium Stock", medium_stock)
    c4.metric("🟢 High Stock", high_stock)

    st.divider()

    # ---------------- Inventory Status ----------------

    st.subheader("Inventory Status")

    status = (
        inventory["Inventory_Status"]
        .value_counts()
        .reset_index()
    )

    status.columns = ["Status", "Products"]

    fig = px.pie(
        status,
        names="Status",
        values="Products",
        hole=0.45,
        title="Inventory Distribution"
    )

    st.plotly_chart(fig, use_container_width=True)

    # ---------------- Top Products ----------------

    st.subheader("Top Selling Products")

    top_sales = (
        inventory.sort_values(
            "Total_Sales",
            ascending=False
        )
        .head(15)
    )

    fig = px.bar(
        top_sales,
        x="Description",
        y="Total_Sales",
        color="Total_Sales",
        text_auto=".2s",
        title="Top Selling Products"
    )

    fig.update_layout(xaxis_tickangle=-45)

    st.plotly_chart(fig, use_container_width=True)

    # ---------------- Low Stock ----------------

    st.subheader("Low Stock Products")

    st.dataframe(
        inventory[inventory["Inventory_Status"] == "Low Stock"],
        use_container_width=True
    )

    # ---------------- High Stock ----------------

    st.subheader("High Stock Products")

    st.dataframe(
        inventory[inventory["Inventory_Status"] == "High Stock"],
        use_container_width=True
    )

    # ---------------- Download ----------------

    csv = inventory.to_csv(index=False)

    st.download_button(
        "⬇ Download Inventory Report",
        csv,
        "inventory_report.csv",
        "text/csv"
    )

    # ---------------- AI Insights ----------------

    st.subheader("🤖 AI Inventory Insights")

    top_product = inventory.sort_values(
        "Total_Sales",
        ascending=False
    ).iloc[0]["Description"]

    st.success(f"🏆 Best Selling Product: {top_product}")

    st.info(
        f"⚠️ {low_stock} products are currently classified as Low Stock."
    )

    st.info(
        f"🟢 {high_stock} products have High Stock levels."
    )

    st.markdown("""
### Recommendations

- Reorder products in the **Low Stock** category before demand increases.
- Monitor **Medium Stock** items to avoid shortages.
- Reduce overstock for products with high inventory and low sales.
- Prioritize warehouse space for fast-moving products.
- Review inventory weekly to improve stock turnover.
""")
        

# ==========================================================
# AI INSIGHTS
# ==========================================================

elif page == "🤖 AI Business Insights":

    st.header("🤖 AI Business Insights")

    st.success("✔ Revenue trends loaded")

    st.success("✔ Customer analytics available")

    st.success("✔ Forecast model ready")

    st.success("✔ Inventory optimization ready")

    st.info("""
### Recommendations

• Focus on repeat customers.

• Maintain stock for top-selling products.

• Reduce inventory for slow-moving products.

• Use demand forecasting for purchase planning.
""")

# ==========================================================
# FOOTER
# ==========================================================

st.markdown("---")

st.caption(
    "RetailPulse AI | Developed by Gulafsha"
)
