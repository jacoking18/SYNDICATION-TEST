# MCA Syndication Tracker – Full System (OrgMeter-style)
# Author: Jacoking - May 2025

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="MCA Tracker", layout="wide")
st.title("MCA Syndication Tracker")

# -------- Sidebar Login --------
user_selected = st.sidebar.selectbox("View As", ["admin"] + st.session_state.get("users", []))

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
        status = "Pending"
        payments.append({
            "Deal_ID": deal_id,
            "Date": date.date(),
            "Amount": daily,
            "Status": status
        })
    return payments

if "payments" not in st.session_state:
    all_payments = []
    for d in st.session_state.deals.itertuples():
        all_payments.extend(calculate_payments(d.Deal_ID, d.Term, d.Start_Date, d.Payback))
    st.session_state.payments = pd.DataFrame(all_payments)

# -------- Financial Totals per User --------
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

# -------- Deal Display Function --------
def show_deal_details(deal):
    st.markdown(f"### {deal['Business Name']} – ${deal['Deal Size']:,.0f} @ {deal['Rate']} for {deal['Term']} days")
    cal = st.session_state.payments.query("Deal_ID == @deal['Deal_ID']").copy()
    paid_count = cal.query("Status == 'Paid'").shape[0]
    progress = paid_count / deal["Term"]
    color = "#4CAF50" if progress == 1 else "#2196F3"
    bg_bar = f"<div style='background:#ccc;border-radius:10px;height:20px;width:100%;'><div style='width:{progress*100:.1f}%;height:100%;background:{color};border-radius:10px;'></div></div>"
    st.markdown(bg_bar, unsafe_allow_html=True)
    st.markdown(f"**{paid_count}/{deal['Term']} payments**" + (" 💰" if progress == 1 else ""))

    with st.expander("Daily Payment Calendar"):
        cal = cal.sort_values("Date")
        for i, row in cal.iterrows():
            color = "#4CAF50" if row["Status"] == "Paid" else "#F44336" if row["Status"] == "Missed" else "#FF9800"
            cols = st.columns([3, 2, 2, 2])
            cols[0].markdown(f"{row['Date']}")
            cols[1].markdown(f"${row['Amount']:.2f}")
            if user_selected == "admin":
                status_options = ["Paid", "Missed", "Adjusted"]
                current_status = row["Status"] if row["Status"] in status_options else "Paid"
                try:
                    status_index = status_options.index(current_status)
                except ValueError:
                    status_index = 0
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
                                    "Status": "Pending"
                                }])
                            ], ignore_index=True)
                if new_status != row["Status"] or new_amount != row["Amount"]:
                    st.session_state.payments.at[i, "Status"] = new_status
                    st.session_state.payments.at[i, "Amount"] = new_amount
            else:
                cols[2].markdown(f"<span style='color:{color};font-weight:bold;'>{row['Status']}</span>", unsafe_allow_html=True)

