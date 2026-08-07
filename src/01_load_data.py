import pandas as pd

# Path to the dataset
file_path = "data/online_retail_II.xlsx"

# Read the first sheet
df = pd.read_excel(file_path)

print("=" * 50)
print("RetailPulse Project")
print("=" * 50)

print("\nDataset Shape:")
print(df.shape)

print("\nColumn Names:")
print(df.columns.tolist())

print("\nFirst 5 Rows:")
print(df.head())