# I'll now generate the full .py file for the MCA Tracker app based on everything we discussed.

full_code = '''
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# ------------------------ PAGE CONFIG ------------------------
st.set_page_config(page_title="MCA Syndication Tracker", layout="wide")
st.title("📊 MCA Syndication Tracker")

# ------------------------ USER CREDENTIALS ------------------------
USER_CREDENTIALS = {
    "albert": "pass1",
    "jacob": "pass2",
    "joel": "pass3",
    "julian": "pass4",
    "daniel": "pass5",
    "verifier": "verifyme",
    "jaco": "adminpass"
}

# ------------------------ LOGIN ------------------------
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.subheader("🔐 Login to Access the Tracker")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.experimental_rerun()
        else:
            st.error("❌ Invalid username or password.")
    st.stop()

user_selected = st.session_state.username

# ------------------------ DATA STORAGE ------------------------
if "deals" not in st.session_state:
    if os.path.exists("deals.csv"):
        st.session_state.deals = pd.read_csv("deals.csv", parse_dates=["Start Date"])
    else:
        st.session_state.deals = pd.DataFrame(columns=["Deal ID", "Business Name", "Deal Size", "Payback", "Rate", "Start Date", "Term (Days)", "Defaulted"])

if "syndications" not in st.session_state:
    if os.path.exists("syndications.csv"):
        st.session_state.syndications = pd.read_csv("syndications.csv")
    else:
        st.session_state.syndications = pd.DataFrame(columns=["Deal ID", "User", "% Funded"])

if "users" not in st.session_state:
    st.session_state.users = ["albert", "jacob", "joel", "julian", "daniel"]

# ------------------------ FUNCTIONS ------------------------
def save_data():
    st.session_state.deals.to_csv("deals.csv", index=False)
    st.session_state.syndications.to_csv("syndications.csv", index=False)

# ------------------------ ADMIN: ADD USER ------------------------
if user_selected == "Add User":
    st.subheader("👤 Add New User")
    with st.form("add_user_form"):
        new_user = st.text_input("Enter New Username")
        add_user_submit = st.form_submit_button("Add User")
        if add_user_submit:
            if new_user.strip() and new_user.lower() not in st.session_state.users:
                st.session_state.users.append(new_user.strip().lower())
                st.success(f"User '{new_user}' added.")
            else:
                st.error("Invalid or duplicate username.")
    st.stop()

# ------------------------ USER DASHBOARDS ------------------------
if user_selected in st.session_state.users:
    merged = pd.merge(st.session_state.syndications, st.session_state.deals, on="Deal ID", how="left")
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

# ------------------------ ADMIN DASHBOARD ------------------------
if user_selected == "jaco":
    st.subheader("📋 CRM Overview")
    st.dataframe(st.session_state.deals)
    st.download_button("Download Deals CSV", st.session_state.deals.to_csv(index=False), file_name="deals.csv")
    st.markdown("---")
    styled_syndications = st.session_state.syndications.copy()
    styled_syndications["% Funded"] = styled_syndications["% Funded"].apply(lambda x: f"{x*100:.0f}%")
    st.dataframe(styled_syndications)
    st.download_button("Download Syndications CSV", st.session_state.syndications.to_csv(index=False), file_name="syndications.csv")

    st.sidebar.header("➕ Add New Deal")
    with st.sidebar.form("add_deal_form"):
        biz_name = st.text_input("Business Name")
        deal_size = st.number_input("Deal Size ($)", value=100000)
        rate = st.number_input("Rate (e.g. 1.48)", value=1.48)
        term = st.number_input("Term (Days)", value=120)
        payback = st.number_input("Payback Amount ($)", value=148000)
        start_date = st.date_input("Start Date", value=datetime.today())
        submitted = st.form_submit_button("Create Deal")
    if submitted:
        new_id = f"D{100+len(st.session_state.deals)}"
        new_deal = pd.DataFrame({
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
        save_data()
        st.success(f"New deal '{biz_name}' added successfully!")

# ------------------------ VERIFIER VIEW ------------------------
if user_selected == "verifier":
    st.subheader("🧾 Verifier Daily Check")
    selected_date = st.date_input("Select Date", datetime.today())
    deals_today = st.session_state.deals[st.session_state.deals["Start Date"] <= selected_date]
    if deals_today.empty:
        st.info("No payments due yet.")
    else:
        for idx, deal in deals_today.iterrows():
            st.write(f"**{deal['Business Name']}**: Defaulted ❌" if deal["Defaulted"] else f"{deal['Business Name']}: Paid ✅")
'''

# Save full code into a Python file
with open("/mnt/data/mca_tracker_app.py", "w") as f:
    f.write(full_code)

"/mnt/data/mca_tracker_app.py"

