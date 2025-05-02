
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
# ----------------- ADMIN TOOLS -----------------
if user_selected == "admin":
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
                    "Deal ID": deal_id,
                    "Business Name": biz,
                    "Deal Size": size,
                    "Rate": rate,
                    "Term": term,
                    "Payback": payback,
                    "Start Date": start,
                    "Defaulted": False
                }])
            ], ignore_index=True)
            st.success(f"Deal '{biz}' created.")

    st.sidebar.markdown("## 🤝 Assign Syndication")
    if not st.session_state.deals.empty:
        deal_names = st.session_state.deals["Deal ID"] + " - " + st.session_state.deals["Business Name"]
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
                {"Deal ID": selected_id, "User": u, "Percent": p}
                for u, p in inputs.items() if p > 0
            ]
            st.session_state.syndications = pd.concat([
                st.session_state.syndications,
                pd.DataFrame(synd_rows)
            ], ignore_index=True)
            st.success(f"Syndication assigned to deal {selected_id}.")

    st.sidebar.markdown("## 🧹 Delete User")
    if len(st.session_state.users) > 0:
        user_to_delete = st.sidebar.selectbox("Select User", st.session_state.users)
        if st.sidebar.button("Delete User"):
            st.session_state.users.remove(user_to_delete)
            st.session_state.syndications = st.session_state.syndications[st.session_state.syndications["User"] != user_to_delete]
            st.success(f"User '{user_to_delete}' deleted.")

    st.sidebar.markdown("## ❌ Delete Deal")
    if not st.session_state.deals.empty:
        deal_ids = st.session_state.deals["Deal ID"].tolist()
        deal_to_delete = st.sidebar.selectbox("Select Deal", deal_ids)
        if st.sidebar.button("Delete Deal"):
            st.session_state.deals = st.session_state.deals[st.session_state.deals["Deal ID"] != deal_to_delete]
            st.session_state.syndications = st.session_state.syndications[st.session_state.syndications["Deal ID"] != deal_to_delete]
            st.session_state.payments = st.session_state.payments[st.session_state.payments["Deal_ID"] != deal_to_delete]
            st.success(f"Deal '{deal_to_delete}' removed.")

    st.sidebar.markdown("## 🔄 Reset Syndication for a Deal")
    if not st.session_state.syndications.empty:
        synd_deal_ids = st.session_state.syndications["Deal ID"].unique().tolist()
        synd_to_clear = st.sidebar.selectbox("Clear Syndication for Deal", synd_deal_ids)
        if st.sidebar.button("Clear Syndication"):
            st.session_state.syndications = st.session_state.syndications[st.session_state.syndications["Deal ID"] != synd_to_clear]
            st.success(f"Syndications removed for deal {synd_to_clear}.")

