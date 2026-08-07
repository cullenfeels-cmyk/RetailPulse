-- ==========================================
-- Sales Analysis
-- ==========================================

-- Total Revenue
SELECT
    SUM(Revenue) AS Total_Revenue
FROM online_retail;

-- Total Quantity Sold
SELECT
    SUM(Quantity) AS Total_Quantity
FROM online_retail;

-- Total Orders
SELECT
    COUNT(DISTINCT Invoice) AS Total_Orders
FROM online_retail;

-- Monthly Revenue
SELECT
    Month,
    SUM(Revenue) AS Monthly_Revenue
FROM online_retail
GROUP BY Month
ORDER BY Month;

-- Monthly Quantity Sold
SELECT
    Month,
    SUM(Quantity) AS Monthly_Quantity
FROM online_retail
GROUP BY Month
ORDER BY Month;