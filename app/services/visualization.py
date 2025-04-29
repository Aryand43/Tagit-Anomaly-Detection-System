import matplotlib.pyplot as plt
import seaborn as sns

sns.set(style="whitegrid")  # Apply a clean, professional theme to all plots

# 1. Plot Monthly Spend Trend (Per User)
def plot_monthly_spend(monthly_spend, user_id):
    data = monthly_spend[monthly_spend['UserID'] == user_id]

    plt.figure(figsize=(10, 6))
    sns.lineplot(x='YearMonth', y='Monthly_Spend', data=data, marker='o')
    plt.title(f'Monthly Spending Trend for {user_id}')
    plt.xlabel('Month')
    plt.ylabel('Total Spend')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# 2. Plot Top Merchants (Per User)
def plot_top_merchants(top_merchants, user_id):
    data = top_merchants[top_merchants['UserID'] == user_id]

    plt.figure(figsize=(10, 6))
    sns.barplot(x='Total_Spend', y='MERC_TXN_ID', data=data, palette='viridis')
    plt.title(f'Top Merchants for {user_id}')
    plt.xlabel('Total Spend')
    plt.ylabel('Merchant ID')
    plt.tight_layout()
    plt.show()

# 3. Plot Transaction Amount Distribution (Per User)
def plot_transaction_distribution(df, user_id):
    data = df[df['UserID'] == user_id]['TXN_AMOUNT']

    plt.figure(figsize=(10, 6))
    sns.histplot(data, bins=50, kde=True)
    plt.title(f'Transaction Amount Distribution for {user_id}')
    plt.xlabel('Transaction Amount')
    plt.ylabel('Frequency')
    plt.tight_layout()
    plt.show()

# 4. Plot Peak Spending Hours (Per User)
def plot_peak_hours(df, user_id):
    data = df[df['UserID'] == user_id]
    hourly_spend = data.groupby('Hour')['TXN_AMOUNT'].sum().reset_index()

    plt.figure(figsize=(10, 6))
    sns.barplot(x='Hour', y='TXN_AMOUNT', data=hourly_spend, palette='coolwarm')
    plt.title(f'Peak Spending Hours for {user_id}')
    plt.xlabel('Hour of Day')
    plt.ylabel('Total Spend')
    plt.tight_layout()
    plt.show()
