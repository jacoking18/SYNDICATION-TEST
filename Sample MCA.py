...

# --- VERIFIER Tab ---
if user_selected == "verifier":
    st.subheader("📅 Daily Payment Verifier Dashboard")
    st.markdown("Every payment is assumed to be 'YES'. Please confirm or update as 'NO' for missed payments.")

    today = datetime.today().date()
    selected_date = st.date_input("Select Date to Review Payments", today)

    # Generate today's expected payments
    verifier_rows = []
    for _, row in st.session_state.deals.iterrows():
        start = row["Start Date"].date()
        days_since_start = (selected_date - start).days
        if 0 <= days_since_start < row["Term (Days)"]:
            verifier_rows.append({
                "Deal ID": row["Deal ID"],
                "Business Name": row["Business Name"],
                "Expected Payment": round(row["Payback"] / row["Term (Days)"], 2),
                "Date": selected_date,
                "Status": "YES"  # assumed paid
            })

    verifier_df = pd.DataFrame(verifier_rows)
    if not verifier_df.empty:
        st.dataframe(verifier_df)
        st.markdown("Select rows below to mark as missed payments:")
        missed_indices = st.multiselect("Select rows to mark as 'NO' (missed)", verifier_df.index.tolist())

        if missed_indices:
            verifier_df.loc[missed_indices, "Status"] = "NO"
            st.warning("The following deals were marked as 'NO':")
            st.dataframe(verifier_df.loc[missed_indices])
        else:
            st.success("All payments assumed paid for today.")
    else:
        st.info("No expected payments to verify for the selected date.")
