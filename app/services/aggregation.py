import pandas as pd

# 1. Total Spend per User
def calculate_total_spend(df):
    total_spend = df.groupby('UserID')['TXN_AMOUNT'].sum().reset_index()
    total_spend.rename(columns={'TXN_AMOUNT': 'Total_Spend'}, inplace=True)
    return total_spend

# 2. Monthly Spend Trend (Per User)
def analyze_monthly_spend(df):
    monthly_spend = (
        df.groupby(['UserID', df['YearMonth'].astype(str)])['TXN_AMOUNT']
        .sum()
        .reset_index()
        .rename(columns={'TXN_AMOUNT': 'Monthly_Spend'})
    )
    return monthly_spend

# 3. Histogram of Transaction Amounts
def transaction_amount_distribution(df):
    txn_distribution = df['TXN_AMOUNT']
    return txn_distribution

# 4. Spend by Transaction Type
def spend_by_transaction_type(df):
    txn_type_spend = df.groupby('TXN_TYPE')['TXN_AMOUNT'].sum().reset_index()
    txn_type_spend.rename(columns={'TXN_AMOUNT': 'Total_Spend'}, inplace=True)
    return txn_type_spend

# 5. Top Merchants by Volume and Value (Per User)
def top_merchants(df, top_n=10):
    top_merchant_volume = (
        df.groupby(['UserID', 'MERC_TXN_ID'])
        .size()
        .reset_index(name='Transaction_Count')
        .sort_values(by='Transaction_Count', ascending=False)
        .groupby('UserID')
        .head(top_n)
        .reset_index(drop=True)
    )

    top_merchant_value = (
        df.groupby(['UserID', 'MERC_TXN_ID'])['TXN_AMOUNT']
        .sum()
        .reset_index()
        .sort_values(by='TXN_AMOUNT', ascending=False)
        .rename(columns={'TXN_AMOUNT': 'Total_Spend'})
        .groupby('UserID')
        .head(top_n)
        .reset_index(drop=True)
    )

    return top_merchant_volume, top_merchant_value

def get_top_merchants_for_user(df, user_id, top_n=10):
    user_df = df[df['UserID'] == user_id]
    top_volume, top_value = top_merchants(user_df, top_n=top_n)
    return top_volume, top_value

# 6. Transaction Frequency per User
def transaction_frequency(df):
    txn_count = df.groupby('UserID').size().reset_index(name='Transaction_Count')
    avg_txn_value = df.groupby('UserID')['TXN_AMOUNT'].mean().reset_index(name='Average_Transaction_Value')
    frequency_df = pd.merge(txn_count, avg_txn_value, on='UserID')
    return frequency_df

# 7. Daily, Weekly, Monthly Spend Trends
def temporal_spend_trends(df):
    daily_spend = df.groupby(df['TXN_DATE'].dt.date)['TXN_AMOUNT'].sum().reset_index(name='Daily_Spend')
    weekly_spend = df.groupby(df['TXN_DATE'].dt.isocalendar().week)['TXN_AMOUNT'].sum().reset_index(name='Weekly_Spend')
    monthly_spend = df.groupby(df['TXN_DATE'].dt.to_period('M'))['TXN_AMOUNT'].sum().reset_index(name='Monthly_Spend')
    return daily_spend, weekly_spend, monthly_spend

# 8. Weekday vs Weekend Spend
def weekday_vs_weekend_spend(df):
    weekday_spend = df.groupby('Weekend')['TXN_AMOUNT'].sum().reset_index()
    weekday_spend['Day_Type'] = weekday_spend['Weekend'].map({0: 'Weekday', 1: 'Weekend'})
    return weekday_spend[['Day_Type', 'TXN_AMOUNT']]

# 9. Peak Spending Hours
def peak_spending_hours(df):
    hourly_spend = df.groupby('Hour')['TXN_AMOUNT'].sum().reset_index()
    hourly_spend.rename(columns={'TXN_AMOUNT': 'Total_Spend'}, inplace=True)
    return hourly_spend

# 10. Currency Breakdown
def currency_spend_breakdown(df):
    if 'CURRENCY' in df.columns:
        currency_spend = df.groupby('CURRENCY')['TXN_AMOUNT'].sum().reset_index()
        currency_spend.rename(columns={'TXN_AMOUNT': 'Total_Spend'}, inplace=True)
        return currency_spend
    else:
        return pd.DataFrame()

# 11. Fee Analysis
def fee_analysis(df):
    total_fees = df['FEE_AMOUNT'].sum()
    avg_fee_ratio = df['Fee_to_Txn_Ratio'].mean()
    return total_fees, avg_fee_ratio

# 12. Rolling Spend Analysis (7-day Moving Average)
def calculate_rolling_spend(df, window=7):
    df_sorted = df.sort_values(['UserID', 'TXN_DATE'])
    rolling_spend = (
        df_sorted.groupby('UserID')
        .apply(lambda group: group.set_index('TXN_DATE')['TXN_AMOUNT'].rolling(window=f'{window}D').mean())
        .reset_index()
        .rename(columns={'TXN_AMOUNT': f'Rolling_{window}D_Avg_Spend'})
    )
    return rolling_spend

# 13. Recurring Payment Detection (Every ~30 Days)
def detect_recurring_payments(df, interval_days=30):
    df_sorted = df.sort_values(['UserID', 'MERC_TXN_ID', 'TXN_DATE'])
    recurring_flags = []

    for (user, merchant), group in df_sorted.groupby(['UserID', 'MERC_TXN_ID']):
        group = group.sort_values('TXN_DATE')
        if len(group) < 3:
            continue  # Need at least 3 transactions to detect pattern
        gaps = group['TXN_DATE'].diff().dt.days.dropna()
        avg_gap = gaps.mean()
        if abs(avg_gap - interval_days) <= 5:  # Allow 5-day margin
            recurring_flags.append({'UserID': user, 'MERC_TXN_ID': merchant, 'Avg_Days_Between_Txns': avg_gap})

    recurring_df = pd.DataFrame(recurring_flags)
    return recurring_df

# 14. User Segmentation (Gold/Silver/Bronze)
def segment_users(total_spend_df):
    spend_quantiles = total_spend_df['Total_Spend'].quantile([0.2, 0.7]).values

    def assign_tier(spend):
        if spend >= spend_quantiles[1]:
            return 'Gold'
        elif spend >= spend_quantiles[0]:
            return 'Silver'
        else:
            return 'Bronze'

    total_spend_df['User_Tier'] = total_spend_df['Total_Spend'].apply(assign_tier)
    return total_spend_df
