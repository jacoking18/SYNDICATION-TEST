import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

st.set_page_config(page_title="MCA Syndication Tracker", layout="wide")
st.title("📊 MCA Syndication Tracker – DEMO")

# --- Sidebar ---
st.sidebar.header("Select User")
user_selected = st.sidebar.selectbox("Choose a user:", ["albert", "jacob", "joel", "julian", "jaco (Admin View)"])

# --- Fake Deals Data ---
deals = pd.DataFrame({
    "Deal ID": [f"D00{i+1}" for i in range(8)],
    "Business Name": ["Joe's Plumbing", "Bella's Bakery", "Speedy Auto", "GreenTech Solar", "Luna Spa", "City Gym", "Zen Market", "FixIt Pro"],
    "Deal Size": [100000, 50000, 75000, 90000, 60000, 85000, 72000, 67000],
    "Payback": [140000, 70000, 105000, 126000, 84000, 119000, 100800, 93800],
    "Rate": [1.4] * 8,
    "Start Date": pd.date_range(start="2025-01-15", periods=8, freq='15D'),
    "Term (Days)": [140, 100, 120, 150, 110, 130, 125, 105],
})

# --- Fake Syndications Data ---
syndications = pd.DataFrame({
    "Deal ID": ["D001", "D002", "D003", "D004", "D005", "D006", "D007", "D008"] * 2,
    "User": ["albert"]*4 + ["jacob"]*4 + ["joel"]*4 + ["julian"]*4,
    "% Funded": np.random.uniform(0.1, 0.5, 16).round(2)
})

# Merge data
merged = pd.merge(syndications, deals, on="Deal ID")
merged["Amount Funded"] = (merged["% Funded"] * merged["Deal Size"]).round(2)
merged["Expected Return"] = (merged["% Funded"] * merged["Payback"]).round(2)
merged["Payment Received"] = (merged["Expected Return"] * np.random.uniform(0.3, 0.8)).round(2)
merged["Outstanding"] = (merged["Expected Return"] - merged["Payment Received"]).round(2)

# Filter view by user
if user_selected != "jaco (Admin View)":
    merged = merged[merged["User"] == user_selected]

# --- User Dashboard ---
st.subheader(f"Deals for: {user_selected.capitalize()}")

# Summary KPIs
col1, col2, col3 = st.columns(3)
col1.metric("Total Funded", f"${merged['Amount Funded'].sum():,.2f}")
col2.metric("Total Expected Return", f"${merged['Expected Return'].sum():,.2f}")
col3.metric("Outstanding Balance", f"${merged['Outstanding'].sum():,.2f}")

# Progress Bars
st.markdown("### 📈 Payment Progress")
for _, row in merged.iterrows():
    pct_collected = row["Payment Received"] / row["Expected Return"]
    st.write(f"**{row['Business Name']}** — Collected: ${row['Payment Received']:,.2f} / ${row['Expected Return']:,.2f}")
    st.progress(min(pct_collected, 1.0))

# Deal Table
st.markdown("### 💼 Syndicated Deals")
st.dataframe(merged[[
    "Deal ID", "Business Name", "Deal Size", "% Funded", "Amount Funded",
    "Expected Return", "Payment Received", "Outstanding"
]])

# Admin view only — Show upcoming payment schedule
if user_selected == "jaco (Admin View)":
    st.subheader("📆 Upcoming Payment Schedule")
    payment_rows = []
    for _, row in deals.iterrows():
        daily_payment = round(row["Payback"] / row["Term (Days)"], 2)
        for i in range(5):  # Show next 5 payments
            date = row["Start Date"] + timedelta(days=i)
            payment_rows.append({
                "Deal ID": row["Deal ID"],
                "Business Name": row["Business Name"],
                "Date": date.date(),
                "Expected Payment": daily_payment,
                "Status": "Paid"
            })
    st.dataframe(pd.DataFrame(payment_rows))

    # Bar chart for deal funding vs outstanding
    st.subheader("📊 Deal Funding vs Outstanding")
    chart_df = merged.groupby("Deal ID")["Amount Funded", "Outstanding"].sum().reset_index()
    st.bar_chart(chart_df.set_index("Deal ID"))

st.markdown("---")
st.caption("Demo Version – Powered by Streamlit")
