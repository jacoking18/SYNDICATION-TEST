import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

st.set_page_config(page_title="MCA Syndication Tracker", layout="wide")
st.title("📊 MCA Syndication Tracker – DEMO")

st.sidebar.header("Select User")
user_selected = st.sidebar.selectbox("Choose a user:", ["albert", "jacob", "joel", "julian", "daniel", "verifier", "jaco (Admin View)"])

# --- Deals Initialization ---
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

# --- Syndications Initialization ---
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

# --- Users Initialization ---
if "users" not in st.session_state:
    st.session_state.users = ["albert", "jacob", "joel", "julian", "daniel"]

# --- Admin Functionality ---
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
            "Start Date": [pd.to_datetime(start_date)],
            "Term (Days)": [term],
            "Defaulted": [False]
        })
        st.session_state.deals = pd.concat([st.session_state.deals, new_deal], ignore_index=True)
        st.success(f"New deal '{biz_name}' added successfully!")

    st.sidebar.markdown("---")
    st.sidebar.header("👥 Assign Syndicators to Deal")
    if not st.session_state.deals.empty:
        synd_deal_id = st.sidebar.selectbox("Select Deal", st.session_state.deals["Deal ID"])
        with st.sidebar.form("assign_syndication_form"):
            st.markdown("Input % participation (must total ≤ 100%)")
            synd_inputs = {}
            for user in st.session_state.users:
                synd_inputs[user] = st.slider(f"{user.capitalize()} %", 0, 100, 0)
            total_pct_value = sum(synd_inputs.values())
            if total_pct_value > 100:
                st.markdown(f"<span style='color:red;font-weight:bold;'>⚠️ Total: {total_pct_value}% — exceeds 100%</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"**Current Total: {total_pct_value}%**")
            assign_submit = st.form_submit_button("Assign Syndicators")

        if assign_submit:
            if total_pct_value <= 100:
                synd_rows = []
                for user, pct in synd_inputs.items():
                    if pct > 0:
                        synd_rows.append({
                            "Deal ID": synd_deal_id,
                            "User": user,
                            "% Funded": pct / 100
                        })
                st.session_state.syndications = pd.concat([st.session_state.syndications, pd.DataFrame(synd_rows)], ignore_index=True)
                st.success("Syndicators assigned successfully.")
            else:
                st.error("Total % exceeds 100%. Please adjust.")
