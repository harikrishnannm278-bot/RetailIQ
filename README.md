# RetailIQ — E-Commerce Data Analytics Project

## Overview

End-to-end data analytics project analysing 100,000+ real orders
from Olist, a Brazilian e-commerce marketplace (2016–2018).

## Business Questions Answered

- Which products and categories drive the most revenue?
- Who are our most valuable customers — and are we losing any?
- Which regions in Brazil have the highest and lowest sales?
- What affects customer review scores?
- How healthy are our delivery operations?

## Key Findings

- **R$20.4M** total revenue across 99,441 orders
- **Bed & Bath** is #1 category at R$1.7M revenue
- **São Paulo** generates R$7.6M — 37% of all revenue
- **94.6%** of customers never return after first purchase
- **22,230 At Risk** customers = R$4.7M revenue at risk
- **91.9%** on-time delivery rate
- **4.02/5** average customer review score

## Tools Used

| Tool       | Purpose                          |
| ---------- | -------------------------------- |
| Python     | Data loading, cleaning, analysis |
| pandas     | Data manipulation                |
| matplotlib | Charts and visualizations        |
| SQL/SQLite | Database queries                 |
| DBeaver    | Professional SQL client          |
| Power BI   | Interactive dashboard            |
| GitHub     | Version control                  |

## Project Structure

```
RetailIQ/
├── data/
│   ├── raw/             ← Original Olist CSVs (9 files)
│   └── processed/       ← Cleaned data outputs
├── src/                 ← Python scripts
│   ├── load_01.py       ← Load all 9 datasets
│   ├── 02_clean.py      ← Clean + build master table
│   ├── 03_eda.py        ← EDA + 4 charts
│   ├── 04_rfm.py        ← RFM customer segmentation
│   ├── 05_kpis.py       ← 14 business KPIs
│   ├── 06_cohort.py     ← Cohort retention analysis
│   ├── 07_export.py     ← Export for Power BI
│   └── create_db.py     ← Create SQLite database
├── sql/
│   └── queries.sql      ← 6 business SQL queries
├── outputs/             ← Generated charts
└── README.md
```

## Scripts

| Script       | What It Does                                               |
| ------------ | ---------------------------------------------------------- |
| load_01.py   | Loads all 9 Olist datasets — 1.5M rows total               |
| 02_clean.py  | Cleans dates, fills nulls, builds 113K row master table    |
| 03_eda.py    | EDA — top categories, monthly trend, reviews, day analysis |
| 04_rfm.py    | RFM model — segments 93,358 customers into 6 groups        |
| 05_kpis.py   | Calculates 14 KPIs — revenue, operations, satisfaction     |
| 06_cohort.py | Cohort analysis — found 94.6% churn rate                   |
| 07_export.py | Exports 6 clean CSVs for Power BI dashboard                |

## SQL Queries (DBeaver)

| Query                    | Business Question                 |
| ------------------------ | --------------------------------- |
| Revenue by Category      | Which categories make most money? |
| Monthly Revenue Trend    | Is the business growing?          |
| Revenue by State         | Which regions dominate?           |
| Order Status Breakdown   | How many orders cancel or fail?   |
| Top 10 Sellers           | Who are the best performers?      |
| Late Deliveries by State | Where are logistics failing?      |

## Power BI Dashboard — 5 Pages

| Page                  | Content                            |
| --------------------- | ---------------------------------- |
| Executive Overview    | Revenue, Orders, Growth trend      |
| Customer Intelligence | RFM segments, Champion vs At Risk  |
| Regional Analysis     | State map, revenue by region       |
| Delivery Performance  | On-time rate, delivery days trend  |
| Operations & Reviews  | Category ratings, scatter analysis |

## Dataset

[Olist Brazilian E-Commerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)

- 100,000+ real orders from 2016–2018
- 9 relational tables
- 1.5 million total rows across all tables

## How to Run

```bash
# Install dependencies
pip install -r requirements.txt

# Run pipeline in order
python src/load_01.py
python src/02_clean.py
python src/03_eda.py
python src/04_rfm.py
python src/05_kpis.py
python src/06_cohort.py
python src/07_export.py

# Create SQL database
python src/create_db.py

```
