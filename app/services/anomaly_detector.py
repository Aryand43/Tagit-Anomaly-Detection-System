import pandas as pd
from sklearn.ensemble import IsolationForest

def detect_outliers(df, contamination=0.01):
    """
    Detect outliers per user using Isolation Forest.
    Adds Anomaly_Type column = 'Outlier'.
    """
    outlier_records = []

    for user_id, user_df in df.groupby('UserID'):
        if len(user_df) < 10:
            continue

        model = IsolationForest(contamination=contamination, random_state=42)
        user_txn_amounts = user_df[['TXN_AMOUNT']]
        model.fit(user_txn_amounts)
        preds = model.predict(user_txn_amounts)

        user_df = user_df.copy()
        user_df['Anomaly_Type'] = None
        user_df.loc[preds == -1, 'Anomaly_Type'] = 'Outlier'

        outlier_txns = user_df[user_df['Anomaly_Type'].notnull()]
        outlier_records.append(outlier_txns)

    return pd.concat(outlier_records) if outlier_records else pd.DataFrame()

def detect_spending_spikes(df, percentile_threshold=95):
    """
    Detect spending spikes above user's 95th percentile.
    Adds Anomaly_Type column = 'Spending Spike'.
    """
    spike_records = []

    for user_id, user_df in df.groupby('UserID'):
        threshold = user_df['TXN_AMOUNT'].quantile(percentile_threshold / 100)
        spike_txns = user_df[user_df['TXN_AMOUNT'] >= threshold].copy()
        spike_txns['Anomaly_Type'] = 'Spending Spike'
        spike_records.append(spike_txns)

    return pd.concat(spike_records) if spike_records else pd.DataFrame()

def detect_duplicates(df, round_to=None):
    """
    Detect duplicate transactions based on UserID + TXN_DATE + MERC_TXN_ID + TXN_AMOUNT.
    Adds Anomaly_Type = 'Duplicate Transaction'.
    
    Optional: round TXN_DATE to 'hour' or 'minute' to catch near-duplicates.
    """
    df_copy = df.copy()

    if round_to == 'hour':
        df_copy['TXN_DATE'] = pd.to_datetime(df_copy['TXN_DATE']).dt.round('H')
    elif round_to == 'minute':
        df_copy['TXN_DATE'] = pd.to_datetime(df_copy['TXN_DATE']).dt.round('min')

    duplicate_mask = df_copy.duplicated(subset=['UserID', 'TXN_DATE', 'MERC_TXN_ID', 'TXN_AMOUNT'], keep=False)
    dupes = df_copy[duplicate_mask].copy()
    dupes['Anomaly_Type'] = 'Duplicate Transaction'

    return dupes

def merge_anomalies(outliers, spikes, duplicates):
    all_anomalies = pd.concat([outliers, spikes, duplicates], ignore_index=True)
    all_anomalies = all_anomalies[all_anomalies['Anomaly_Type'].notnull()]
    required_cols = ['UserID', 'TXN_DATE', 'TXN_AMOUNT', 'MERC_TXN_ID', 'Anomaly_Type']
    for col in required_cols:
        if col not in all_anomalies.columns:
            all_anomalies[col] = None
    group_keys = ['UserID', 'TXN_DATE', 'TXN_AMOUNT', 'MERC_TXN_ID']
    merged = all_anomalies.groupby(group_keys, dropna=False).agg({
        'Anomaly_Type': lambda x: '; '.join(sorted(set(i for i in x if pd.notnull(i)))),
        'UserID': 'first',
        'TXN_AMOUNT': 'first',
        'MERC_TXN_ID': 'first',
        'TXN_DATE': 'first'
    }).reset_index(drop=True)

    return merged

def summarize_anomalies(merged_anomalies):
    """
    Returns count of anomaly types per user in clean summary form.
    
    Output: DataFrame with columns: UserID | Anomaly_Type | Count
    """
    exploded = merged_anomalies.copy()

    # Handle stacked anomaly types by splitting them
    exploded['Anomaly_Type'] = exploded['Anomaly_Type'].str.split('; ')
    exploded = exploded.explode('Anomaly_Type')

    summary = (
        exploded.groupby(['UserID', 'Anomaly_Type'])
        .size()
        .reset_index(name='Anomaly_Count')
    )

    return summary