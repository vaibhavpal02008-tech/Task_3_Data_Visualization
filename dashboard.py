
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="Retail Sales Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Retail Sales Analytics Dashboard")
st.caption("CODE_ALPHA Internship | Task 3: Data Visualization")

# Load dataset
FILE = Path("retail_sales_dataset.csv")

@st.cache_data
def load_data():
    # Handles the quoted, tab-separated file format
    with open(FILE, "r", encoding="utf-8-sig") as f:
        lines = [line.strip() for line in f if line.strip()]

    rows = []
    for line in lines:
        if line.startswith('"') and line.endswith('"'):
            line = line[1:-1]
        rows.append(line.split("\t"))

    data = pd.DataFrame(rows[1:], columns=rows[0])
    data.columns = data.columns.str.strip()

    data["Date"] = pd.to_datetime(
        data["Date"], format="%d-%m-%Y", errors="coerce"
    )
    for col in ["Total Amount", "Quantity", "Age", "Price per Unit"]:
        data[col] = pd.to_numeric(data[col], errors="coerce")

    return data

try:
    df = load_data()
except Exception as e:
    st.error(f"Could not load the dataset: {e}")
    st.stop()

df = df.dropna(subset=["Total Amount", "Date"])

# Sidebar filters
st.sidebar.header("🔎 Dashboard Filters")

categories = sorted(df["Product Category"].dropna().unique())
selected_categories = st.sidebar.multiselect(
    "Product Category",
    categories,
    default=categories
)

genders = sorted(df["Gender"].dropna().unique())
selected_genders = st.sidebar.multiselect(
    "Gender",
    genders,
    default=genders
)

filtered = df[
    df["Product Category"].isin(selected_categories)
    & df["Gender"].isin(selected_genders)
].copy()

if filtered.empty:
    st.warning("No data matches the selected filters.")
    st.stop()

# KPI cards
total_sales = filtered["Total Amount"].sum()
transactions = len(filtered)
average_transaction = filtered["Total Amount"].mean()
units_sold = filtered["Quantity"].sum()

c1, c2, c3, c4 = st.columns(4)
c1.metric("💰 Total Sales", f"{total_sales:,.0f}")
c2.metric("🧾 Transactions", f"{transactions:,}")
c3.metric("📈 Average Transaction", f"{average_transaction:,.2f}")
c4.metric("📦 Units Sold", f"{units_sold:,.0f}")

st.divider()

# Charts
left, right = st.columns(2)

with left:
    st.subheader("Sales by Product Category")
    category_sales = (
        filtered.groupby("Product Category", as_index=False)
        ["Total Amount"].sum()
        .sort_values("Total Amount", ascending=False)
    )
    fig_category = px.bar(
        category_sales,
        x="Product Category",
        y="Total Amount",
        color="Product Category",
        title="Total Sales per Category"
    )
    st.plotly_chart(fig_category, width="stretch")

with right:
    st.subheader("Monthly Sales Trend")
    monthly = (
        filtered.assign(Month=filtered["Date"].dt.to_period("M").astype(str))
        .groupby("Month", as_index=False)["Total Amount"].sum()
        .sort_values("Month")
    )
    fig_monthly = px.line(
        monthly,
        x="Month",
        y="Total Amount",
        markers=True,
        title="Sales by Month"
    )
    st.plotly_chart(fig_monthly, width="stretch")

left2, right2 = st.columns(2)

with left2:
    st.subheader("Average Transaction by Gender")
    gender_sales = (
        filtered.groupby("Gender", as_index=False)["Total Amount"].mean()
    )
    fig_gender = px.bar(
        gender_sales,
        x="Gender",
        y="Total Amount",
        color="Gender",
        title="Average Transaction Amount"
    )
    st.plotly_chart(fig_gender, width="stretch")

with right2:
    st.subheader("Customer Age vs Transaction Amount")
    fig_age = px.scatter(
        filtered.dropna(subset=["Age"]),
        x="Age",
        y="Total Amount",
        color="Gender",
        hover_data=["Product Category", "Quantity"],
        title="Age vs Transaction Amount"
    )
    st.plotly_chart(fig_age, width="stretch")

# Data table and download
st.divider()
st.subheader("📋 Filtered Sales Data")
st.dataframe(filtered, width="stretch", hide_index=True)

csv_data = filtered.to_csv(index=False).encode("utf-8")
st.download_button(
    label="⬇️ Download Filtered Data as CSV",
    data=csv_data,
    file_name="filtered_retail_sales.csv",
    mime="text/csv"
)

st.success("Dashboard loaded successfully!")
