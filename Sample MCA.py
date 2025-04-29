
# UPDATED MCA SYNDICATION TRACKER - Admin Sidebar Enhancement Included
# Author: Jacoking - April 2025

import streamlit as st
import pandas as pd
from datetime import datetime

# ------------------------ CONFIG ------------------------
st.set_page_config(page_title="MCA Syndication Tracker", layout="wide")
st.title("📊 MCA Syndication Tracker")

# ------------------------ CREDENTIALS ------------------------
USER_CREDENTIALS = {
    "albert": "pass1",
    "jacob": "pass2",
    "joel": "pass3",
    "julian": "pass4",
    "daniel": "pass5",
    "verifier": "verifyme",
    "jaco": "adminpass"
}

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

# ------------------------ STATE INIT ------------------------
if "deals" not in st.session_state:
    st.session_state.deals = pd.DataFrame(columns=["Deal ID", "Business Name", "Deal Size", "Payback", "Rate", "Start Date", "Term (Days)", "Defaulted"])
if "syndications" not in st.session_state:
    st.session_state.syndications = pd.DataFrame(columns=["Deal ID", "User", "% Funded"])
if "users" not in st.session_state:
    st.session_state.users = ["albert", "jacob", "joel", "julian", "daniel"]

# ------------------------ ADMIN VIEW ------------------------
if user_selected == "jaco":
    st.markdown("### 📋 CRM Overview")
    st.dataframe(st.session_state.deals)
    st.dataframe(st.session_state.syndications)

    # --- SIDEBAR FOR ADMIN ACTIONS ---
    st.sidebar.markdown("## ➕ Add New Deal")
    
    
    with st.sidebar.form("add_deal_form"):
        biz_name = st.text_input("Business Name")
        deal_size = st.number_input("Deal Size ($)", value=10000, step=100, format="%.0f")
        rate = st.number_input("Rate (e.g. 1.499)", value=1.499, format="%.3f")
        term = st.number_input("Term (Days)", value=120)
        start_date = st.date_input("Start Date", value=datetime.today())

        # Live calculation
        payback = deal_size * rate
        per_payment = payback / term if term else 0

        st.markdown(f"<br><b>📈 Payback Amount:</b> <span style='color:#4CAF50;'>${payback:,.2f}</span>", unsafe_allow_html=True)
        st.markdown(f"<b>📆 {term} payments of:</b> <span style='color:#2196F3;'>${per_payment:,.2f}</span>", unsafe_allow_html=True)

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
        st.success(f"New deal '{biz_name}' added.")

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
        st.success(f"New deal '{biz_name}' added.")

    # --- ADD USER ---
    st.sidebar.markdown("## 👤 Add New User")
    with st.sidebar.form("add_user_form"):
        new_user = st.text_input("New Username")
        add_user_submit = st.form_submit_button("Add User")
    if add_user_submit:
        if new_user.strip() and new_user.lower() not in st.session_state.users:
            st.session_state.users.append(new_user.strip().lower())
            st.success(f"User '{new_user}' added.")
        else:
            st.error("Invalid or duplicate user.")

    # --- ASSIGN SYNDICATION ---
    st.sidebar.markdown("## 🤝 Assign Syndicators")
    if not st.session_state.deals.empty:
        deal_options = st.session_state.deals.apply(lambda row: f"{row['Deal ID']} - {row['Business Name']}", axis=1)
        selected_option = st.sidebar.selectbox("Select Deal", deal_options)
        synd_deal_id = selected_option.split(" - ")[0]
        with st.sidebar.form("assign_syndication_form"):
            st.markdown("Assign % to each user (total ≤ 100%)")
            synd_inputs = {}
            for user in st.session_state.users:
                synd_inputs[user] = st.slider(f"{user.capitalize()} %", 0, 100, 0)
            total_pct = sum(synd_inputs.values())
            if total_pct > 100:
                st.error(f"⚠️ Total {total_pct}% exceeds 100%.")
            else:
                st.success(f"✅ Total: {total_pct}%")
            assign_submit = st.form_submit_button("Assign")
        if assign_submit and total_pct <= 100:
            rows = []
            for user, pct in synd_inputs.items():
                if pct > 0:
                    rows.append({"Deal ID": synd_deal_id, "User": user, "% Funded": pct / 100})
            st.session_state.syndications = pd.concat([st.session_state.syndications, pd.DataFrame(rows)], ignore_index=True)
            st.success("Syndicators assigned successfully.")

