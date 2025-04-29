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
                    "% Funded": round(pct / 100, 2)
                })
    st.session_state.syndications = pd.DataFrame(syndications_list)

# --- Users Initialization ---

# --- User Dashboard View ---
if user_selected in st.session_state.users:
    merged = pd.merge(st.session_state.syndications, st.session_state.deals, on="Deal ID")
    user_deals = merged[merged["User"] == user_selected]

    st.subheader(f"💼 Deals for: {user_selected.capitalize()}")
    if user_deals.empty:
        st.info("No deals assigned yet.")
    else:
        col1, col2, col3 = st.columns(3)
        total_funded = user_deals["% Funded"] * user_deals["Deal Size"]
        total_payback = user_deals["% Funded"] * user_deals["Payback"]
        col1.metric("Total Funded", f"${total_funded.sum():,.0f}")
        col2.metric("Total Expected Return", f"${total_payback.sum():,.0f}")
        col3.metric("Outstanding Balance", f"${(total_payback.sum()*0.6):,.0f}")

        st.markdown("### 📊 Payment Progress")
        for _, row in user_deals.iterrows():
            expected_return = row["% Funded"] * row["Payback"]
            payments_total = row["Term (Days)"]
            payments_made = int(0.6 * payments_total)
            pct_collected = payments_made / payments_total
            bar_color = "#4CAF50" if not row["Defaulted"] else "#F44336"
            st.markdown(f"""
            <div style='margin-bottom: 10px;'>
                <b>{row['Business Name']}</b> — Collected: ({payments_made}/{payments_total}) payments
                <div style='background-color:#e0e0e0;border-radius:10px;height:16px;width:60%;margin-top:4px;'>
                    <div style='height:100%;width:{pct_collected*100:.1f}%;background-color:{bar_color};border-radius:10px;'></div>
                </div>
            </div>""", unsafe_allow_html=True)
if "users" not in st.session_state:
    st.session_state.users = ["albert", "jacob", "joel", "julian", "daniel"]

# --- Admin Functionality ---
if user_selected == "jaco (Admin View)":
    st.markdown("<h2 style='color:#4CAF50;'>📋 CRM Overview</h2>", unsafe_allow_html=True)
    st.markdown("<h4 style='color:#2196F3;'>📄 All Deals</h4>", unsafe_allow_html=True)
    st.dataframe(st.session_state.deals)
    st.markdown("<h4 style='color:#673AB7;'>🤝 All Syndications</h4>", unsafe_allow_html=True)
        styled_syndications = st.session_state.syndications.copy()
    styled_syndications["% Funded"] = styled_syndications["% Funded"].apply(lambda x: f"{x*100:.0f}%")
    st.dataframe(styled_syndications)
    st.markdown("---")
    st.sidebar.markdown("---")
    st.sidebar.markdown("<h4 style='margin-top:20px;'>➕ <u>Add New Deal</u></h4>", unsafe_allow_html=True)
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
    st.sidebar.markdown("<h4 style='margin-top:30px;'>👥 <u>Assign Syndicators to Deal</u></h4>", unsafe_allow_html=True)
    if not st.session_state.deals.empty:
        deal_options = st.session_state.deals.apply(lambda row: f"{row['Deal ID']} - {row['Business Name']}", axis=1)
        selected_option = st.sidebar.selectbox("Select Deal", deal_options)
        synd_deal_id = selected_option.split(" - ")[0]
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
