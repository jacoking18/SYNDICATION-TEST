import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

st.set_page_config(page_title="MCA Syndication Tracker", layout="wide")
st.title("📊 MCA Syndication Tracker – DEMO")

# --- Sidebar ---
st.sidebar.header("Select User")
user_selected = st.sidebar.selectbox("Choose a user:", ["albert", "jacob", "joel", "julian", "daniel", "verifier", "jaco (Admin View)"])

# --- Session state initialization ---
if "deals" not in st.session_state:
    st.session_state.deals = pd.DataFrame({
        "Deal ID": [f"D{100+i}" for i in range(10)],
        "Business Name": [
            "Joe's Plumbing", "Bella's Bakery", "Speedy Auto", "GreenTech Solar",
            "Luna Spa", "City Gym", "Zen Market", "FixIt Pro", "Super Coffee", "Nova Law"
        ],
        "Deal Size": [100000, 50000, 75000, 90000, 60000, 85000, 72000, 67000, 95000, 80000],
        "Payback": [140000, 70000, 105000, 126000, 84000, 119000, 100800, 93800, 133000, 112000],
        "Rate": [1.4]*10,
        "Start Date": pd.date_range(start="2024-12-01", periods=10, freq='10D'),
        "Term (Days)": [140, 100, 120, 150, 110, 130, 125, 105, 160, 115],
        "Defaulted": [False, False, False, True, False, False, False, True, False, False]
    })

if "syndications" not in st.session_state:
    deals = st.session_state.deals
    syndications_list = []
    users = ["albert", "jacob", "joel", "julian", "daniel"]
    percentages = [
        [40, 20, 20, 20, 0],
        [30, 30, 20, 20, 0],
        [25, 25, 25, 25, 0],
        [50, 30, 10, 10, 0],
        [40, 30, 20, 10, 0],
        [20, 20, 20, 20, 20],
        [30, 25, 25, 20, 0],
        [60, 20, 10, 10, 0],
        [35, 35, 20, 10, 0],
        [40, 30, 20, 10, 0]
    ]
    for idx, deal in deals.iterrows():
        for user, pct in zip(users, percentages[idx]):
            if pct > 0:
                syndications_list.append({
                    "Deal ID": deal["Deal ID"],
                    "User": user,
                    "% Funded": pct / 100
                })
    st.session_state.syndications = pd.DataFrame(syndications_list)

if "users" not in st.session_state:
    st.session_state.users = ["albert", "jacob", "joel", "julian", "daniel"]

# --- Admin functionality ---
if user_selected == "jaco (Admin View)":
    st.sidebar.markdown("---")
    st.sidebar.header("➕ Add New Deal")
    with st.sidebar.form("add_deal_form"):
        biz_name = st.text_input("Business Name", "New Business")
        deal_size = st.number_input("Deal Size ($)", value=100000)
        rate = st.number_input("Rate (e.g. 1.48)", value=1.48)
        term = st.number_input("Term (Days)", value=120)
        payback = st.number_input("Payback Amount ($)", value=149000)
        start_date = st.date_input("Start Date", value=datetime.today())
        submitted = st.form_submit_button("Create Deal")

    if submitted:
        new_id = f"D{100+len(st.session_state.deals)}"
        new_deal = pd.DataFrame.from_dict({
            "Deal ID": [new_id],
            "Business Name": [biz_name],
            "Deal Size": [deal_size],
            "Payback": [payback],
            "Rate": [rate],
            "Start Date": [start_date],
            "Term (Days)": [term],
            "Defaulted": [False]
        })
        st.session_state.deals = pd.concat([st.session_state.deals, new_deal], ignore_index=True)
        st.success(f"New deal '{biz_name}' added successfully!")

# --- Verifier Tab ---
if user_selected == "verifier":
    st.subheader("📅 Daily Payment Verifier Dashboard")
    today = datetime.today().date()
    selected_date = st.date_input("Select Date to Review Payments", today)

    verifier_rows = []
    for _, row in st.session_state.deals.iterrows():
        start = row["Start Date"].date()
        days_since_start = (selected_date - start).days
        if 0 <= days_since_start < row["Term (Days)"]:
            verifier_rows.append({
                "Deal ID": row["Deal ID"],
                "Business Name": row["Business Name"],
                "Expected Payment": round(row["Payback"] / row["Term (Days)"], 2),
                "Date": selected_date,
                "Status": "YES"
            })

    verifier_df = pd.DataFrame(verifier_rows)
    if not verifier_df.empty:
        st.dataframe(verifier_df)
        missed_indices = st.multiselect("Select rows to mark as 'NO' (missed)", verifier_df.index.tolist())
        if missed_indices:
            verifier_df.loc[missed_indices, "Status"] = "NO"
            st.warning("The following deals were marked as 'NO':")
            st.dataframe(verifier_df.loc[missed_indices])
        else:
            st.success("All payments assumed paid for today.")
    else:
        st.info("No expected payments to verify for the selected date.")

# --- Main Dashboard ---
if user_selected not in ["verifier", "jaco (Admin View)"]:
    merged = pd.merge(st.session_state.syndications, st.session_state.deals, on="Deal ID")
    merged = merged[merged["User"] == user_selected]

    st.subheader(f"Deals for: {user_selected.capitalize()}")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Funded", f"${merged['% Funded'].mul(merged['Deal Size']).sum():,.2f}")
    col2.metric("Total Payback Expected", f"${merged['% Funded'].mul(merged['Payback']).sum():,.2f}")
    col3.metric("Outstanding Balance", f"${merged['% Funded'].mul(merged['Payback']).sum()*0.6:,.2f}")
    col4.metric("Total Collected as of {datetime.today().date()}", f"${merged['% Funded'].mul(merged['Payback']).sum()*0.4:,.2f}")

    st.markdown("### 📈 Payment Progress")
    for _, row in merged.iterrows():
        expected_return = row["% Funded"] * row["Payback"]
        payments_total = row["Term (Days)"]
        payments_made = int(0.6 * payments_total)  # Assume 60% progress
        pct_collected = payments_made / payments_total
        bar_color = "#4CAF50" if not row["Defaulted"] else "#D32F2F"
        st.markdown(f"""
        <div style='margin-bottom: 10px;'>
            <b>{row['Business Name']}</b> — Collected: ({payments_made}/{payments_total}) payments
            <div style='background-color:#e0e0e0;border-radius:10px;height:16px;width:60%;margin-top:4px;'>
                <div style='height:100%;width:{pct_collected*100:.1f}%;background-color:{bar_color};border-radius:10px;'></div>
            </div>
        </div>""", unsafe_allow_html=True)

# --- Admin CRM Total View ---
if user_selected == "jaco (Admin View)":
    st.subheader("📋 Total Deals in CRM")
    st.dataframe(st.session_state.deals)
    st.dataframe(st.session_state.syndications)

st.markdown("---")
st.caption("Demo Version — CAPNOW MCA Tracker")
