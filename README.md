# 📊 SaaS Business Performance Dashboard

A business intelligence dashboard built with **Python**, **Pandas**, **Streamlit**, and **Plotly** that tracks core SaaS subscription metrics, visualises revenue trends, and surfaces data quality issues automatically.

> Built as a portfolio project for a Business Intelligence Trainee application.

---

## ✨ Features

- **KPI Cards** — Live calculations of MRR, Churn Rate, ARPU, and Active Subscriber count
- **Revenue Trend** — Monthly MRR line chart with area fill across the full subscription period
- **World Map** — Choropleth map showing subscriber distribution by country
- **Tier Bar Chart** — Horizontal bar chart comparing revenue contribution per subscription tier
- **Data Health Check** — Automated null detection, duplicate row flagging, and completeness scoring
- **Sidebar Filters** — Filter all views by Subscription Tier and Country in real time

---

## 🗂️ Project Structure

```
saas-dashboard/
├── app.py            # Streamlit UI layer (presentation only)
├── data.py           # Data layer: generation, KPIs, health checks
├── requirements.txt  # Pinned Python dependencies
├── .gitignore
└── README.md
```

`app.py` and `data.py` are deliberately separated — the data layer is fully independent of Streamlit and can be imported, tested, or replaced without touching the UI.

---

## 📐 KPI Definitions

| KPI | Formula | Business Meaning |
|---|---|---|
| **MRR** | `sum(Monthly Revenue)` of active users | Total predictable monthly income |
| **Churn Rate** | `churned / total × 100` | % of subscribers who have cancelled |
| **ARPU** | `MRR / active subscribers` | Average value of each paying customer |

---

## 🧱 Tech Stack

| Tool | Purpose |
|---|---|
| `Python 3.10+` | Core language |
| `Pandas` | Data manipulation and aggregation |
| `NumPy` | Random data generation with seeding |
| `Streamlit` | Web UI and interactive filters |
| `Plotly` | Line chart, choropleth map, bar chart |

---

## 🚀 Getting Started

**1. Clone the repository**
```bash
git clone https://github.com/your-username/saas-dashboard.git
cd saas-dashboard
```

**2. Create and activate a virtual environment**
```bash
python -m venv venv

# Mac / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Run the app**
```bash
streamlit run app.py
```

The dashboard opens automatically at `http://localhost:8501`.

---

## 🩺 Data Health Section

The dashboard runs three automated checks on every load:

| Check | What it catches |
|---|---|
| **Null Values** | Missing fields per column that could skew KPIs |
| **Duplicate Rows** | Repeated records that inflate subscriber counts |
| **Completeness %** | Overall fill rate across all columns and rows |

Badges are colour-coded: 🟢 clean, 🟡 warning, 🔴 action required.

> **Note on `Churn Date` nulls:** A null here means the subscriber is still active — this is intentional domain behaviour, not missing data. A production pipeline would document this as a sentinel value and exclude it from null counts.

---

## 📦 Dataset

The mock dataset is generated programmatically in `data.py` using a fixed random seed (`seed=42`) for full reproducibility. It simulates **1,200 SaaS subscribers** across:

- **15 countries** with realistic geographic weighting
- **3 subscription tiers** — Starter ($29), Professional ($79), Enterprise ($299)
- **18% churn probability** per subscriber
- **Date range** — January 2023 to January 2024

Five duplicate rows and eight null Country values are injected deliberately to give the Data Health section real issues to surface.

---

## 🔧 Configuration

To change dataset size or random seed, edit the constants at the top of `data.py`:

```python
# data.py
CHURN_PROBABILITY = 0.18   # % of users who churn
DATASET_START     = datetime(2023, 1, 1)
DATASET_END       = datetime(2024, 1, 1)
```

Call `generate_dataset(n=2000, seed=99)` in `app.py` to generate a larger or different dataset.

---

## 📝 Git History

```
chore: add .gitignore for Python and Streamlit project
chore: add requirements.txt with pinned dependencies
feat: add data layer with dataset generation, KPI calculations, and health checks
feat: add Streamlit UI layer, imports all logic from data.py
docs: add README
```

---

## 👤 Author

**TUON Phannarong**
CS Student
[github.com/Chiyuka](https://github.com/Chiyuka) · [www.linkedin.com/in/phannarong-tuon-734267296](https://www.linkedin.com/in/phannarong-tuon-734267296)
