import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

st.set_page_config(page_title="MCA Syndication Tracker", layout="wide")
st.title("📊 MCA Syndication Tracker – DEMO")

# --- Sidebar ---
st.sidebar.header("Select User")
user_selected = st.sidebar.selectbox("Choose a user:", ["albert", "jacob", "joel", "julian", "jaco (Admin View)"])

# --- Session state to store deals and syndications ---
if "deals" not in st.session_state:
    st.session_state.deals = pd.DataFrame({
        "Deal ID": [f"D00{i+1}" for i in range(8)],
        "Business Name": ["Joe's Plumbing", "Bella's Bakery", "Speedy Auto", "GreenTech Solar", "Luna Spa", "City Gym", "Zen Market", "FixIt Pro"],
        "Deal Size": [100000, 50000, 75000, 90000, 60000, 85000, 72000, 67000],
        "Payback": [140000, 70000, 105000, 126000, 84000, 119000, 100800, 93800],
        "Rate": [1.4] * 8,
        "Start Date": pd.date_range(start="2025-01-15", periods=8, freq='15D'),
        "Term (Days)": [140, 100, 120, 150, 110, 130, 125, 105],
        "Defaulted": [False]*7 + [True],
    })

if "syndications" not in st.session_state:
    st.session_state.syndications = pd.DataFrame({
        "Deal ID": ["D001", "D002", "D003", "D004", "D005", "D006", "D007", "D008"] * 2,
        "User": ["albert"]*4 + ["jacob"]*4 + ["joel"]*4 + ["julian"]*4,
        "% Funded": np.random.uniform(0.1, 0.5, 16).round(2)
    })

# --- Merge Data ---
merged = pd.merge(st.session_state.syndications, st.session_state.deals, on="Deal ID")
merged["Amount Funded"] = (merged["% Funded"] * merged["Deal Size"]).round(2)
merged["Expected Return"] = (merged["% Funded"] * merged["Payback"]).round(2)
merged["Payment Received"] = (merged["Expected Return"] * np.random.uniform(0.3, 0.8)).round(2)
merged["Outstanding"] = (merged["Expected Return"] - merged["Payment Received"]).round(2)

# --- Filter View ---
if user_selected != "jaco (Admin View)":
    merged = merged[merged["User"] == user_selected]

# --- User Dashboard ---
st.subheader(f"Deals for: {user_selected.capitalize()}")
col1, col2, col3 = st.columns(3)
col1.metric("Total Funded", f"${merged['Amount Funded'].sum():,.2f}")
col2.metric("Total Expected Return", f"${merged['Expected Return'].sum():,.2f}")
col3.metric("Outstanding Balance", f"${merged['Outstanding'].sum():,.2f}")

# Progress Bars with Custom Styling
st.markdown("### 📈 Payment Progress")
for _, row in merged.iterrows():
    pct_collected = row["Payment Received"] / row["Expected Return"]
    bar_color = "#4CAF50" if not row.get("Defaulted", False) else "#D32F2F"  # green or red
    bar_html = f"""
    <div style='margin-bottom: 10px;'>
        <b>{row['Business Name']}</b> — Collected: ${row['Payment Received']:,.2f} / ${row['Expected Return']:,.2f}
        <div style='background-color:#e0e0e0;border-radius:10px;height:16px;width:60%;margin-top:4px;'>
            <div style='height:100%;width:{pct_collected*100:.1f}%;background-color:{bar_color};border-radius:10px;'></div>
        </div>
    </div>"""
    st.markdown(bar_html, unsafe_allow_html=True)

# Missed payment example (manual add)
if user_selected == "jaco (Admin View)":
    st.markdown("### ❌ Missed Payment Report")
    missed_df = pd.DataFrame({
        "Deal ID": ["D008"],
        "Business Name": ["FixIt Pro"],
        "Date": [datetime.today().date()],
        "Expected Payment": [893.33],
        "Status": ["Missed"]
    })
    st.dataframe(missed_df)

# Deal Table
st.markdown("### 💼 Syndicated Deals")
st.dataframe(merged[[
    "Deal ID", "Business Name", "Deal Size", "% Funded", "Amount Funded",
    "Expected Return", "Payment Received", "Outstanding"
]])

# Admin view only — Extra Charts
if user_selected == "jaco (Admin View)":
    st.subheader("📆 Upcoming Payment Schedule")
    payment_rows = []
    for _, row in st.session_state.deals.iterrows():
        daily_payment = round(row["Payback"] / row["Term (Days)"], 2)
        for i in range(5):
            date = row["Start Date"] + timedelta(days=i)
            payment_rows.append({
                "Deal ID": row["Deal ID"],
                "Business Name": row["Business Name"],
                "Date": date.date(),
                "Expected Payment": daily_payment,
                "Status": "Paid" if not row["Defaulted"] else "Defaulted"
            })
    st.dataframe(pd.DataFrame(payment_rows))

    st.subheader("📊 Deal Funding vs Outstanding")
    chart_df = merged.groupby("Deal ID")["Amount Funded", "Outstanding"].sum().reset_index()
    st.bar_chart(chart_df.set_index("Deal ID"))

st.markdown("---")
st.caption("Demo Version – Powered by Streamlit")
