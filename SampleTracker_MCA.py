# MCA Syndication Tracker – Full System (OrgMeter-style)
# Author: Jacoking - May 2025

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="MCA Tracker", layout="wide")
st.title("MCA Syndication Tracker")

# -------- Sidebar Login --------
if "users" not in st.session_state:
    st.session_state.users = ["albert", "jacobo", "matty", "joel", "zack", "juli"]

user_selected = st.sidebar.selectbox("View As", ["admin"] + st.session_state.users)

# -------- Initialize Data --------
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

if "modified_deals" not in st.session_state:
    st.session_state.modified_deals = {}

def calculate_payments(deal_id, term, start_date, payback):
    daily = round(payback / term, 2)
    return [{
        "Deal_ID": deal_id,
        "Date": (start_date + timedelta(days=i)).date(),
        "Amount": daily,
        "Status": ""
    } for i in range(term)]

if "payments" not in st.session_state:
    all_payments = []
    for d in st.session_state.deals.itertuples():
        all_payments.extend(calculate_payments(d.Deal_ID, d.Term, d.Start_Date, d.Payback))
    st.session_state.payments = pd.DataFrame(all_payments)

def calculate_user_balances():
    paid_df = st.session_state.payments.query("Status == 'Paid'")
    totals = {}
    for user in st.session_state.users:
        user_deals = st.session_state.syndications.query("User == @user")
        total_drawn = 0
        total_payable = 0
        for row in user_deals.itertuples():
            deal = st.session_state.deals.query("Deal_ID == @row.Deal_ID").iloc[0]
            paid = paid_df.query("Deal_ID == @row.Deal_ID")
            percent = row.Percent / 100
            total_drawn += paid["Amount"].sum() * percent
            total_payable += deal["Payback"] * percent
        totals[user] = {
            "Drawn": total_drawn,
            "Available": total_payable - total_drawn
        }
    return totals

def show_deal_details(deal):
    modified = st.session_state.modified_deals.get(deal['Deal_ID'], {})
    term = modified.get("Term", deal["Term"])
    payback = modified.get("Payback", deal["Payback"])
    st.markdown(f"### {deal['Business Name']} – ${deal['Deal Size']:,.0f} @ {deal['Rate']} for {deal['Term']} days" +
                (f" → Modified: {term} days" if term != deal['Term'] else ""))
    
    cal = st.session_state.payments.query("Deal_ID == @deal['Deal_ID']").copy()
    paid_count = cal.query("Status == 'Paid'").shape[0]
    progress = paid_count / term
    color = "#4CAF50" if progress == 1 else "#2196F3"
    st.markdown(f"<div style='background:#ccc;border-radius:10px;height:20px;width:100%;'><div style='width:{progress*100:.1f}%;height:100%;background:{color};border-radius:10px;'></div></div>", unsafe_allow_html=True)
    st.markdown(f"**{paid_count}/{term} payments**" + (" 💰" if progress == 1 else ""))

    with st.expander("Daily Payment Calendar"):
        cal = cal.sort_values("Date")
        for i, row in cal.iterrows():
            color = "#4CAF50" if row["Status"] == "Paid" else "#F44336" if row["Status"] == "Missed" else "#FF9800"
            cols = st.columns([3, 2, 2, 2])
            cols[0].markdown(f"{row['Date']}")
            cols[1].markdown(f"${row['Amount']:.2f}")
            if user_selected == "admin":
                status_options = ["", "Paid", "Missed", "Adjusted"]
                status_index = status_options.index(row["Status"]) if row["Status"] in status_options else 0
                new_status = cols[2].selectbox("", status_options, index=status_index, key=f"status_{deal['Deal_ID']}_{i}")
                new_amount = row["Amount"]
                if new_status == "Adjusted":
                    new_amount = cols[3].number_input("Adj. Amt", value=row["Amount"], key=f"amt_{deal['Deal_ID']}_{i}")
                    extend_days = cols[3].number_input("Extend Days", min_value=0, value=0, key=f"extend_{deal['Deal_ID']}_{i}")
                    if extend_days > 0:
                        for j in range(extend_days):
                            next_date = row['Date'] + timedelta(days=j+1)
                            st.session_state.payments = pd.concat([
                                st.session_state.payments,
                                pd.DataFrame([{
                                    "Deal_ID": deal['Deal_ID'],
                                    "Date": next_date,
                                    "Amount": new_amount,
                                    "Status": ""
                                }])
                            ], ignore_index=True)
                        new_term = term + extend_days
                        new_payback = payback + (new_amount * extend_days)
                        st.session_state.modified_deals[deal['Deal_ID']] = {"Term": new_term, "Payback": new_payback}
                st.session_state.payments.at[i, "Status"] = new_status
                st.session_state.payments.at[i, "Amount"] = new_amount
            else:
                cols[2].markdown(f"<span style='color:{color};font-weight:bold;'>{row['Status']}</span>", unsafe_allow_html=True)

