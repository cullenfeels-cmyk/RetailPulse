-- ==========================================
-- Data Cleaning
-- ==========================================

-- Remove records with missing Customer IDs
DELETE
FROM online_retail
WHERE CustomerID IS NULL;

-- Remove negative or zero quantities
DELETE
FROM online_retail
WHERE Quantity <= 0;

-- Remove negative or zero prices
DELETE
FROM online_retail
WHERE Price <= 0;

-- Check remaining records
SELECT COUNT(*) AS Total_Records
FROM online_retail;