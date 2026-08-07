-- ==========================================
-- Customer Analysis
-- ==========================================

-- Total Customers
SELECT
    COUNT(DISTINCT CustomerID) AS Total_Customers
FROM online_retail;

-- Top 10 Customers by Revenue
SELECT
    CustomerID,
    SUM(Revenue) AS Total_Revenue
FROM online_retail
GROUP BY CustomerID
ORDER BY Total_Revenue DESC
LIMIT 10;

-- Top 10 Customers by Quantity
SELECT
    CustomerID,
    SUM(Quantity) AS Total_Quantity
FROM online_retail
GROUP BY CustomerID
ORDER BY Total_Quantity DESC
LIMIT 10;