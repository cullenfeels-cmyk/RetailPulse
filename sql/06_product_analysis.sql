-- ==========================================
-- Product Analysis
-- ==========================================

-- Total Products
SELECT
    COUNT(DISTINCT StockCode) AS Total_Products
FROM online_retail;

-- Top 10 Products by Revenue
SELECT
    Description,
    SUM(Revenue) AS Total_Revenue
FROM online_retail
GROUP BY Description
ORDER BY Total_Revenue DESC
LIMIT 10;

-- Top 10 Products by Quantity
SELECT
    Description,
    SUM(Quantity) AS Total_Quantity
FROM online_retail
GROUP BY Description
ORDER BY Total_Quantity DESC
LIMIT 10;