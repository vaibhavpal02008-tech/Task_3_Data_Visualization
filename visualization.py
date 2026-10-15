
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

OUTPUT = Path("outputs")
OUTPUT.mkdir(exist_ok=True)
# Load the dataset correctly

from pathlib import Path

FILE = Path("retail_sales_dataset.csv")

with open(FILE, "r", encoding="utf-8-sig") as f:
    lines = [line.strip() for line in f if line.strip()]

rows = []

for line in lines:
    # Remove quotes surrounding the entire row
    if line.startswith('"') and line.endswith('"'):
        line = line[1:-1]

    rows.append(line.split("\t"))

df = pd.DataFrame(
    rows[1:],
    columns=[col.strip() for col in rows[0]]
)

# Convert columns to correct data types
df["Date"] = pd.to_datetime(
    df["Date"],
    format="%d-%m-%Y",
    errors="coerce"
)

df["Total Amount"] = pd.to_numeric(
    df["Total Amount"], errors="coerce"
)

df["Age"] = pd.to_numeric(df["Age"], errors="coerce")

print("Columns detected:", df.columns.tolist())
print(df.head())

# Fix date format
df["Date"] = pd.to_datetime(
    df["Date"],
    format="%d-%m-%Y",
    errors="coerce"
)

# Check the loaded columns
print("Columns:", df.columns.tolist())
print(df.head())
# 1. Sales by category
category_sales = df.groupby("Product Category")["Total Amount"].sum().sort_values()

plt.figure(figsize=(9, 5))
category_sales.plot(kind="barh")
plt.title("Total Sales by Product Category")
plt.xlabel("Total Sales")
plt.ylabel("Category")
plt.tight_layout()
plt.savefig(OUTPUT / "sales_by_category.png", dpi=150)
plt.close()

# 2. Monthly sales trend
monthly = (
    df.dropna(subset=["Date"])
      .assign(Month=lambda x: x["Date"].dt.to_period("M").astype(str))
      .groupby("Month")["Total Amount"].sum()
)

plt.figure(figsize=(10, 5))
monthly.plot(marker="o")
plt.title("Monthly Sales Trend")
plt.xlabel("Month")
plt.ylabel("Total Sales")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(OUTPUT / "monthly_sales.png", dpi=150)
plt.close()

# 3. Sales by product category and gender
plt.figure(figsize=(9, 5))
sns.barplot(data=df, x="Product Category",
            y="Total Amount", hue="Gender", errorbar=None)
plt.title("Sales by Category and Gender")
plt.xticks(rotation=20)
plt.tight_layout()
plt.savefig(OUTPUT / "category_gender.png", dpi=150)
plt.close()

# 4. Age and total amount relationship
plt.figure(figsize=(9, 5))
sns.scatterplot(data=df, x="Age", y="Total Amount",
                hue="Gender", alpha=0.7)
plt.title("Customer Age vs Transaction Amount")
plt.tight_layout()
plt.savefig(OUTPUT / "age_vs_sales.png", dpi=150)
plt.close()

print("Visualization completed successfully!")
print("Charts saved in the outputs folder.")
print("\nHighest-sales category:", category_sales.idxmax())
print("Total sales:", df["Total Amount"].sum())
