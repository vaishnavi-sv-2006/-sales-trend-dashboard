import pandas as pd
import numpy as np

# Load raw data
df = pd.read_csv("/home/claude/sales_data_raw.csv")
print("BEFORE CLEANING")
print(f"Shape: {df.shape}")
print(f"Nulls:\n{df.isnull().sum()[df.isnull().sum() > 0]}")
print(f"Duplicates: {df.drop(columns=['Row ID']).duplicated().sum()}")
print("-" * 50)

# 1. Fix inconsistent text casing (e.g. "EAST" vs "East")
df["Region"] = df["Region"].str.strip().str.title()

# 2. Remove exact duplicate rows (ignoring Row ID, which is just an index)
df = df.drop_duplicates(subset=df.columns.difference(["Row ID"]))

# 3. Handle missing Region: fill using the State -> Region mapping (since State is never null)
state_region_map = (
    df.dropna(subset=["Region"])
    .drop_duplicates(subset=["State"])
    .set_index("State")["Region"]
    .to_dict()
)
df["Region"] = df.apply(
    lambda row: state_region_map.get(row["State"], row["Region"]) if pd.isna(row["Region"]) else row["Region"],
    axis=1
)

# 4. Handle missing Sales: use category median (sensible imputation)
category_median_sales = df.groupby("Category")["Sales"].median()
def fill_sales(row):
    if pd.isna(row["Sales"]):
        return category_median_sales[row["Category"]]
    return row["Sales"]
df["Sales"] = df.apply(fill_sales, axis=1)

# 5. Convert date columns to proper datetime
df["Order Date"] = pd.to_datetime(df["Order Date"], format="%m/%d/%Y")
df["Ship Date"] = pd.to_datetime(df["Ship Date"], format="%m/%d/%Y")

# 6. Add useful derived columns for analysis
df["Order Year"] = df["Order Date"].dt.year
df["Order Month"] = df["Order Date"].dt.month
df["Order Month Name"] = df["Order Date"].dt.strftime("%b")
df["Order Year-Month"] = df["Order Date"].dt.to_period("M").astype(str)
df["Shipping Days"] = (df["Ship Date"] - df["Order Date"]).dt.days
df["Profit Margin %"] = (df["Profit"] / df["Sales"] * 100).round(2)

# 7. Reset Row ID after dedup
df = df.sort_values("Order Date").reset_index(drop=True)
df["Row ID"] = range(1, len(df) + 1)

# 8. Round monetary columns
df["Sales"] = df["Sales"].round(2)

print("AFTER CLEANING")
print(f"Shape: {df.shape}")
null_sum = df.isnull().sum()
print(f"Nulls:\n{null_sum[null_sum > 0] if null_sum.sum() > 0 else 'None'}")
print(f"Duplicates: {df.drop(columns=['Row ID']).duplicated().sum()}")
print("-" * 50)
print(df.dtypes)

df.to_csv("/home/claude/sales_data_cleaned.csv", index=False)
print("\nSaved cleaned file to sales_data_cleaned.csv")
