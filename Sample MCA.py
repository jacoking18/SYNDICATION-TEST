
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="MCA Syndication Tracker", layout="wide")
st.title("📊 MCA Syndication Tracker")

# SESSION INITIALIZATION
if "users" not in st.session_state:
    st.session_state.users = [{"name": "admin", "role": "admin", "email": "admin@example.com", "password": "admin"}]
if "deals" not in st.session_state:
    st.session_state.deals = pd.DataFrame(columns=["Deal ID", "Business Name", "Deal Size", "Rate", "Term", "Payback", "Start Date"])
if "syndications" not in st.session_state:
    st.session_state.syndications = pd.DataFrame(columns=["Deal ID", "User", "Percent"])
if "payments" not in st.session_state:
    st.session_state.payments = pd.DataFrame(columns=["Deal ID", "User", "Date", "Paid"])

# LOGIN
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.logged_user = None

if not st.session_state.logged_in:
    st.subheader("🔐 Login")
    login_email = st.text_input("Email")
    login_pass = st.text_input("Password", type="password")
    if st.button("Login"):
        user = next((u for u in st.session_state.users if u["email"] == login_email and u["password"] == login_pass), None)
        if user:
            st.session_state.logged_in = True
            st.session_state.logged_user = user
            st.experimental_rerun()
        else:
            st.error("Invalid credentials")
    st.stop()

user = st.session_state.logged_user
st.sidebar.markdown(f"👤 Logged in as: `{user['name']}` ({user['role'].capitalize()})")

# ADMIN VIEW
if user["role"] == "admin":
    st.header("⚙️ Admin Dashboard")

    st.subheader("➕ Create New Deal")
    with st.form("create_deal_form"):
        business = st.text_input("Business Name")
        size = st.number_input("Deal Size ($)", min_value=1000, step=500)
        rate = st.number_input("Rate (e.g., 1.48)", format="%.3f")
        term = st.number_input("Term (Days)", min_value=1)
        start = st.date_input("Start Date", value=datetime.today())
        payback = size * rate
        daily_payment = payback / term
        st.markdown(f"💰 **Payback:** ${payback:,.2f}")
        st.markdown(f"📅 **{term} payments of:** ${daily_payment:,.2f}")
        submit_deal = st.form_submit_button("Create Deal")
        if submit_deal:
            deal_id = f"D{100 + len(st.session_state.deals)}"
            new = pd.DataFrame([[deal_id, business, size, rate, term, payback, start]],
                columns=["Deal ID", "Business Name", "Deal Size", "Rate", "Term", "Payback", "Start Date"])
            st.session_state.deals = pd.concat([st.session_state.deals, new], ignore_index=True)
            st.success(f"Deal {business} created!")

    st.subheader("👥 Add User")
    with st.form("add_user_form"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Role", ["investor", "verifier"])
        if st.form_submit_button("Add User"):
            st.session_state.users.append({"name": name, "email": email, "password": password, "role": role})
            st.success(f"User {name} added.")

    st.subheader("🤝 Assign Syndication")
    deal_options = st.session_state.deals["Deal ID"] + " - " + st.session_state.deals["Business Name"]
    selected_deal = st.selectbox("Select Deal", deal_options)
    selected_id = selected_deal.split(" - ")[0]
    with st.form("assign_synd_form"):
        assigned_rows = []
        for u in st.session_state.users:
            if u["role"] == "investor":
                pct = st.slider(f"{u['name']} %", 0, 100, 0)
                if pct > 0:
                    assigned_rows.append({"Deal ID": selected_id, "User": u["name"], "Percent": pct})
        if st.form_submit_button("Assign Syndicators"):
            st.session_state.syndications = pd.concat([st.session_state.syndications, pd.DataFrame(assigned_rows)], ignore_index=True)
            st.success("Syndication saved.")

    st.subheader("📊 Deal Table")
    st.dataframe(st.session_state.deals)
    st.subheader("📋 Syndication Overview")
    st.dataframe(st.session_state.syndications)
    st.subheader("🧑‍💼 Users List")
    st.dataframe(pd.DataFrame(st.session_state.users))

# INVESTOR VIEW
elif user["role"] == "investor":
    st.header("📈 Investor Dashboard")
    user_name = user["name"]
    synd = st.session_state.syndications[st.session_state.syndications["User"] == user_name]
    if synd.empty:
        st.info("You are not part of any deals yet.")
    else:
        merged = pd.merge(synd, st.session_state.deals, on="Deal ID")
        total_invested = (merged["Percent"] / 100) * merged["Deal Size"]
        total_return = (merged["Percent"] / 100) * merged["Payback"]
        collected = 0.6 * total_return  # Assume 60% collected
        st.metric("💵 Invested", f"${total_invested.sum():,.2f}")
        st.metric("💰 Expected Return", f"${total_return.sum():,.2f}")
        st.metric("📥 Collected", f"${collected.sum():,.2f}")
        st.metric("📤 Remaining", f"${(total_return - collected).sum():,.2f}")

        st.subheader("💼 Your Deals")
        for _, row in merged.iterrows():
            term = row["Term"]
            paid = int(0.6 * term)
            pct = paid / term * 100
            st.markdown(f"**{row['Business Name']}** — {paid}/{term} payments")
            st.progress(pct)

# VERIFIER VIEW
elif user["role"] == "verifier":
    st.header("🔎 Daily Verifier")
    today = datetime.today().date()
    for _, deal in st.session_state.deals.iterrows():
        for synd in st.session_state.syndications[st.session_state.syndications["Deal ID"] == deal["Deal ID"]].itertuples():
            label = f"{deal['Business Name']} – {synd.User} – {today}"
            default_paid = True
            key = f"{deal['Deal ID']}_{synd.User}_{today}"
            paid = st.checkbox(label, value=default_paid, key=key)
            if not st.session_state.payments[(st.session_state.payments["Deal ID"] == deal["Deal ID"]) &
                                              (st.session_state.payments["User"] == synd.User) &
                                              (st.session_state.payments["Date"] == today)].any().any():
                st.session_state.payments = pd.concat([
                    st.session_state.payments,
                    pd.DataFrame([[deal["Deal ID"], synd.User, today, paid]], columns=["Deal ID", "User", "Date", "Paid"])
                ], ignore_index=True)

# LOGOUT
st.sidebar.markdown("---")
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.logged_user = None
    st.experimental_rerun()
