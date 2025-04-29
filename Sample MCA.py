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

if "users" not in st.session_state:
    st.session_state.users = ["albert", "jacob", "joel", "julian", "daniel"]

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
