import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

st.set_page_config(page_title="MCA Syndication Tracker", layout="wide")
st.title("📊 MCA Syndication Tracker – DEMO")

# --- Sidebar ---
st.sidebar.header("Select User")
user_selected = st.sidebar.selectbox("Choose a user:", ["albert", "jacob", "joel", "julian", "verifier", "jaco (Admin View)"])

# --- Session state initialization ---
if "deals" not in st.session_state:
    st.session_state.deals = pd.DataFrame({
        "Deal ID": [f"D00{i+1}" for i in range(8)],
        "Business Name": ["Joe's Plumbing", "Bella's Bakery", "Speedy Auto", "GreenTech Solar", "Luna Spa", "City Gym", "Zen Market", "FixIt Pro"],
        "Deal Size": [100000, 50000, 75000, 90000, 60000, 85000, 72000, 67000],
        "Payback": [140000, 70000, 105000, 126000, 84000, 119000, 100800, 93800],
        "Rate": [1.4] * 8,
        "Start Date": pd.date_range(start="2024-12-01", periods=8, freq='15D'),
        "Term (Days)": [140, 100, 120, 150, 110, 130, 125, 105],
        "Defaulted": [False]*7 + [True],
    })

if "syndications" not in st.session_state:
    st.session_state.syndications = pd.DataFrame({
        "Deal ID": ["D001", "D002", "D003", "D004", "D005", "D006", "D007", "D008"] * 2,
        "User": ["albert"]*4 + ["jacob"]*4 + ["joel"]*4 + ["julian"]*4,
        "% Funded": np.random.uniform(0.1, 0.5, 16).round(2)
    })

if "users" not in st.session_state:
    st.session_state.users = ["albert", "jacob", "joel", "julian", "daniel"]

# --- Admin functionality ---
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
            "Defaulted": [False]
        })
        st.session_state.deals = pd.concat([st.session_state.deals, new_deal], ignore_index=True)
        st.success(f"New deal '{biz_name}' added successfully!")

    st.sidebar.markdown("---")
    st.sidebar.header("👥 Syndicate Deal")
    if not st.session_state.deals.empty:
        selected_deal = st.sidebar.selectbox("Select Deal to Syndicate", st.session_state.deals["Deal ID"])
        with st.sidebar.form("syndicate_form"):
            st.markdown("Input % participation for each user")
            inputs = {}
            for user in st.session_state.users:
                inputs[user] = st.slider(f"{user.capitalize()} %", 0, 100, 0)
            syndicate_submitted = st.form_submit_button("Add Syndications")

        if syndicate_submitted:
            synd_data = {"Deal ID": [], "User": [], "% Funded": []}
            for user, pct in inputs.items():
                if pct > 0:
                    synd_data["Deal ID"].append(selected_deal)
                    synd_data["User"].append(user)
                    synd_data["% Funded"].append(pct / 100)
            new_rows = pd.DataFrame(synd_data)
            st.session_state.syndications = pd.concat([st.session_state.syndications, new_rows], ignore_index=True)
            st.success(f"Syndication added to Deal {selected_deal}")

    st.sidebar.markdown("---")
    st.sidebar.header("👤 Add New User")
    with st.sidebar.form("add_user_form"):
        new_user = st.text_input("New User Email or Name")
        add_user_submit = st.form_submit_button("Add User")

    if add_user_submit and new_user:
        if new_user not in st.session_state.users:
            st.session_state.users.append(new_user)
            st.success(f"User '{new_user}' added successfully!")
        else:
            st.warning("User already exists.")

# --- VERIFIER Tab ---
if user_selected == "verifier":
    st.subheader("📅 Daily Payment Verifier Dashboard")
    st.markdown("Every payment is assumed to be 'YES'. Please confirm or update as 'NO' for missed payments.")

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
        st.markdown("Select rows below to mark as missed payments:")
        missed_indices = st.multiselect("Select rows to mark as 'NO' (missed)", verifier_df.index.tolist())

        if missed_indices:
            verifier_df.loc[missed_indices, "Status"] = "NO"
            st.warning("The following deals were marked as 'NO':")
            st.dataframe(verifier_df.loc[missed_indices])
        else:
            st.success("All payments assumed paid for today.")
    else:
        st.info("No expected payments to verify for the selected date.")
