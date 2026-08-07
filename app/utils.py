from pathlib import Path
import pandas as pd
import streamlit as st


@st.cache_data(show_spinner=False)
def load_data():
    """Loads and prepares retail dataset with all required metrics safely."""

    # ==========================================================
    # LOAD DATA
    # ==========================================================
    data_path = Path(__file__).parent.parent / "data" / "cleaned_data.csv"

    if not data_path.exists():
        # Fallback path check if file structure differs
        data_path = Path(__file__).parent / "data" / "cleaned_data.csv"

    if not data_path.exists():
        st.error(f"Dataset not found at {data_path}. Please check file location.")
        return pd.DataFrame()

    df = pd.read_csv(data_path)

    # Clean column names
    df.columns = df.columns.str.strip()

    # ==========================================================
    # DATE HANDLING
    # ==========================================================
    if "InvoiceDate" in df.columns:
        df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")
        df["Year"] = df["InvoiceDate"].dt.year
        df["Month"] = df["InvoiceDate"].dt.month
        df["MonthName"] = df["InvoiceDate"].dt.strftime("%b")

    # ==========================================================
    # UNIFIED SALES / REVENUE LOGIC
    # ==========================================================
    if "TotalPrice" not in df.columns:
        if "Sales" in df.columns:
            df["TotalPrice"] = df["Sales"]
        elif "Revenue" in df.columns:
            df["TotalPrice"] = df["Revenue"]
        elif "UnitPrice" in df.columns and "Quantity" in df.columns:
            df["TotalPrice"] = df["UnitPrice"] * df["Quantity"]
        else:
            df["TotalPrice"] = 0.0

    # Ensure aliases exist
    if "Sales" not in df.columns:
        df["Sales"] = df["TotalPrice"]

    if "Revenue" not in df.columns:
        df["Revenue"] = df["TotalPrice"]

    # ==========================================================
    # DATA CLEANING
    # ==========================================================
    if "Quantity" in df.columns:
        df = df[df["Quantity"] > 0]

    if "TotalPrice" in df.columns:
        df = df[df["TotalPrice"] > 0]

    # Clean missing critical identifiers
    critical_cols = [
        col for col in ["CustomerID", "InvoiceDate"] if col in df.columns
    ]
    if critical_cols:
        df = df.dropna(subset=critical_cols)

    if "CustomerID" in df.columns:
        # Prevent trailing decimals like '12345.0' in string IDs
        df["CustomerID"] = (
            df["CustomerID"]
            .astype(str)
            .str.replace(r"\.0$", "", regex=True)
            .str.strip()
        )

    # ==========================================================
    # METRICS CALCULATION
    # ==========================================================
    if "InvoiceNo" in df.columns:
        order_value = (
            df.groupby("InvoiceNo")["TotalPrice"].sum().reset_index()
        )
        avg_order_value = order_value["TotalPrice"].mean()
        df["AvgOrderValue"] = avg_order_value

    if "CustomerID" in df.columns:
        df["CustomerSpend"] = df.groupby("CustomerID")["TotalPrice"].transform(
            "sum"
        )

    if "Description" in df.columns:
        df["ProductSales"] = df.groupby("Description")["TotalPrice"].transform(
            "sum"
        )

    return df.reset_index(drop=True)