# -------- Show Deals --------
if user_selected == "admin":
    st.header("Admin Dashboard")
    for _, d in st.session_state.deals.iterrows():
        show_deal_details(d)

    st.header("Syndicator Metrics")
    balances = calculate_user_balances()
    for u, b in balances.items():
        st.markdown(f"**{u.capitalize()}**: Drawn = ${b['Drawn']:.2f} | Available = ${b['Available']:.2f}")

    st.sidebar.markdown("## ➕ Add User")
    with st.sidebar.form("add_user_form"):
        new_user = st.text_input("Username").lower().strip()
        if st.form_submit_button("Add User") and new_user:
            if new_user not in st.session_state.users:
                st.session_state.users.append(new_user)
                st.success(f"User '{new_user}' added.")
            else:
                st.warning("User already exists.")

    st.sidebar.markdown("## 💼 Add Deal")
    with st.sidebar.form("add_deal_form"):
        biz = st.text_input("Business Name")
        size = st.number_input("Deal Size ($)", min_value=0)
        rate = st.number_input("Rate (e.g. 1.499)", value=1.499, format="%.3f")
        term = st.number_input("Term (Days)", min_value=1)
        start = st.date_input("Start Date", value=datetime.today())
        if st.form_submit_button("Create Deal") and biz:
            deal_id = f"D{100 + len(st.session_state.deals)}"
            payback = size * rate
            st.session_state.deals = pd.concat([
                st.session_state.deals,
                pd.DataFrame([{
                    "Deal_ID": deal_id,
                    "Business Name": biz,
                    "Deal Size": size,
                    "Rate": rate,
                    "Term": term,
                    "Payback": payback,
                    "Start_Date": start,
                    "Defaulted": False
                }])
            ], ignore_index=True)
            st.success(f"Deal '{biz}' created.")

    st.sidebar.markdown("## 🤝 Assign Syndication")
    if not st.session_state.deals.empty:
        deal_names = st.session_state.deals["Deal_ID"] + " - " + st.session_state.deals["Business Name"]
        selected_deal = st.sidebar.selectbox("Select Deal", deal_names)
        selected_id = selected_deal.split(" - ")[0]
        with st.sidebar.form("assign_form"):
            st.markdown("Assign % (total ≤ 100%)")
            inputs = {u: st.slider(f"{u}", 0, 100, 0) for u in st.session_state.users}
            total = sum(inputs.values())
            st.markdown(f"**Total Assigned: {total}%**")
            assign = st.form_submit_button("Assign")
        if assign and total <= 100:
            synd_rows = [
                {"Deal_ID": selected_id, "User": u, "Percent": p}
                for u, p in inputs.items() if p > 0
            ]
            st.session_state.syndications = pd.concat([
                st.session_state.syndications,
                pd.DataFrame(synd_rows)
            ], ignore_index=True)
            st.success(f"Syndication assigned to deal {selected_id}.")

    # -------- Delete Block --------
    st.sidebar.markdown("## 🗑️ Delete")
    delete_type = st.sidebar.selectbox("Delete Type", ["Deal", "User", "Syndication"])
    if delete_type == "Deal":
        deal_ids = st.session_state.deals["Deal_ID"].tolist()
        selected = st.sidebar.selectbox("Select Deal to Delete", deal_ids)
        if st.sidebar.button("Delete Deal"):
            st.session_state.deals = st.session_state.deals[st.session_state.deals["Deal_ID"] != selected]
            st.session_state.payments = st.session_state.payments[st.session_state.payments["Deal_ID"] != selected]
            st.session_state.syndications = st.session_state.syndications[st.session_state.syndications["Deal_ID"] != selected]
            st.success(f"Deleted deal {selected}")
    elif delete_type == "User":
        selected = st.sidebar.selectbox("Select User to Delete", st.session_state.users)
        if st.sidebar.button("Delete User"):
            st.session_state.users.remove(selected)
            st.session_state.syndications = st.session_state.syndications[st.session_state.syndications["User"] != selected]
            st.success(f"Deleted user {selected}")
    elif delete_type == "Syndication":
        unique_synd = st.session_state.syndications.drop_duplicates(subset=["Deal_ID", "User"])
        options = [f"{row['Deal_ID']} - {row['User']}" for _, row in unique_synd.iterrows()]
        selected = st.sidebar.selectbox("Select Syndication to Delete", options)
        deal_id, user = selected.split(" - ")
        if st.sidebar.button("Delete Syndication"):
            mask = (st.session_state.syndications["Deal_ID"] == deal_id) & (st.session_state.syndications["User"] == user)
            st.session_state.syndications = st.session_state.syndications[~mask]
            st.success(f"Deleted syndication {deal_id} - {user}")

else:
    st.header(f"{user_selected.capitalize()}'s Deals")
    synd = st.session_state.syndications.query("User == @user_selected")
    user_deals = pd.merge(synd, st.session_state.deals, on="Deal_ID")
    for _, d in user_deals.iterrows():
        show_deal_details(d)
