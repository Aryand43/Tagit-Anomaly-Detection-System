from data_loader import load_and_clean_data
from aggregation import (
    calculate_total_spend,
    analyze_monthly_spend,
    transaction_amount_distribution,
    spend_by_transaction_type,
    top_merchants,
    transaction_frequency,
    temporal_spend_trends,
    weekday_vs_weekend_spend,
    peak_spending_hours,
    currency_spend_breakdown,
    fee_analysis
)
from visualization import (
    plot_monthly_spend,
    plot_top_merchants,
    plot_transaction_distribution,
    plot_peak_hours
)

if __name__ == "__main__":
    # Load data
    df = load_and_clean_data('../../data/transactions.csv')
    # Aggregations
    total_spend = calculate_total_spend(df)
    monthly_spend = analyze_monthly_spend(df)
    txn_type_spend = spend_by_transaction_type(df)
    top_volume, top_value = top_merchants(df)
    frequency = transaction_frequency(df)
    daily_spend, weekly_spend, monthly_spend_trends = temporal_spend_trends(df)
    weekend_spend = weekday_vs_weekend_spend(df)
    peak_hours = peak_spending_hours(df)
    currency_breakdown = currency_spend_breakdown(df)
    total_fees, avg_fee_ratio = fee_analysis(df)

    # Choose a User ID to plot (change as needed)
    user_id = 'System'  # Example UserID from your dataset

    # Visualizations (All forced per user)
    plot_monthly_spend(monthly_spend, user_id)
    plot_top_merchants(top_value, user_id)
    plot_transaction_distribution(df, user_id)
    plot_peak_hours(df, user_id)

