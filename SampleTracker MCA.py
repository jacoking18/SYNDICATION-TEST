
# MCA Tracker – Collapsible Calendar with Visual Completion
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="MCA Tracker", layout="wide")
st.title("📊 MCA Syndication Tracker")

user_selected = st.sidebar.selectbox("View As", ["admin", "albert", "jacobo", "matty", "joel", "zack", "juli"])

# ---------------- DATA ----------------
if "deals" not in st.session_state:
    st.session_state.deals = pd.DataFrame([
        {"Deal_ID": "D101", "Business Name": "Green Cafe", "Deal Size": 30000, "Rate": 1.49, "Term": 30,
         "Payback": 30000 * 1.49, "Start_Date": datetime.today() - timedelta(days=29), "Defaulted": False},
        {"Deal_ID": "D102", "Business Name": "FastFit Gym", "Deal Size": 50000, "Rate": 1.45, "Term": 60,
         "Payback": 50000 * 1.45, "Start_Date": datetime.today() - timedelta(days=30), "Defaulted": False},
        {"Deal_ID": "D103", "Business Name": "TechNova Labs", "Deal Size": 100000, "Rate": 1.50, "Term": 90,
         "Payback": 100000 * 1.50, "Start_Date": datetime.today() - timedelta(days=20), "Defaulted": False}
    ])

if "users" not in st.session_state:
    st.session_state.users = ["albert", "jacobo", "matty", "joel", "zack", "juli"]

if "syndications" not in st.session_state:
    st.session_state.syndications = pd.DataFrame([
        {"Deal_ID": "D101", "User": "albert", "Percent": 40},
        {"Deal_ID": "D101", "User": "jacobo", "Percent": 60},
        {"Deal_ID": "D102", "User": "matty", "Percent": 30},
        {"Deal_ID": "D102", "User": "joel", "Percent": 30},
        {"Deal_ID": "D102", "User": "zack", "Percent": 40},
        {"Deal_ID": "D103", "User": "juli", "Percent": 50},
        {"Deal_ID": "D103", "User": "jacobo", "Percent": 50}
    ])

def calculate_payments(deal_id, term, start_date, payback):
    daily = round(payback / term, 2)
    payments = []
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
        payments.append({
            "Deal_ID": deal_id,
            "Date": date.date(),
            "Amount": daily if status != "Adjusted" else round(daily * 0.7, 2),
            "Status": status
        })
    return payments

if "payments" not in st.session_state:
    all_payments = []
    for d in st.session_state.deals.itertuples():
        all_payments.extend(calculate_payments(d.Deal_ID, d.Term, d.Start_Date, d.Payback))
    st.session_state.payments = pd.DataFrame(all_payments)

# ---------------- VIEW ----------------
def show_deal_details(deal):
    st.markdown(f"### 🔹 {deal['Business Name']} – ${deal['Deal Size']:,.0f} @ {deal['Rate']} for {deal['Term']} days")
    paid_count = st.session_state.payments.query("Deal_ID == @deal['Deal_ID'] and Status == 'Paid'").shape[0]
    progress = paid_count / deal["Term"]
    color = "#4CAF50" if progress == 1 else "#2196F3"
    st.markdown(f"<div style='background:#ddd;border-radius:10px;height:18px;width:70%;'><div style='height:100%;width:{progress*100:.1f}%;background:{color};border-radius:10px;'></div></div>", unsafe_allow_html=True)
    status_text = "💰 Completed!" if progress == 1 else f"{paid_count}/{deal['Term']} payments"
    st.markdown(f"**{status_text}**")

    with st.expander("📅 Daily Payment Calendar"):
        cal = st.session_state.payments.query("Deal_ID == @deal['Deal_ID']").copy()
        cal = cal.sort_values("Date")
        for row in cal.itertuples():
            icon = "✅" if row.Status == "Paid" else "❌" if row.Status == "Missed" else "✏️"
            color = "#4CAF50" if row.Status == "Paid" else "#F44336" if row.Status == "Missed" else "#FF9800"
            st.markdown(
                f"<div style='display:flex;gap:20px;'><span>{row.Date}</span><span>${row.Amount:.2f}</span><span style='color:{color};font-weight:bold;'>{icon} {row.Status}</span></div>",
                unsafe_allow_html=True
            )

if user_selected == "admin":
    st.header("👑 Admin Dashboard")
    for _, d in st.session_state.deals.iterrows():
        show_deal_details(d)
else:
    st.header(f"👤 {user_selected.capitalize()}'s Deals")
    synd = st.session_state.syndications.query("User == @user_selected")
    user_deals = pd.merge(synd, st.session_state.deals, on="Deal_ID")
    for _, d in user_deals.iterrows():
        show_deal_details(d)
