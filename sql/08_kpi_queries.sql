-- ==========================================
-- KPI Queries
-- ==========================================

-- Revenue KPI
SELECT SUM(Revenue) AS Total_Revenue
FROM online_retail;

-- Orders KPI
SELECT COUNT(DISTINCT Invoice) AS Total_Orders
FROM online_retail;

-- Customers KPI
SELECT COUNT(DISTINCT CustomerID) AS Total_Customers
FROM online_retail;

-- Countries KPI
SELECT COUNT(DISTINCT Country) AS Total_Countries
FROM online_retail;

-- Quantity KPI
SELECT SUM(Quantity) AS Total_Quantity
FROM online_retail;

-- Average Order Value
SELECT
    SUM(Revenue) / COUNT(DISTINCT Invoice) AS Average_Order_Value
FROM online_retail;

-- Average Product Price
SELECT
    AVG(Price) AS Average_Product_Price
FROM online_retail;