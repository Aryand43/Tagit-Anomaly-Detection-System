import streamlit as st
import pandas as pd
import os
from app.services.data_loader import load_and_clean_data
from app.services.aggregation import analyze_monthly_spend as get_monthly_spend, get_top_merchants_for_user
from app.services.visualization import plot_monthly_spend, plot_transaction_distribution, plot_top_merchants, plot_peak_hours
from app.services.anomaly_detector import detect_outliers, detect_spending_spikes, detect_duplicates, merge_anomalies, summarize_anomalies

st.set_page_config(page_title="Tagit Transaction Dashboard", layout="wide")

st.image("https://www.tagitmobile.com/wp-content/uploads/2019/02/tagits-digital-banking-solutions-logo.svg", width=180)
st.markdown("""
    <h2 style='font-family:sans-serif; color:#0B5ED7;'>Tagit Digital Banking Dashboard</h2>
    <hr style='border: 1px solid #E9ECEF;'>
""", unsafe_allow_html=True)

@st.cache_resource
def get_data():
    return load_and_clean_data("data/transactions.csv")

raw_df = get_data()
user_list = raw_df['UserID'].dropna().unique().tolist()

if "selected_user" not in st.session_state:
    st.session_state.selected_user = user_list[0] if user_list else ""
if "date_range" not in st.session_state:
    st.session_state.date_range = []
if "run_analysis" not in st.session_state:
    st.session_state.run_analysis = False

st.sidebar.title("🔎 Filter Transactions")
st.session_state.selected_user = st.sidebar.selectbox("Select UserID", sorted(user_list), index=user_list.index(st.session_state.selected_user) if st.session_state.selected_user in user_list else 0)
st.session_state.date_range = st.sidebar.date_input("Date Range", st.session_state.date_range)

if st.sidebar.button("Run Analysis"):
    st.session_state.run_analysis = True
if st.sidebar.button("Reset Filters"):
    st.session_state.selected_user = user_list[0] if user_list else ""
    st.session_state.date_range = []
    st.session_state.run_analysis = False
    st.rerun()

if not st.session_state.run_analysis:
    st.markdown("""
        <style>
            .welcome-box {
                text-align: center;
                background-color: #F8F9FA;
                padding: 30px;
                border-radius: 8px;
                color: #212529;
            }
        </style>
        <div class='welcome-box'>
            <h2>👋 Welcome to Tagit's Smart Transaction Dashboard</h2>
            <p>Use the sidebar to select a user and timeframe, then click <strong>Run Analysis</strong> to begin.</p>
            <p>You will receive insights on transaction behavior, spending trends, and anomaly detection in real-time.</p>
        </div>
    """, unsafe_allow_html=True)
    st.dataframe(raw_df.head(), use_container_width=True)

