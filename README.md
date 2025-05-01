# Tagit Smart Transaction Dashboard

A comprehensive transaction monitoring dashboard built using **Streamlit**, designed for financial data exploration, anomaly detection, and user-specific behavioral analysis.

---

## 📌 Project Features

### ✅ Dashboard Overview
- Summary metrics for each user (total transactions, total spend, total anomalies).
- High-value anomaly alerts.

### 💸 Spending Patterns
- **Monthly Spending Trend** with peak/low annotations and rolling averages.
- **Transaction Distribution** histogram with mean, median, and skew indicators.
- **Top Merchants** by spend, with transaction volume and detailed annotations.
- **Peak Spending Hours** with percentage share and hour-wise highlights.

### ⚠️ Anomaly Detection
- **Outliers**: Detected using Isolation Forest per user.
- **Spending Spikes**: Transactions above the 95th percentile.
- **Duplicate Transactions**: Based on identical User ID + Timestamp + Merchant + Amount.
- Summary table for each anomaly type.
- Toggle to mark transactions as reviewed.

### 📥 Ingest a New Transaction (Quick Anomaly Check)
- Allows manual input of a transaction's details (amount, type, date, hour, etc.).
- Instantly flags anomalies by comparing with existing user behavior.

### 📤 Exports
- Download buttons for cleaned data and anomaly datasets.
- Plots saved locally into the `/outputs/plots/` directory for presentations.

---

## 🛠️ Folder Structure
```
.
├── dashboard.py                  # Main Streamlit app
├── data/
│   └── transactions.csv          # Transactional data file
├── app/
│   └── services/
│       ├── data_loader.py       # Cleans & preps data
│       ├── aggregation.py       # Monthly, merchant-level analytics
│       ├── anomaly_detector.py  # Isolation Forest, spike & duplicate checks
│       └── visualization.py     # All annotated charts
└── outputs/
    └── plots/                   # Auto-saved visualizations for export
```

---

## 📦 Requirements
Make sure these are included in your `requirements.txt`:
```
streamlit
pandas
matplotlib
seaborn
scikit-learn
```

---

## 🚀 How to Run the App Locally
1. Clone the repo:
```bash
git clone https://github.com/your-org/tagit-dashboard.git
cd tagit-dashboard
```
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Run the dashboard:
```bash
streamlit run dashboard.py
```

---

## 🧠 Customization Guide

### 💾 Adding New Data
- Replace or add to `data/transactions.csv`
- Ensure columns include:
  - `UserID`
  - `TXN_AMOUNT`
  - `TXN_TYPE`
  - `MERC_TXN_ID`
  - `TXN_DATE`

### ⚙️ Modifying Anomaly Logic
- Edit `anomaly_detector.py`
- Tune Isolation Forest or percentile thresholds

### 🎨 Changing Visuals
- Go to `visualization.py`
- Update colors, annotations, chart types

### 🔐 Deployment Notes
- The dashboard is compatible with **Streamlit Cloud**
- Ensure `outputs/` directory is not hard-written to prevent permission issues
- Remove or modify any `os.makedirs()` that fails on cloud

---

## 🔗 Useful Resources
- [Streamlit Docs](https://docs.streamlit.io/)
- [Seaborn Gallery](https://seaborn.pydata.org/examples/index.html)
- [Scikit-learn Isolation Forest](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html)

---

## 👨‍💻 Maintainers
- Aryan Dutt — [LinkedIn](https://www.linkedin.com/in/aryan-dutt-/)   
- Tagit AI Engineering Team

For any feature requests or issues, please submit via GitHub or contact the maintainer.

---

_This dashboard is built as a real-time transaction monitoring tool to demonstrate scalable financial anomaly detection with human-friendly insights._

