# MCA Syndication Tracker – Full System (OrgMeter-style)
# Author: Jacoking - May 2025

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="MCA Tracker", layout="wide")
st.title("📊 MCA Syndication Tracker")

# -------- Sidebar Login --------
user_selected = st.sidebar.selectbox("View As", ["admin", "albert", "jacobo", "matty", "joel", "zack", "juli"])

# -------- Initialize Data --------
if "users" not in st.session_state:
    st.session_state.users = ["albert", "jacobo", "matty", "joel", "zack", "juli"]

if "deals" not in st.session_state:
    st.session_state.deals = pd.DataFrame([
        {"Deal_ID": "D101", "Business Name": "Green Cafe", "Deal Size": 30000, "Rate": 1.49, "Term": 30,
         "Payback": 30000 * 1.49, "Start_Date": datetime.today() - timedelta(days=29), "Defaulted": False},
        {"Deal_ID": "D102", "Business Name": "FastFit Gym", "Deal Size": 50000, "Rate": 1.45, "Term": 60,
         "Payback": 50000 * 1.45, "Start_Date": datetime.today() - timedelta(days=45), "Defaulted": False},
        {"Deal_ID": "D103", "Business Name": "TechNova Labs", "Deal Size": 100000, "Rate": 1.50, "Term": 90,
         "Payback": 100000 * 1.50, "Start_Date": datetime.today() - timedelta(days=25), "Defaulted": False}
    ])

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

# -------- Deal Display Function --------
def show_deal_details(deal):
    st.markdown(f"### 🔷 {deal['Business Name']} – ${deal['Deal Size']:,.0f} @ {deal['Rate']} for {deal['Term']} days")
    paid_count = st.session_state.payments.query("Deal_ID == @deal['Deal_ID'] and Status == 'Paid'").shape[0]
    progress = paid_count / deal["Term"]
    color = "#4CAF50" if progress == 1 else "#2196F3"
    bg_bar = f"<div style='background:#ccc;border-radius:10px;height:20px;width:100%;'><div style='width:{progress*100:.1f}%;height:100%;background:{color};border-radius:10px;'></div></div>"
    st.markdown(bg_bar, unsafe_allow_html=True)
    st.markdown(f"**{paid_count}/{deal['Term']} payments** {'💰' if progress == 1 else ''}")

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

# -------- Views --------
if user_selected == "admin":
    st.header("👑 Admin Dashboard")
    for _, d in st.session_state.deals.iterrows():
        show_deal_details(d)

    # Admin Tools (Sidebar)
    st.sidebar.markdown("## ➕ Add User")
    with st.sidebar.form("add_user"):
        new_user = st.text_input("Username").lower().strip()
        if st.form_submit_button("Add") and new_user:
            if new_user not in st.session_state.users:
                st.session_state.users.append(new_user)
                st.success(f"User '{new_user}' added.")
            else:
                st.warning("User already exists.")

    st.sidebar.markdown("## 💼 Add Deal")
    with st.sidebar.form("add_deal"):
        biz = st.text_input("Business Name")
        size = st.number_input("Deal Size", min_value=0)
        rate = st.number_input("Rate", value=1.5)
        term = st.number_input("Term", min_value=1)
        start = st.date_input("Start Date", value=datetime.today())
        submit = st.form_submit_button("Create Deal")
        if submit and biz:
            new_id = f"D{100 + len(st.session_state.deals)}"
            payback = size * rate
            new_deal = pd.DataFrame([{
                "Deal_ID": new_id, "Business Name": biz, "Deal Size": size,
                "Rate": rate, "Term": term, "Payback": payback,
                "Start_Date": start, "Defaulted": False
            }])
            st.session_state.deals = pd.concat([st.session_state.deals, new_deal], ignore_index=True)
            st.session_state.payments = pd.concat([
                st.session_state.payments,
                pd.DataFrame(calculate_payments(new_id, term, start, payback))
            ], ignore_index=True)
            st.success(f"Deal '{biz}' created.")

    st.sidebar.markdown("## 🤝 Assign Syndication")
    deal_list = st.session_state.deals["Deal_ID"] + " - " + st.session_state.deals["Business Name"]
    selected_deal = st.sidebar.selectbox("Select Deal", deal_list)
    deal_id = selected_deal.split(" - ")[0]
    with st.sidebar.form("assign_form"):
        st.write("Assign % (Total ≤ 100%)")
        inputs = {u: st.slider(u, 0, 100, 0) for u in st.session_state.users}
        total = sum(inputs.values())
        st.markdown(f"**Total: {total}%**")
        if st.form_submit_button("Assign") and total <= 100:
            new_rows = [{"Deal_ID": deal_id, "User": u, "Percent": p} for u, p in inputs.items() if p > 0]
            st.session_state.syndications = pd.concat([
                st.session_state.syndications,
                pd.DataFrame(new_rows)
            ], ignore_index=True)
            st.success("Syndication Assigned.")

else:
    st.header(f"👤 {user_selected.capitalize()}'s Dashboard")
    syn = st.session_state.syndications.query("User == @user_selected")
    my_deals = pd.merge(syn, st.session_state.deals, on="Deal_ID")
    if my_deals.empty:
        st.info("No deals assigned yet.")
    else:
        total_inv = (my_deals["Percent"] / 100 * my_deals["Deal Size"]).sum()
        total_ret = (my_deals["Percent"] / 100 * my_deals["Payback"]).sum()
        collected = 0.6 * total_ret
        st.metric("Invested", f"${total_inv:,.2f}")
        st.metric("Expected Return", f"${total_ret:,.2f}")
        st.metric("Collected", f"${collected:,.2f}")
        st.metric("Remaining", f"${total_ret - collected:,.2f}")
        for _, d in my_deals.iterrows():
            show_deal_details(d)
