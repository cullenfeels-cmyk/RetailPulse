# DAX Measures

## Total Revenue

```DAX
Total Revenue =
SUM(cleaned_online_retail[Revenue])
```

## Total Orders

```DAX
Total Orders =
DISTINCTCOUNT(cleaned_online_retail[Invoice])
```

## Total Customers

```DAX
Total Customers =
DISTINCTCOUNT(cleaned_online_retail[Customer ID])
```

## Total Countries

```DAX
Total Countries =
DISTINCTCOUNT(cleaned_online_retail[Country])
```

## Total Quantity

```DAX
Total Quantity =
SUM(cleaned_online_retail[Quantity])
```

## Average Monthly Revenue

```DAX
Average Monthly Revenue =
AVERAGEX(
    VALUES(cleaned_online_retail[Month]),
    CALCULATE(SUM(cleaned_online_retail[Revenue]))
)
```

## Average Order Value

```DAX
Average Order Value =
DIVIDE(
    SUM(cleaned_online_retail[Revenue]),
    DISTINCTCOUNT(cleaned_online_retail[Invoice])
)
```

## Total Products

```DAX
Total Products =
DISTINCTCOUNT(cleaned_online_retail[StockCode])
```