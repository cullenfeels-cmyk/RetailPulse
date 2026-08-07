# Calculated Columns

## Dataset

The RetailPulse project uses a single cleaned fact table:

- cleaned_online_retail

Most transformations were completed during the Python data-cleaning stage before importing the dataset into Power BI.

## Columns Used

- Invoice
- StockCode
- Description
- Quantity
- InvoiceDate
- Price
- Customer ID
- Country
- Month
- Revenue

## Notes

- Revenue was calculated during data preprocessing.
- Month was created for time-based analysis.
- The Power BI model consists of a single fact table, making it simple and efficient for this portfolio project.