# -------- Show Admin or User Interface --------
if user_selected == "admin":
    st.header("Admin Dashboard")
    for _, d in st.session_state.deals.iterrows():
        show_deal_details(d)

    st.header("Syndicator Metrics")
    balances = calculate_user_balances()
    for u, b in balances.items():
        st.markdown(f"**{u.capitalize()}**: Drawn = ${b['Drawn']:.2f} | Available = ${b['Available']:.2f}")

    # Admin Sidebar Tools
    st.sidebar.header("Admin Tools")
    new_user = st.sidebar.text_input("New Username")
    if st.sidebar.button("Add User") and new_user and new_user not in st.session_state.users:
        st.session_state.users.append(new_user)
        st.success(f"User '{new_user}' added.")

    with st.sidebar.form("add_deal_form"):
        name = st.text_input("Business Name")
        size = st.number_input("Deal Size", min_value=0)
        rate = st.number_input("Rate", value=1.5)
        term = st.number_input("Term", min_value=1)
        start = st.date_input("Start Date", value=datetime.today())
        if st.form_submit_button("Create Deal") and name:
            did = f"D{100 + len(st.session_state.deals)}"
            payback = size * rate
            new_deal = {"Deal_ID": did, "Business Name": name, "Deal Size": size, "Rate": rate, "Term": term, "Payback": payback, "Start_Date": start, "Defaulted": False}
            st.session_state.deals = pd.concat([st.session_state.deals, pd.DataFrame([new_deal])], ignore_index=True)
            st.success(f"Deal '{name}' created.")

    if not st.session_state.deals.empty:
        deal_names = st.session_state.deals["Deal_ID"] + " - " + st.session_state.deals["Business Name"]
        selected_deal = st.sidebar.selectbox("Select Deal", deal_names)
        selected_id = selected_deal.split(" - ")[0]
        with st.sidebar.form("assign_form"):
            st.markdown("Assign % (total ≤ 100%)")
            inputs = {u: st.slider(f"{u}", 0, 100, 0) for u in st.session_state.users}
            total = sum(inputs.values())
            st.markdown(f"**Total Assigned: {total}%**")
            if st.form_submit_button("Assign") and total <= 100:
                synd_rows = [{"Deal_ID": selected_id, "User": u, "Percent": p} for u, p in inputs.items() if p > 0]
                st.session_state.syndications = pd.concat([st.session_state.syndications, pd.DataFrame(synd_rows)], ignore_index=True)
                st.success(f"Syndication assigned to deal {selected_id}.")

else:
    st.header(f"{user_selected.capitalize()}'s Deals")
    synd = st.session_state.syndications.query("User == @user_selected")
    user_deals = pd.merge(synd, st.session_state.deals, on="Deal_ID")
    for _, d in user_deals.iterrows():
        show_deal_details(d)
