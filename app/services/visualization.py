import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import os
import pandas as pd
from matplotlib.ticker import FuncFormatter
import numpy as np

sns.set(style="whitegrid")

def plot_monthly_spend(monthly_spend, user_id, save_path=None):
    if monthly_spend.empty:
        st.warning("No monthly spend data available.")
        return

    data = monthly_spend[monthly_spend['UserID'] == user_id].copy()
    data['YearMonth'] = pd.to_datetime(data['YearMonth'])
    start = data['YearMonth'].min()
    end = data['YearMonth'].max()
    subtitle = f"({start.strftime('%b %Y')} – {end.strftime('%b %Y')})"

    # Add 3-month rolling average
    data['Rolling_Avg'] = data['Monthly_Spend'].rolling(window=3).mean()

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.lineplot(x='YearMonth', y='Monthly_Spend', data=data, marker='o', ax=ax, label='Monthly Spend')
    sns.lineplot(x='YearMonth', y='Rolling_Avg', data=data, linestyle='--', ax=ax, label='3-Month Avg')
    plt.title(f"Monthly Spending Trend {subtitle}", fontsize=14)
    plt.xlabel("Month")
    plt.ylabel("Spend")
    plt.xticks(rotation=45)

    if len(data) > 1:
        peak = data.loc[data['Monthly_Spend'].idxmax()]
        low = data.loc[data['Monthly_Spend'].idxmin()]
        ax.annotate(f"Peak: ${peak['Monthly_Spend']:,.0f}", xy=(peak['YearMonth'], peak['Monthly_Spend']), xytext=(peak['YearMonth'], peak['Monthly_Spend'] * 1.1),
                    arrowprops=dict(facecolor='green', arrowstyle='->'))
        ax.annotate(f"Low: ${low['Monthly_Spend']:,.0f}", xy=(low['YearMonth'], low['Monthly_Spend']), xytext=(low['YearMonth'], low['Monthly_Spend'] * 1.1),
                    arrowprops=dict(facecolor='red', arrowstyle='->'))

    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"${x:,.0f}"))
    ax.set_ylim(bottom=0)
    ax.legend()
    plt.tight_layout()

    if save_path:
        os.makedirs(save_path, exist_ok=True)
        plt.savefig(os.path.join(save_path, f"{user_id}_monthly_spend.png"))
    st.pyplot(fig)
    plt.clf()

def plot_top_merchants(top_merchants, user_id, save_path=None):
    data = top_merchants[top_merchants['UserID'] == user_id]
    if data.empty:
        st.warning("No merchant data available.")
        return

    fig, ax = plt.subplots(figsize=(10, 6))
    data = data.sort_values('Total_Spend', ascending=True)

    display_labels = [
        f"${spend:,.0f} | {int(cnt)} txns" if 'Transaction_Count' in data else f"${spend:,.0f}"
        for spend, cnt in zip(data['Total_Spend'], data.get('Transaction_Count', [0]*len(data)))
    ]

    sns.barplot(x='Total_Spend', y='MERC_TXN_ID', data=data, palette='viridis', ax=ax)
    plt.title("Top Merchants by Spend")
    plt.xlabel("Total Spend")
    plt.ylabel("Merchant")

    for i, (value, label) in enumerate(zip(data['Total_Spend'], display_labels)):
        ax.text(value, i, label, va='center')

    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"${x:,.0f}"))
    ax.set_xlim(left=0)

    plt.tight_layout()
    if save_path:
        os.makedirs(save_path, exist_ok=True)
        plt.savefig(os.path.join(save_path, f"{user_id}_top_merchants.png"))
    st.pyplot(fig)
    plt.clf()

def plot_transaction_distribution(user_df, user_id, save_path=None):
    if user_df.empty:
        st.warning("No transaction data to display distribution.")
        return

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.histplot(user_df['TXN_AMOUNT'], bins=30, kde=True, ax=ax)
    plt.title("Transaction Amount Distribution")
    plt.xlabel("Transaction Amount")
    plt.ylabel("Frequency")

    mean = user_df['TXN_AMOUNT'].mean()
    median = user_df['TXN_AMOUNT'].median()
    ax.axvline(mean, color='green', linestyle='--', label=f"Mean: ${mean:,.2f}")
    ax.axvline(median, color='red', linestyle='--', label=f"Median: ${median:,.2f}")
    ax.fill_betweenx([0, ax.get_ylim()[1]], min(mean, median), max(mean, median), color='gray', alpha=0.2)
    ax.legend(title="Distribution Indicators")

    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"${x:,.0f}"))
    ax.set_xlim(left=0)

    plt.tight_layout()
    if save_path:
        os.makedirs(save_path, exist_ok=True)
        plt.savefig(os.path.join(save_path, f"{user_id}_transaction_distribution.png"))
    st.pyplot(fig)
    plt.clf()

def plot_peak_hours(user_df, user_id, save_path=None):
    if 'Hour' not in user_df.columns:
        st.warning("Missing Hour column in data.")
        return

    hourly_spend = user_df.groupby('Hour')['TXN_AMOUNT'].sum().reset_index()
    total = hourly_spend['TXN_AMOUNT'].sum()
    hourly_spend['Pct'] = hourly_spend['TXN_AMOUNT'] / total * 100

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(x='Hour', y='TXN_AMOUNT', data=hourly_spend, palette='coolwarm', ax=ax)
    plt.title("Peak Spending Hours")
    plt.xlabel("Hour of Day")
    plt.ylabel("Spend")

    peak = hourly_spend.loc[hourly_spend['TXN_AMOUNT'].idxmax()]
    low = hourly_spend.loc[hourly_spend['TXN_AMOUNT'].idxmin()]

    ax.annotate(f"Peak: {peak['Pct']:.1f}%", xy=(peak['Hour'], peak['TXN_AMOUNT']),
                xytext=(peak['Hour'], peak['TXN_AMOUNT'] * 1.1),
                arrowprops=dict(facecolor='orange', arrowstyle='->'))
    if low['Pct'] < 2:
        ax.annotate(f"Low: {low['Pct']:.1f}%", xy=(low['Hour'], low['TXN_AMOUNT']),
                    xytext=(low['Hour'], low['TXN_AMOUNT'] * 1.1),
                    arrowprops=dict(facecolor='blue', arrowstyle='->'))

    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"${x:,.0f}"))
    ax.set_ylim(bottom=0)

    plt.tight_layout()
    if save_path:
        os.makedirs(save_path, exist_ok=True)
        plt.savefig(os.path.join(save_path, f"{user_id}_peak_hours.png"))
    st.pyplot(fig)
    plt.clf()
