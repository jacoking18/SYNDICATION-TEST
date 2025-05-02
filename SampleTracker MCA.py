
# MCA Tracker – Calendar View + Admin Controls
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="MCA Tracker", layout="wide")
st.title("📊 MCA Syndication Tracker")

user_selected = st.sidebar.selectbox("View As", ["admin", "albert", "jacobo", "matty", "joel", "zack", "juli"])

# Sample payment status logic
def calculate_payments(deal_id, term, start_date, payback):
    daily = round(payback / term, 2)
    history = []
    for i in range(term):
        date = start_date + timedelta(days=i)
        if deal_id == "D101":
            status = "Paid"
        elif deal_id == "D102" and i == 10:
            status = "Missed"
        elif deal_id == "D102" and i == 20:
            status = "Adjusted"
        elif deal_id == "D102" and i < 25:
            status = "Paid"
        elif deal_id == "D103" and i < 12:
            status = "Paid"
        else:
            status = "Pending"
        amt = daily * 0.7 if status == "Adjusted" else daily
        history.append({"Deal ID": deal_id, "Date": date.date(), "Amount": amt, "Status": status})
    return history

# Initial data
if "deals" not in st.session_state:
    st.session_state.deals = pd.DataFrame([
        {"Deal ID": "D101", "Business Name": "Green Cafe", "Deal Size": 30000, "Rate": 1.49, "Term": 30,
         "Payback": 30000*1.49, "Start Date": datetime.today() - timedelta(days=29), "Defaulted": False},
        {"Deal ID": "D102", "Business Name": "FastFit Gym", "Deal Size": 50000, "Rate": 1.45, "Term": 60,
         "Payback": 50000*1.45, "Start Date": datetime.today() - timedelta(days=30), "Defaulted": False},
        {"Deal ID": "D103", "Business Name": "TechNova Labs", "Deal Size": 100000, "Rate": 1.50, "Term": 90,
         "Payback": 100000*1.50, "Start Date": datetime.today() - timedelta(days=20), "Defaulted": False}
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

if "payments" not in st.session_state:
    all_payments = []
    for d in st.session_state.deals.itertuples():
        all_payments.extend(calculate_payments(d._1, d.Term, d.Start_Date, d.Payback))
    st.session_state.payments = pd.DataFrame(all_payments)

def view_deal_card(deal):
    st.markdown(f"### 🔹 {deal['Business Name']} – ${deal['Deal Size']:,.0f} @ {deal['Rate']}")
    df = st.session_state.payments.query("`Deal ID` == @deal['Deal ID']")
    paid = df[df["Status"] == "Paid"].shape[0]
    pct = paid / deal["Term"]
    bar = "#4CAF50" if pct == 1 else "#2196F3"
    st.markdown(f"<div style='background:#ccc;border-radius:10px;height:18px;width:70%;margin-bottom:4px;'><div style='width:{pct*100:.1f}%;background:{bar};height:100%;border-radius:10px;'></div></div>", unsafe_allow_html=True)
    status = "💰 Fully Paid!" if pct == 1 else f"{paid}/{deal['Term']} payments"
    st.markdown(f"**{status}**")
    with st.expander("📅 Daily Payment Log"):
        for p in df.itertuples():
            icon = "✅" if p.Status == "Paid" else "❌" if p.Status == "Missed" else "✏️"
            clr = "#4CAF50" if p.Status == "Paid" else "#F44336" if p.Status == "Missed" else "#FF9800"
            st.markdown(f"<div style='display:flex;gap:20px;'><span>{p.Date}</span><span>${p.Amount:.2f}</span><span style='color:{clr};font-weight:bold;'>{icon} {p.Status}</span></div>", unsafe_allow_html=True)

if user_selected == "admin":
    st.header("👑 Admin View")
    for _, row in st.session_state.deals.iterrows():
        view_deal_card(row)
else:
    st.header(f"👤 {user_selected.capitalize()}'s Deals")
    synd = st.session_state.syndications.query("User == @user_selected")
    for _, row in pd.merge(synd, st.session_state.deals, on="Deal ID").iterrows():
        view_deal_card(row)
