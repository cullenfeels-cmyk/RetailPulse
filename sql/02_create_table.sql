-- ==========================================
-- Create Online Retail Table
-- ==========================================

CREATE TABLE online_retail (
    Invoice INT,
    StockCode VARCHAR(20),
    Description VARCHAR(255),
    Quantity INT,
    InvoiceDate DATETIME,
    Price DECIMAL(10,2),
    CustomerID INT,
    Country VARCHAR(100),
    Month DATE,
    Revenue DECIMAL(12,2)
);