import pandas as pd
import numpy as np

pd.set_option("display.width", 120)
pd.set_option("display.max_columns", 20)

df = pd.read_csv("/home/claude/sales_data_cleaned.csv")
df["Order Date"] = pd.to_datetime(df["Order Date"])

print("=" * 60)
print("1. OVERALL SUMMARY")
print("=" * 60)
total_sales = df["Sales"].sum()
total_profit = df["Profit"].sum()
total_orders = df["Order ID"].nunique()
avg_order_value = total_sales / total_orders
overall_margin = total_profit / total_sales * 100

print(f"Total Sales:        ${total_sales:,.2f}")
print(f"Total Profit:       ${total_profit:,.2f}")
print(f"Total Orders:       {total_orders:,}")
print(f"Avg Order Value:    ${avg_order_value:,.2f}")
print(f"Overall Margin:     {overall_margin:.2f}%")

print("\n" + "=" * 60)
print("2. YEARLY TREND")
print("=" * 60)
yearly = df.groupby("Order Year").agg(
    Sales=("Sales", "sum"),
    Profit=("Profit", "sum"),
    Orders=("Order ID", "nunique")
).round(2)
yearly["YoY Growth %"] = (yearly["Sales"].pct_change() * 100).round(2)
print(yearly)

print("\n" + "=" * 60)
print("3. MONTHLY TREND (Year-Month)")
print("=" * 60)
monthly = df.groupby("Order Year-Month").agg(
    Sales=("Sales", "sum"),
    Profit=("Profit", "sum")
).round(2)
print(f"Best month: {monthly['Sales'].idxmax()} (${monthly['Sales'].max():,.2f})")
print(f"Worst month: {monthly['Sales'].idxmin()} (${monthly['Sales'].min():,.2f})")

print("\n" + "=" * 60)
print("4. SEASONALITY (by calendar month, across all years)")
print("=" * 60)
seasonal = df.groupby("Order Month").agg(Sales=("Sales", "sum")).round(2)
seasonal["Month Name"] = pd.to_datetime(seasonal.index, format="%m").strftime("%b")
seasonal = seasonal.sort_values("Sales", ascending=False)
print(seasonal.head(3), "\n...top 3 months shown")

print("\n" + "=" * 60)
print("5. TOP CATEGORIES & SUB-CATEGORIES")
print("=" * 60)
cat = df.groupby("Category").agg(
    Sales=("Sales", "sum"),
    Profit=("Profit", "sum")
).round(2).sort_values("Sales", ascending=False)
cat["Margin %"] = (cat["Profit"] / cat["Sales"] * 100).round(2)
print(cat)

print("\nTop 5 Sub-Categories by Sales:")
subcat = df.groupby("Sub-Category").agg(
    Sales=("Sales", "sum"),
    Profit=("Profit", "sum")
).round(2).sort_values("Sales", ascending=False)
subcat["Margin %"] = (subcat["Profit"] / subcat["Sales"] * 100).round(2)
print(subcat.head(5))

print("\nWORST 3 Sub-Categories by Profit Margin (potential problem areas):")
print(subcat.sort_values("Margin %").head(3))

print("\n" + "=" * 60)
print("6. REGIONAL PERFORMANCE")
print("=" * 60)
region = df.groupby("Region").agg(
    Sales=("Sales", "sum"),
    Profit=("Profit", "sum"),
    Orders=("Order ID", "nunique")
).round(2).sort_values("Sales", ascending=False)
region["Margin %"] = (region["Profit"] / region["Sales"] * 100).round(2)
print(region)

print("\n" + "=" * 60)
print("7. DISCOUNT IMPACT ON PROFIT")
print("=" * 60)
df["Discount Band"] = pd.cut(df["Discount"], bins=[-0.01, 0, 0.15, 0.3, 1],
                               labels=["No Discount", "Low (0-15%)", "Medium (15-30%)", "High (30%+)"])
discount_impact = df.groupby("Discount Band").agg(
    Sales=("Sales", "sum"),
    Profit=("Profit", "sum"),
    AvgMargin=("Profit Margin %", "mean")
).round(2)
print(discount_impact)

print("\n" + "=" * 60)
print("8. SEGMENT PERFORMANCE")
print("=" * 60)
segment = df.groupby("Segment").agg(
    Sales=("Sales", "sum"),
    Profit=("Profit", "sum")
).round(2).sort_values("Sales", ascending=False)
print(segment)

# Save key summary tables for dashboard use
yearly.to_csv("/home/claude/summary_yearly.csv")
monthly.to_csv("/home/claude/summary_monthly.csv")
cat.to_csv("/home/claude/summary_category.csv")
region.to_csv("/home/claude/summary_region.csv")
discount_impact.to_csv("/home/claude/summary_discount.csv")

print("\n\nSummary tables saved for dashboard use.")
