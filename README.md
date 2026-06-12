# 📊 COVID-19 ANALYSIS Dashboard

An interactive analytics dashboard for visualizing COVID-19 trends across India using Dash, Plotly, and Pandas.

---

## 📌 Overview

This project provides real-time insights into India's COVID-19 pandemic progression through an interactive web dashboard. Users can explore state-wise data, analyze daily trends, and visualize case distributions using dynamic charts and KPIs.

---

## ✨ Features

- **Interactive State Filtering** — Select individual states or view all-India data
- **Date Range Selection** — Analyze specific time periods dynamically
- **Live KPI Cards** — Real-time total cases, active cases, recoveries & deaths
- **Daily Trend Analysis** — Line chart showing daily new cases with area fill
- **State-wise Comparison** — Bar chart ranking top 10 affected states
- **Case Distribution** — Pie chart visualizing active vs recovered vs deceased
- **Responsive Design** — Mobile-friendly layout with custom CSS
- **Cumulative Data Handling** — Accurate processing of time-series cumulative data

---

## 🛠️ Technologies Used

| Category | Technology |
|----------|------------|
| Language | Python 3.8+ |
| Framework | Dash |
| Visualization | Plotly |
| Data Processing | Pandas |
| Web Server | Gunicorn |
| Styling | CSS3 |
| Deployment | Railway / Render / Heroku |

---

## ⚙️ Workflow

1. User selects state and date range via filters
2. Dash callbacks process filtered data
3. Pandas aggregates cumulative statistics
4. Plotly generates interactive visualizations
5. Dashboard updates dynamically without page refresh
6. Real-time KPIs reflect current selections

---

## 🚀 Installation

bash
# Clone the repository
git clone https://github.com/HUMAID26/covid19-india-dashboard.git

# Navigate to project directory
cd covid19-india-dashboard

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py

# Open in browser
http://127.0.0.1:8050
⚠️ Note

This project is intended for educational and learning purposes related to Python web scraping and Flask integration.

👨‍💻 Author

Humaid Khatib
