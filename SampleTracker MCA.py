
# MCA Tracker – Enhanced Admin Tools and Visuals
# Author: Jacoking – April 2025

import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="MCA Tracker", layout="wide")
st.title("📊 MCA Syndication Tracker")

user_selected = st.sidebar.selectbox("View As", ["admin", "albert", "jacobo", "matty", "joel", "zack", "juli"])

# ------------------------ DATA INIT ------------------------
if "deals" not in st.session_state:
    st.session_state.deals = pd.DataFrame([
        {"Deal ID": "D101", "Business Name": "Green Cafe", "Deal Size": 30000, "Rate": 1.49, "Term": 30,
         "Payback": 30000 * 1.49, "Start Date": datetime.today(), "Defaulted": False},
        {"Deal ID": "D102", "Business Name": "FastFit Gym", "Deal Size": 50000, "Rate": 1.45, "Term": 60,
         "Payback": 50000 * 1.45, "Start Date": datetime.today(), "Defaulted": False},
        {"Deal ID": "D103", "Business Name": "TechNova Labs", "Deal Size": 100000, "Rate": 1.50, "Term": 90,
         "Payback": 100000 * 1.50, "Start Date": datetime.today(), "Defaulted": False}
    ])

if "users" not in st.session_state:
    st.session_state.users = ["albert", "jacobo", "matty", "joel", "zack", "juli"]

if "syndications" not in st.session_state:
    st.session_state.syndications = pd.DataFrame([
        {"Deal ID": "D101", "User": "albert", "Percent": 40},
        {"Deal ID": "D101", "User": "jacobo", "Percent": 60},
        {"Deal ID": "D102", "User": "matty", "Percent": 30},
        {"Deal ID": "D102", "User": "joel", "Percent": 30},
        {"Deal ID": "D102", "User": "zack", "Percent": 40},
        {"Deal ID": "D103", "User": "juli", "Percent": 50},
        {"Deal ID": "D103", "User": "jacobo", "Percent": 50}
    ])

# ------------------------ ADMIN VIEW ------------------------
if user_selected == "admin":
    st.header("👑 Admin Dashboard")

    st.sidebar.markdown("## ➕ Add User")
    with st.sidebar.form("add_user_form"):
        new_user = st.text_input("Username")
        if st.form_submit_button("Add User") and new_user:
            if new_user not in st.session_state.users:
                st.session_state.users.append(new_user.lower())
                st.success(f"Added user '{new_user}'")

    st.sidebar.markdown("## ➕ Add Deal")
    with st.sidebar.form("add_deal_form"):
        biz_name = st.text_input("Business Name")
        size = st.number_input("Deal Size", min_value=0)
        rate = st.number_input("Rate", value=1.50, format="%.3f")
        term = st.number_input("Term (Days)", min_value=1)
        date = st.date_input("Start Date", value=datetime.today())
        if st.form_submit_button("Create Deal"):
            new_id = f"D{100 + len(st.session_state.deals)}"
            payback = size * rate
            new_row = pd.DataFrame([{
                "Deal ID": new_id,
                "Business Name": biz_name,
                "Deal Size": size,
                "Rate": rate,
                "Term": term,
                "Payback": payback,
                "Start Date": date,
                "Defaulted": False
            }])
            st.session_state.deals = pd.concat([st.session_state.deals, new_row], ignore_index=True)
            st.success(f"Deal '{biz_name}' added.")

    st.sidebar.markdown("## 🤝 Add Syndication")
    if not st.session_state.deals.empty:
        deal_names = st.session_state.deals["Deal ID"] + " - " + st.session_state.deals["Business Name"]
        selected_deal = st.sidebar.selectbox("Select Deal", deal_names)
        deal_id = selected_deal.split(" - ")[0]
        with st.sidebar.form("assign_form"):
            inputs = {}
            for u in st.session_state.users:
                inputs[u] = st.slider(f"{u.capitalize()} %", 0, 100, 0)
            total = sum(inputs.values())
            st.markdown(f"**Total Assigned:** {total}%")
            if st.form_submit_button("Assign") and total <= 100:
                rows = [{"Deal ID": deal_id, "User": user, "Percent": pct} for user, pct in inputs.items() if pct > 0]
                st.session_state.syndications = pd.concat([st.session_state.syndications, pd.DataFrame(rows)], ignore_index=True)
                st.success("Syndication updated.")

    st.subheader("📋 All Deals")
    for _, row in st.session_state.deals.iterrows():
        st.markdown(f"### 🔹 {row['Business Name']} (${row['Deal Size']:,.0f}) – {row['Term']} Days @ {row['Rate']}")
        st.write(f"**Payback:** ${row['Payback']:,.2f}")
        paid = int(0.6 * row['Term'])
        st.markdown(f"*Payments:* {paid}/{row['Term']}")
        st.progress(paid / row['Term'])
        deal_synds = st.session_state.syndications[st.session_state.syndications["Deal ID"] == row["Deal ID"]]
        if not deal_synds.empty:
            st.markdown("**Investors in this Deal:**")
            for _, s in deal_synds.iterrows():
                amount = s["Percent"] / 100 * row["Deal Size"]
                st.markdown(f"- {s['User'].capitalize()} — {s['Percent']}% → ${amount:,.0f}")
        else:
            st.info("No investors yet.")
        st.divider()

# ------------------------ INVESTOR VIEW ------------------------
else:
    st.header(f"👤 {user_selected.capitalize()}'s Deal Overview")
    syn = st.session_state.syndications[st.session_state.syndications["User"] == user_selected]
    merged = pd.merge(syn, st.session_state.deals, on="Deal ID")
    if merged.empty:
        st.info("No deals assigned.")
    else:
        total_inv = (merged["Percent"] / 100 * merged["Deal Size"]).sum()
        total_ret = (merged["Percent"] / 100 * merged["Payback"]).sum()
        collected = 0.6 * total_ret
        st.metric("Invested", f"${total_inv:,.2f}")
        st.metric("Expected Return", f"${total_ret:,.2f}")
        st.metric("Collected", f"${collected:,.2f}")
        st.metric("Remaining", f"${(total_ret - collected):,.2f}")
        st.subheader("📊 Your Deals")
        for _, row in merged.iterrows():
            biz = row["Business Name"]
            pct = row["Percent"]
            inv = row["Percent"] / 100 * row["Deal Size"]
            term = row["Term"]
            paid = int(0.6 * term)
            st.markdown(f"### 🏢 {biz} – {pct}% → ${inv:,.0f}")
            st.markdown(f"*Payments:* {paid}/{term}")
            st.progress(paid / term)