# === CONTINUED FROM EARLIER ===

    # --- VIEW USERS TABLE ---
    
    st.sidebar.markdown("## 👥 View All Users")
    if st.sidebar.button("Show Users Table"):
        user_data = pd.DataFrame({
            "Username": st.session_state.users,
            "Password": [USER_CREDENTIALS.get(u, "unknown") for u in st.session_state.users]
        })
        st.subheader("🔐 Registered Users (Admin Only)")
        st.dataframe(user_data)



    # --- DELETE DEAL ---
    st.sidebar.markdown("## 🗑 Delete Deal")
    if not st.session_state.deals.empty:
        deal_to_delete = st.sidebar.selectbox("Select Deal to Delete", st.session_state.deals["Deal ID"])
        if st.sidebar.button("Delete Deal"):
            st.session_state.deals = st.session_state.deals[st.session_state.deals["Deal ID"] != deal_to_delete]
            st.session_state.syndications = st.session_state.syndications[st.session_state.syndications["Deal ID"] != deal_to_delete]
            st.success(f"Deleted deal {deal_to_delete}")

    # --- DELETE USER ---
    st.sidebar.markdown("## 🗑 Delete User")
    user_to_delete = st.sidebar.selectbox("Select User to Delete", [u for u in st.session_state.users if u != 'jaco'])
    if st.sidebar.button("Delete User"):
        st.session_state.users.remove(user_to_delete)
        st.session_state.syndications = st.session_state.syndications[st.session_state.syndications["User"] != user_to_delete]
        st.success(f"User '{user_to_delete}' removed from system.")

# ------------------------ USER VIEW ------------------------
elif user_selected in st.session_state.users:
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
        col2.metric("Expected Return", f"${total_payback.sum():,.0f}")
        col3.metric("Outstanding", f"${(total_payback.sum()*0.6):,.0f}")
        st.markdown("### 📊 Progress")
        for _, row in user_deals.iterrows():
            biz = row['Business Name']
            term = int(row['Term (Days)'])
            made = int(0.6 * term)
            pct = made / term
            bar = "#4CAF50" if not row["Defaulted"] else "#F44336"
            st.markdown(f"<b>{biz}</b> — Collected: ({made}/{term}) payments", unsafe_allow_html=True)
            st.markdown(f"""
            <div style='background:#ddd;border-radius:10px;width:60%;height:16px;'>
                <div style='width:{pct*100:.1f}%;background:{bar};height:100%;border-radius:10px;'></div>
            </div>
            """, unsafe_allow_html=True)

    if user_selected == "jaco (Admin View)":
        st.sidebar.markdown("## 👥 View & Delete Users")
        if st.sidebar.button("Show Users Table"):
            st.dataframe(pd.DataFrame(st.session_state.users, columns=["Username"]))
        user_to_delete = st.sidebar.selectbox("Select User to Delete", st.session_state.users)
        if st.sidebar.button("Delete User"):
            if user_to_delete in st.session_state.users:
                st.session_state.users.remove(user_to_delete)
                st.session_state.syndications = st.session_state.syndications[st.session_state.syndications["User"] != user_to_delete]
                st.success(f"User '{user_to_delete}' deleted.")

        st.sidebar.markdown("---")
        st.sidebar.markdown("## 📄 View & Delete Deals")
        if st.sidebar.button("Show Deal Table"):
            st.dataframe(st.session_state.deals)
        if not st.session_state.deals.empty:
            deal_ids = st.session_state.deals["Deal ID"].tolist()
            deal_to_delete = st.sidebar.selectbox("Select Deal to Delete", deal_ids)
            if st.sidebar.button("Delete Deal"):
                st.session_state.deals = st.session_state.deals[st.session_state.deals["Deal ID"] != deal_to_delete]
                st.session_state.syndications = st.session_state.syndications[st.session_state.syndications["Deal ID"] != deal_to_delete]
                st.success(f"Deal '{deal_to_delete}' deleted.")

        st.sidebar.markdown("---")
        st.sidebar.markdown("## 🤝 View & Delete Syndications")
        if st.sidebar.button("Show Syndications Table"):
            st.dataframe(st.session_state.syndications)
        if not st.session_state.syndications.empty:
            synd_ids = st.session_state.syndications["Deal ID"].unique().tolist()
            synd_to_delete = st.sidebar.selectbox("Select Deal's Syndications to Delete", synd_ids)
            if st.sidebar.button("Delete Syndication"):
                st.session_state.syndications = st.session_state.syndications[st.session_state.syndications["Deal ID"] != synd_to_delete]
                st.success(f"All syndicators removed from deal '{synd_to_delete}'.")
