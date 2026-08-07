-- ==========================================
-- Country Analysis
-- ==========================================

-- Total Countries
SELECT
    COUNT(DISTINCT Country) AS Total_Countries
FROM online_retail;

-- Revenue by Country
SELECT
    Country,
    SUM(Revenue) AS Total_Revenue
FROM online_retail
GROUP BY Country
ORDER BY Total_Revenue DESC;

-- Quantity by Country
SELECT
    Country,
    SUM(Quantity) AS Total_Quantity
FROM online_retail
GROUP BY Country
ORDER BY Total_Quantity DESC;