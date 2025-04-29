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
    })

if "syndications" not in st.session_state:
    st.session_state.syndications = pd.DataFrame({
        "Deal ID": ["D001", "D002", "D003", "D004", "D005", "D006", "D007", "D008"] * 2,
        "User": ["albert"]*4 + ["jacob"]*4 + ["joel"]*4 + ["julian"]*4,
        "% Funded": np.random.uniform(0.1, 0.5, 16).round(2)
    })

# --- Admin Input for New Deals ---
if user_selected == "jaco (Admin View)":
    st.sidebar.markdown("---")
    st.sidebar.header("➕ Add New Deal")
    with st.sidebar.form("add_deal_form"):
        biz_name = st.text_input("Business Name", "Maria Bakery")
        deal_size = st.number_input("Deal Size ($)", value=100000)
        rate = st.number_input("Rate (e.g. 1.48)", value=1.48)
        term = st.number_input("Term (Days)", value=120)
        payback = st.number_input("Payback Amount ($)", value=149000)
        start_date = st.date_input("Start Date", value=datetime.today())
        submitted = st.form_submit_button("Create Deal")

    if submitted:
        new_id = f"D{len(st.session_state.deals)+1:03}"
        new_deal = pd.DataFrame.from_dict({
            "Deal ID": [new_id],
            "Business Name": [biz_name],
            "Deal Size": [deal_size],
            "Payback": [payback],
            "Rate": [rate],
            "Start Date": [start_date],
            "Term (Days)": [term],
        })
        st.session_state.deals = pd.concat([st.session_state.deals, new_deal], ignore_index=True)
        st.success(f"New deal '{biz_name}' added successfully!")

    st.sidebar.markdown("---")
    st.sidebar.header("👥 Syndicate Deal")
    if not st.session_state.deals.empty:
        selected_deal = st.sidebar.selectbox("Select Deal to Syndicate", st.session_state.deals["Deal ID"])
        with st.sidebar.form("syndicate_form"):
            st.markdown("Input % participation for each user")
            percent_albert = st.slider("Albert %", 0, 100, 30)
            percent_julian = st.slider("Julian %", 0, 100, 30)
            percent_joel = st.slider("Joel %", 0, 100, 10)
            percent_jacob = st.slider("Jacob %", 0, 100, 20)
            percent_daniel = st.slider("Daniel %", 0, 100, 10)
            syndicate_submitted = st.form_submit_button("Add Syndications")

        if syndicate_submitted:
            new_rows = pd.DataFrame({
                "Deal ID": [selected_deal]*5,
                "User": ["albert", "julian", "joel", "jacob", "daniel"],
                "% Funded": [percent_albert, percent_julian, percent_joel, percent_jacob, percent_daniel]
            })
            new_rows["% Funded"] = new_rows["% Funded"] / 100  # convert to decimal
            st.session_state.syndications = pd.concat([st.session_state.syndications, new_rows], ignore_index=True)
            st.success(f"Syndication added to Deal {selected_deal}")

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
                "Status": "Paid"
            })
    st.dataframe(pd.DataFrame(payment_rows))

    st.subheader("📊 Deal Funding vs Outstanding")
    chart_df = merged.groupby("Deal ID")["Amount Funded", "Outstanding"].sum().reset_index()
    st.bar_chart(chart_df.set_index("Deal ID"))

st.markdown("---")
st.caption("Demo Version – Powered by Streamlit")
