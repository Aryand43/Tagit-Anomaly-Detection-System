import matplotlib.pyplot as plt
import seaborn as sns
import os
import streamlit as st

sns.set(style="whitegrid")

def plot_monthly_spend(monthly_spend, user_id, save_path=None):
    data = monthly_spend[monthly_spend['UserID'] == user_id]

    plt.figure(figsize=(10, 6))
    ax = sns.lineplot(x='YearMonth', y='Monthly_Spend', data=data, marker='o', color='steelblue')
    plt.title(f'Monthly Spending Trend for {user_id}', fontsize=16)
    plt.xlabel('Month', fontsize=12)
    plt.ylabel('Total Spend', fontsize=12)
    plt.xticks(rotation=45)
    plt.grid(True)

    # Highlight peak month
    if not data.empty:
        peak = data.loc[data['Monthly_Spend'].idxmax()]
        plt.annotate(f'Peak: {peak["Monthly_Spend"]:.2f}',
                     xy=(peak['YearMonth'], peak['Monthly_Spend']),
                     xytext=(peak['YearMonth'], peak['Monthly_Spend'] * 1.1),
                     arrowprops=dict(facecolor='red', arrowstyle="->"))

    plt.tight_layout()

    if save_path:
        os.makedirs(save_path, exist_ok=True)
        plt.savefig(f"{save_path}/monthly_spend_{user_id}.png")
    else:
        st.pyplot(plt.gcf())
        plt.clf()


def plot_top_merchants(top_merchants, user_id, save_path=None):
    data = top_merchants[top_merchants['UserID'] == user_id]

    plt.figure(figsize=(10, 6))
    colors = ['gold' if i < 3 else 'lightblue' for i in range(len(data))]

    ax = sns.barplot(x='Total_Spend', y='MERC_TXN_ID', data=data, palette=colors)
    plt.title(f'Top Merchants for {user_id}', fontsize=16)
    plt.xlabel('Total Spend', fontsize=12)
    plt.ylabel('Merchant ID', fontsize=12)
    plt.grid(True)

    plt.tight_layout()

    if save_path:
        os.makedirs(save_path, exist_ok=True)
        plt.savefig(f"{save_path}/top_merchants_{user_id}.png")
    else:
        st.pyplot(plt.gcf())
        plt.clf()


def plot_transaction_distribution(df, user_id, save_path=None):
    data = df[df['UserID'] == user_id]['TXN_AMOUNT']

    plt.figure(figsize=(10, 6))
    sns.histplot(data, bins=50, kde=True, color='mediumseagreen')

    mean_value = data.mean()
    plt.axvline(mean_value, color='red', linestyle='--', label=f'Mean: {mean_value:.2f}')

    plt.title(f'Transaction Amount Distribution for {user_id}', fontsize=16)
    plt.xlabel('Transaction Amount', fontsize=12)
    plt.ylabel('Frequency', fontsize=12)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    if save_path:
        os.makedirs(save_path, exist_ok=True)
        plt.savefig(f"{save_path}/txn_distribution_{user_id}.png")
    else:
        st.pyplot(plt.gcf())
        plt.clf()


def plot_peak_hours(df, user_id, save_path=None):
    data = df[df['UserID'] == user_id]
    hourly_spend = data.groupby('Hour')['TXN_AMOUNT'].sum().reset_index()

    plt.figure(figsize=(10, 6))
    ax = sns.barplot(x='Hour', y='TXN_AMOUNT', data=hourly_spend, palette='coolwarm')

    plt.title(f'Peak Spending Hours for {user_id}', fontsize=16)
    plt.xlabel('Hour of Day', fontsize=12)
    plt.ylabel('Total Spend', fontsize=12)
    plt.grid(True)

    # Highlight peak hour
    if not hourly_spend.empty:
        peak = hourly_spend.loc[hourly_spend['TXN_AMOUNT'].idxmax()]
        plt.annotate(f'Peak: {peak["Hour"]}h',
                     xy=(peak['Hour'], peak['TXN_AMOUNT']),
                     xytext=(peak['Hour'], peak['TXN_AMOUNT'] * 1.1),
                     arrowprops=dict(facecolor='red', arrowstyle="->"))

    plt.tight_layout()

    if save_path:
        os.makedirs(save_path, exist_ok=True)
        plt.savefig(f"{save_path}/peak_hours_{user_id}.png")
    else:
        st.pyplot(plt.gcf())
        plt.clf()

