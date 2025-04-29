import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="MCA Syndication Tracker", layout="wide")
st.title("📊 MCA Syndication Tracker – DEMO")

# --- Simulated Data ---
st.sidebar.header("Select User")
user_selected = st.sidebar.selectbox("Choose a user:", ["John Doe", "Maria Lopez", "Admin View"])

# Sample deals data
deals = pd.DataFrame({
    "Deal ID": ["D001", "D002"],
    "Business Name": ["Joe's Plumbing", "Bella's Bakery"],
    "Deal Size": [100000, 50000],
    "Payback": [140000, 70000],
    "Rate": [1.4, 1.4],
    "Start Date": [datetime(2025, 4, 1), datetime(2025, 4, 10)],
    "Term (Days)": [140, 100],
})

# Sample syndication data
syndications = pd.DataFrame({
    "Deal ID": ["D001", "D002"],
    "User": ["John Doe", "Maria Lopez"],
    "% Funded": [0.1, 0.2],
})

# Merge for display
merged = pd.merge(syndications, deals, on="Deal ID")
merged["Amount Funded"] = merged["% Funded"] * merged["Deal Size"]
merged["Expected Return"] = merged["% Funded"] * merged["Payback"]
merged["Payment Received"] = merged["Expected Return"] * 0.35  # Simulate some progress
merged["Outstanding"] = merged["Expected Return"] - merged["Payment Received"]

# Filter by user
if user_selected != "Admin View":
    merged = merged[merged["User"] == user_selected]

# Display
st.subheader(f"Deals for: {user_selected}")
st.dataframe(merged[[
    "Deal ID", "Business Name", "Deal Size", "% Funded", "Amount Funded",
    "Expected Return", "Payment Received", "Outstanding"
]])

# Admin-only payment summary
if user_selected == "Admin View":
    st.subheader("📆 Payment Schedule (Auto-filled)")
    payment_rows = []
    for _, row in deals.iterrows():
        for i in range(5):  # Show just 5 upcoming payments per deal for demo
            date = row["Start Date"] + timedelta(days=i)
            payment_rows.append({
                "Deal ID": row["Deal ID"],
                "Date": date.date(),
                "Expected Payment": round(row["Payback"] / row["Term (Days)"], 2),
                "Status": "Paid"
            })
    st.dataframe(pd.DataFrame(payment_rows))

st.markdown("---")
st.caption("Demo Version – Powered by Streamlit")
