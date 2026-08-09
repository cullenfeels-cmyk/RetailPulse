# RetailPulse – AI-Powered Customer Analytics & Demand Forecasting Dashboard

## Project Overview
RetailPulse is an end-to-end AI-powered retail analytics and demand forecasting platform built using Python, SQL, Streamlit, and advanced Machine Learning/MLOps practices. The project analyzes historical retail datasets to forecast future product demand, segment customer behavior through RFM analysis, predict churn-prone accounts, and optimize inventory planning.

## Objectives
* Clean and preprocess complex transactional retail data.
* Perform Exploratory Data Analysis (EDA) and robust feature engineering (lag stats, rolling averages).
* Implement customer segmentation via K-Means clustering and Churn classification models.
* Build demand forecasting models using Prophet and LSTM hybrid architectures.
* Develop an interactive, multi-page visual analytics dashboard.
* Integrate MLOps workflows including MLflow experiment tracking, Optuna tuning, and data drift detection.

## Tools & Technologies
* **Programming & ML:** Python, Pandas, NumPy, Scikit-Learn, TensorFlow, Prophet
* **Database & Analytics:** SQL, Excel
* **Frontend & Visualization:** Streamlit, Matplotlib, Seaborn
* **MLOps & Orchestration:** MLflow, Optuna, Apache Airflow, Docker
* **Version Control:** Git & GitHub

## Dashboard Pages (15-Page Interactive Suite)
1. Home (`1_Home.py`)
2. Executive Dashboard (`2_Executive_Dashboard.py`)
3. Sales Analytics (`3_Sales_Analytics.py`)
4. Product Analytics (`4_Product_Analytics.py`)
5. Customer Analysis (`5_customer_analysis.py`)
6. Country Insights (`6_Country_Insights.py`)
7. Time Analysis (`7_Time_Analysis.py`)
8. Profit Analysis (`8_Profit_Analysis.py`)
9. Inventory Risk (`9_Inventory_Risk.py`)
10. Business Insights (`10_Business_Insights.py`)
11. Advanced Analytics (`11_Advanced_Analytics.py`)
12. KPI Summary (`12_KPI_Summary.py`)
13. Customer Churn Risk (`13_Customer_Churn_Risk.py`)
14. Demand Explorer (`14_Demand_Explorer.py`)
15. Thank You (`15_Thank_You.py`)
    
## Key KPIs
* Total Revenue
* Total Orders
* Total Customers
* Total Countries
* Total Quantity Sold
* Average Order Value (AOV)
* Average Monthly Revenue
* Forecasted Demand vs. Adjusted Demand
* Reorder Points & Safety Stock Levels

## Business & Technical Insights
* Monthly and seasonal sales trend extraction
* Identification of top-selling products and high-value customer tiers
* Country-wise revenue distribution analysis
* Churn feature importance analysis (highlighting recency as a primary risk indicator)
* Automated data drift and distribution checks (Old vs. New data comparisons)

## Author
**Gulafsha**  
*Data Analytics & AI Portfolio Project*
