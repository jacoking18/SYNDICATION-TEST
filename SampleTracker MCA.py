
# MCA Tracker - Admin Progress View and Visual Enhancements
# Author: Jacoking - April 2025

import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="MCA Tracker", layout="wide")
st.title("📊 MCA Syndication Tracker")

# ------------------------ SETUP ------------------------
user_selected = st.sidebar.selectbox("View As", ["admin", "albert", "jacobo", "matty", "joel", "zack", "juli"])

# ------------------------ INITIAL DATA ------------------------
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

    def create_deal_progress_table():
        df = st.session_state.deals.copy()
        df["Progress"] = df["Term"].apply(lambda t: int(0.6 * t))
        df["Progress Bar"] = df.apply(lambda row: f"{int(0.6 * row['Term'])}/{row['Term']}", axis=1)
        return df

    st.subheader("📋 All Deals (with Payment Progress)")
    deals_with_progress = create_deal_progress_table()
    st.dataframe(deals_with_progress)

    st.subheader("📊 Syndications")
    st.dataframe(st.session_state.syndications)

    st.subheader("👥 All Users")
    st.dataframe(pd.DataFrame(st.session_state.users, columns=["Username"]))

    st.subheader("🔍 View Any Investor's Dashboard")
    investor = st.selectbox("Choose Investor", st.session_state.users)
    syn = st.session_state.syndications[st.session_state.syndications["User"] == investor]
    merged = pd.merge(syn, st.session_state.deals, on="Deal ID")
    if merged.empty:
        st.info("No deals for this user.")
    else:
        total_inv = (merged["Percent"] / 100 * merged["Deal Size"]).sum()
        total_ret = (merged["Percent"] / 100 * merged["Payback"]).sum()
        collected = 0.6 * total_ret
        st.metric("Invested", f"${total_inv:,.2f}")
        st.metric("Expected Return", f"${total_ret:,.2f}")
        st.metric("Collected (est)", f"${collected:,.2f}")
        st.metric("Remaining", f"${(total_ret - collected):,.2f}")
        for _, row in merged.iterrows():
            paid = int(0.6 * row["Term"])
            st.markdown(f"**{row['Business Name']}** ({paid}/{row['Term']}) payments")
            st.progress(paid / row["Term"])

# ------------------------ INVESTOR VIEW ------------------------
else:
    st.header(f"👤 {user_selected.capitalize()}'s Dashboard")
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
        st.markdown("### 🧾 Your Deals Progress")
        for _, row in merged.iterrows():
            paid = int(0.6 * row["Term"])
            pct = paid / row["Term"]
            st.markdown(f"**{row['Business Name']}**")
            st.markdown(f"*Progress:* {paid}/{row['Term']} payments")
            st.markdown(f"<div style='background:#eee;width:100%;height:16px;border-radius:8px;'><div style='width:{pct * 100:.1f}%;background:#4CAF50;height:100%;border-radius:8px;'></div></div>", unsafe_allow_html=True)
