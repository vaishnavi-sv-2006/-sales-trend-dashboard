import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

np.random.seed(42)
random.seed(42)

n_rows = 9994  # similar size to the real Superstore dataset

regions = ["East", "West", "Central", "South"]
states_by_region = {
    "East": ["New York", "Pennsylvania", "New Jersey", "Massachusetts", "Virginia"],
    "West": ["California", "Washington", "Oregon", "Nevada", "Arizona"],
    "Central": ["Texas", "Illinois", "Ohio", "Michigan", "Missouri"],
    "South": ["Florida", "Georgia", "North Carolina", "Tennessee", "Alabama"],
}
categories = {
    "Furniture": ["Chairs", "Tables", "Bookcases", "Furnishings"],
    "Office Supplies": ["Binders", "Paper", "Storage", "Art", "Labels"],
    "Technology": ["Phones", "Machines", "Accessories", "Copiers"],
}
segments = ["Consumer", "Corporate", "Home Office"]
ship_modes = ["Standard Class", "Second Class", "First Class", "Same Day"]

start_date = datetime(2021, 1, 1)
end_date = datetime(2024, 12, 31)
date_range_days = (end_date - start_date).days

rows = []
for i in range(n_rows):
    order_date = start_date + timedelta(days=random.randint(0, date_range_days))
    ship_delay = random.randint(1, 7)
    ship_date = order_date + timedelta(days=ship_delay)

    region = random.choice(regions)
    state = random.choice(states_by_region[region])
    category = random.choice(list(categories.keys()))
    sub_category = random.choice(categories[category])

    # base price varies by category to feel realistic
    base_price = {
        "Furniture": np.random.uniform(50, 800),
        "Office Supplies": np.random.uniform(2, 150),
        "Technology": np.random.uniform(30, 1200),
    }[category]

    quantity = random.randint(1, 8)
    discount = random.choice([0, 0, 0, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5])
    sales = round(base_price * quantity * (1 - discount * 0.3), 2)  # discount softens revenue a bit
    profit_margin = np.random.uniform(-0.25, 0.35)  # some orders lose money
    profit = round(sales * profit_margin, 2)

    rows.append({
        "Row ID": i + 1,
        "Order ID": f"US-{order_date.year}-{100000 + i}",
        "Order Date": order_date.strftime("%m/%d/%Y"),
        "Ship Date": ship_date.strftime("%m/%d/%Y"),
        "Ship Mode": random.choice(ship_modes),
        "Customer ID": f"CG-{random.randint(10000,99999)}",
        "Segment": random.choice(segments),
        "Region": region,
        "State": state,
        "Category": category,
        "Sub-Category": sub_category,
        "Sales": sales,
        "Quantity": quantity,
        "Discount": discount,
        "Profit": profit,
    })

df = pd.DataFrame(rows)

# --- Intentionally introduce messiness for cleaning practice ---
# 1. Some missing values
missing_idx = np.random.choice(df.index, size=150, replace=False)
df.loc[missing_idx, "Sales"] = np.nan

missing_idx2 = np.random.choice(df.index, size=80, replace=False)
df.loc[missing_idx2, "Region"] = np.nan

# 2. Some duplicate rows
dup_rows = df.sample(40, random_state=1)
df = pd.concat([df, dup_rows], ignore_index=True)

# 3. Inconsistent text casing
df.loc[df.sample(frac=0.05, random_state=2).index, "Region"] = df["Region"].str.upper()

# 4. Shuffle rows
df = df.sample(frac=1, random_state=3).reset_index(drop=True)
df["Row ID"] = range(1, len(df) + 1)

df.to_csv("/home/claude/sales_data_raw.csv", index=False)
print(f"Generated {len(df)} rows")
print(df.head())
print("\nNulls per column:\n", df.isnull().sum())
print("\nDuplicate rows (excluding Row ID):", df.drop(columns=["Row ID"]).duplicated().sum())
