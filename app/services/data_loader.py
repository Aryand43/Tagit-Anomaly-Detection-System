import pandas as pd
import os
import json

def load_and_clean_data(file_path):
    dtype = {
        'UserID': str,
        'TXN_ID': str,
        'MERC_TXN_ID': str,
        'TXN_TYPE': str,
        'CURRENCY': str
    }

    parse_dates = ['TXN_DATE']

    df = pd.read_csv(file_path, dtype=dtype, parse_dates=parse_dates)

    # Basic cleaning
    df['TXN_AMOUNT'] = pd.to_numeric(df['TXN_AMOUNT'], errors='coerce')
    df['FEE_AMOUNT'] = pd.to_numeric(df['FEE_AMOUNT'], errors='coerce')

    df['FEE_AMOUNT'].fillna(0, inplace=True)

    # Ensure datetime parsing
    df['TXN_DATE'] = pd.to_datetime(df['TXN_DATE'], errors='coerce')

    # Drop any rows with null critical values
    df.dropna(subset=['UserID', 'TXN_DATE', 'TXN_AMOUNT'], inplace=True)

    # Add extra engineered features
    df['YearMonth'] = df['TXN_DATE'].dt.to_period('M')
    df['Weekday'] = df['TXN_DATE'].dt.weekday
    df['Weekend'] = df['Weekday'].apply(lambda x: 1 if x >= 5 else 0)
    df['Hour'] = df['TXN_DATE'].dt.hour

    # Transaction Amount Binning
    bins = [-float('inf'), 10, 100, 500, float('inf')]
    labels = ['<10', '10-100', '100-500', '500+']
    df['TXN_Amount_Bin'] = pd.cut(df['TXN_AMOUNT'], bins=bins, labels=labels)

    # Days Since Last Transaction per User
    df = df.sort_values(['UserID', 'TXN_DATE'])
    df['Days_Since_Last_TXN'] = df.groupby('UserID')['TXN_DATE'].diff().dt.days

    # Aggregate multiple transactions on same day
    daily_spend_df = df.groupby(['UserID', 'TXN_DATE'])['TXN_AMOUNT'].sum().reset_index()

    # Calculate rolling 7D spend
    rolling_7d = (
        daily_spend_df.sort_values(['UserID', 'TXN_DATE'])
        .groupby('UserID')
        .apply(lambda group: group.set_index('TXN_DATE')['TXN_AMOUNT'].rolling('7D').sum())
        .reset_index()
        .rename(columns={'TXN_AMOUNT': 'Rolling_7D_Spend'})
    )

    # Calculate rolling 30D spend
    rolling_30d = (
        daily_spend_df.sort_values(['UserID', 'TXN_DATE'])
        .groupby('UserID')
        .apply(lambda group: group.set_index('TXN_DATE')['TXN_AMOUNT'].rolling('30D').sum())
        .reset_index()
        .rename(columns={'TXN_AMOUNT': 'Rolling_30D_Spend'})
    )

    # Merge rolling spends back into main df
    df = pd.merge(df, rolling_7d, on=['UserID', 'TXN_DATE'], how='left')
    df = pd.merge(df, rolling_30d, on=['UserID', 'TXN_DATE'], how='left')

    # Merchant Spend Ratio
    total_user_spend = df.groupby('UserID')['TXN_AMOUNT'].transform('sum')
    df['Merchant_Spend_Ratio'] = df['TXN_AMOUNT'] / total_user_spend

    # Fee to Transaction Ratio
    df['Fee_to_Txn_Ratio'] = df['FEE_AMOUNT'] / df['TXN_AMOUNT']

    # Validation Assertions
    assert df['TXN_AMOUNT'].isnull().sum() == 0, "Transaction Amount cannot have NULLs!"
    assert pd.api.types.is_numeric_dtype(df['TXN_AMOUNT']), "Transaction Amount must be numeric!"
    assert df['TXN_DATE'].isnull().sum() == 0, "Transaction Date cannot have NULLs!"
    assert df['UserID'].isnull().sum() == 0, "UserID must not have NULLs!"

    # Warning for duplicates
    duplicate_count = df.duplicated(subset=['UserID', 'TXN_DATE', 'TXN_AMOUNT']).sum()
    if duplicate_count > 0:
        print(f"Warning: {duplicate_count} duplicate transactions found based on UserID + TXN_DATE + TXN_AMOUNT!")

    # Create data dictionary JSON
    print("Finished cleaning and attempting to save data dictionary...")
    os.makedirs('../../outputs', exist_ok=True)
    data_dictionary = {
        column: str(dtype) for column, dtype in zip(df.columns, df.dtypes)
    }
    with open('../../outputs/data_dictionary.json', 'w') as f:
        json.dump(data_dictionary, f, indent=4)

    return df