if st.session_state.run_analysis:
    user_df = raw_df[raw_df['UserID'] == st.session_state.selected_user]

    if st.session_state.date_range and len(st.session_state.date_range) == 2:
        user_df = user_df[(user_df['TXN_DATE'] >= pd.to_datetime(st.session_state.date_range[0])) &
                          (user_df['TXN_DATE'] <= pd.to_datetime(st.session_state.date_range[1]))]

    if user_df.empty:
        st.warning("No transactions found in selected range.")
    else:
        start_date = pd.to_datetime(st.session_state.date_range[0]).strftime('%b %Y') if st.session_state.date_range else "Start"
        end_date = pd.to_datetime(st.session_state.date_range[1]).strftime('%b %Y') if st.session_state.date_range else "End"

        st.markdown(f"### 📈 Analysis for User `{st.session_state.selected_user}` from {start_date} to {end_date}")

        if len(user_df) < 10:
            st.warning("⚠️ Too few transactions to run reliable anomaly detection.")

        tabs = st.tabs(["📊 Overview", "💸 Spending Patterns", "⚠️ Anomaly Insights", "📤 Exports"])

        with tabs[0]:
            st.header(f"📊 Overview for User: {st.session_state.selected_user}")
            total_txns = len(user_df)
            total_spend = user_df['TXN_AMOUNT'].sum()

            outliers = detect_outliers(user_df)
            spikes = detect_spending_spikes(user_df)
            duplicates = detect_duplicates(user_df, round_to="minute")

            merged_anomalies = merge_anomalies(outliers, spikes, duplicates)

            if not merged_anomalies.empty and 'UserID' in merged_anomalies.columns:
                summary = summarize_anomalies(merged_anomalies)
            else:
                summary = pd.DataFrame(columns=['UserID', 'Anomaly_Type', 'Anomaly_Count'])

            total_anomalies = len(merged_anomalies)

            col1, col2, col3 = st.columns(3)
            col1.metric("Total Transactions", total_txns)
            col2.metric("Total Spend", f"${total_spend:,.2f}")
            col3.metric("Total Anomalies", total_anomalies)

            if merged_anomalies.empty:
                st.info("No anomalies detected or not enough data to analyze.")
            else:
                sample_row = merged_anomalies.sort_values('TXN_AMOUNT', ascending=False).iloc[0]
                st.warning(f"🚨 High-value anomaly flagged on {sample_row['TXN_DATE'].date()} for Merchant {sample_row['MERC_TXN_ID']}")
            with st.expander("🔍 Check a New Transaction for Anomaly"):
                txn_amt = st.number_input("Transaction Amount", min_value=0.0, step=0.01)
                txn_type = st.selectbox("Transaction Type", user_df['TXN_TYPE'].dropna().unique())
                merchant_id = st.selectbox("Merchant ID", user_df['MERC_TXN_ID'].dropna().unique())
                txn_date = st.date_input("Transaction Date")
                txn_hour = st.slider("Transaction Hour", 0, 23)

                if st.button("Run Anomaly Check"):
                    sim_txn = pd.DataFrame([{
                        'UserID': st.session_state.selected_user,
                        'TXN_AMOUNT': txn_amt,
                        'TXN_TYPE': txn_type,
                        'MERC_TXN_ID': merchant_id,
                        'TXN_DATE': pd.to_datetime(txn_date) + pd.to_timedelta(txn_hour, unit='h'),
                        'Hour': txn_hour
                    }])

                    result_msgs = []

                    if not detect_outliers(pd.concat([user_df, sim_txn])).tail(1).empty:
                        result_msgs.append("Outlier")

                    threshold = user_df['TXN_AMOUNT'].quantile(0.95)
                    if txn_amt > threshold:
                        result_msgs.append("Spending Spike")

                    dup_check = user_df[
                        (user_df['TXN_DATE'].dt.floor('min') == sim_txn['TXN_DATE'].iloc[0].floor('min')) &
                        (user_df['MERC_TXN_ID'] == merchant_id) &
                        (user_df['TXN_AMOUNT'] == txn_amt)
                    ]
                    if not dup_check.empty:
                        result_msgs.append("Duplicate Transaction")

                    if result_msgs:
                        st.error(f"🚨 Anomalies detected: {', '.join(result_msgs)}")
                    else:
                        st.success("✅ No anomaly detected.")

        with tabs[1]:
            st.header("💸 Spending Patterns")
            monthly = get_monthly_spend(user_df)
            with st.container():
                st.markdown("#### Monthly Spending Trend")
                st.markdown("This chart shows how the user's monthly transaction behavior evolved over time. Peaks and lows are highlighted.")
                st.divider()
                if not monthly.empty:
                    plot_monthly_spend(monthly, st.session_state.selected_user)
            with st.container():
                st.markdown("#### Transaction Distribution")
                st.markdown("Distribution of transaction amounts — mean, median and skew are visualized.")
                st.divider()
                plot_transaction_distribution(user_df, st.session_state.selected_user)
            with st.container():
                st.markdown("#### Top Merchants")
                st.markdown("Displays the top 10 merchants this user spent the most on. Spend and transaction count shown.")
                top_merchant_volume, top_merchant_value = get_top_merchants_for_user(raw_df, st.session_state.selected_user)
                merchant_count = top_merchant_value['MERC_TXN_ID'].nunique() if not top_merchant_value.empty else 0
                st.markdown(f"**Merchants Analyzed:** {merchant_count}")
                st.divider()
                if not top_merchant_value.empty:
                    plot_top_merchants(top_merchant_value, st.session_state.selected_user)
            with st.container():
                st.markdown("#### Peak Spending Hours")
                st.markdown("Hourly distribution of spend — see when users transact most and least.")
                st.divider()
                plot_peak_hours(user_df, st.session_state.selected_user)

        with tabs[2]:
            st.header("⚠️ Anomaly Insights")
            st.subheader("Flagged Transactions")
            st.markdown("Spending spikes are transactions above the 95th percentile of past behavior. Outliers are based on Isolation Forest. Duplicates use exact matches within close timestamps.")
            anomaly_filter = st.radio("Filter by Type", ["All", "Outlier", "Spending Spike", "Duplicate Transaction"])

            filtered_anomalies = merged_anomalies
            if anomaly_filter != "All":
                filtered_anomalies = merged_anomalies[merged_anomalies['Anomaly_Type'].str.contains(anomaly_filter)]

            reviewed = st.checkbox("Mark anomalies as reviewed")
            st.data_editor(filtered_anomalies, use_container_width=True, disabled=not reviewed)

            st.divider()
            st.subheader("Anomaly Summary")
            st.dataframe(summary, use_container_width=True)
            with st.expander("ℹ️ What does this chart mean?"):
                st.markdown("""
                - **Outliers**: Detected using Isolation Forest, based on historical transaction behavior.
                - **Spending Spikes**: Transactions above the 95th percentile.
                - **Duplicates**: Same UserID + Date + Merchant + Amount, within close time windows.
                """)

        with tabs[3]:
            st.header("📤 Exports")
            st.download_button("Download Cleaned Data", data=user_df.to_csv(index=False), file_name="cleaned_data.csv")
            st.download_button("Download Anomalies", data=merged_anomalies.to_csv(index=False), file_name="anomalies.csv")
            os.makedirs("outputs/plots", exist_ok=True)
            if not monthly.empty:
                plot_monthly_spend(monthly, st.session_state.selected_user, save_path="outputs/plots")
            if not top_merchant_value.empty:
                plot_top_merchants(top_merchant_value, st.session_state.selected_user, save_path="outputs/plots")
            plot_transaction_distribution(user_df, st.session_state.selected_user, save_path="outputs/plots")
            plot_peak_hours(user_df, st.session_state.selected_user, save_path="outputs/plots")
            st.success("All visualizations saved in outputs/plots/")
