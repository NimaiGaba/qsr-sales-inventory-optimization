# QSR Sales & Inventory Optimization

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![SQL](https://img.shields.io/badge/SQL-SQLite%20%7C%20ANSI%20SQL-orange.svg)](https://www.sqlite.org/)
[![Power BI](https://img.shields.io/badge/Power%20BI-Star%20Schema%20%26%20DAX-yellow.svg)](https://powerbi.microsoft.com/)
[![Tests](https://img.shields.io/badge/Tests-Pytest%2017%2F17%20Passing-brightgreen.svg)](https://pytest.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An enterprise-grade, end-to-end **Data Analytics and Business Intelligence project** analyzing sales performance, day-part dining dynamics, food cost profitability, and rule-based inventory optimization for **Artisan Crust Co.**, a high-volume Quick Service Restaurant (QSR) chain operating across 4 metropolitan locations.

> **Scope Note:** This is a pure **Data Analytics and Business Intelligence** project. It contains **no machine learning models, predictive black boxes, or forecasting algorithms**. All insights and optimizations are derived from rigorous SQL relational querying, Pandas data engineering, dynamic reorder-point inventory modeling, and Power BI DAX architecture.

---

## 📌 Executive Summary & Key Measured Results

All metrics are calculated directly from 33,051 verified orders and 65,851 menu line items over the complete 2024 operating year:

| Executive Metric | Measured Value | Operational Benchmark & Context |
|:---|:---:|:---|
| **Gross Sales (GMV)** | **$1,085,821.50** | Total pre-discount transactional revenue |
| **Promotional Discounts Awarded** | **$18,533.48** | 1.71% effective promo rate (well-controlled discount leakage) |
| **Net Operating Revenue** | **$1,067,288.02** | Realized net sales settled at point-of-sale |
| **Cost of Goods Sold (COGS)** | **$318,309.00** | **29.82% food cost** (healthy industry standard: 28–32%) |
| **Gross Profit** | **$748,979.02** | **70.18% gross margin** across the menu |
| **Total Orders Fulfilled** | **33,051** | Averaging 90.3 orders/day chain-wide |
| **Average Order Value (AOV)** | **$32.29** | Spikes to **$34.50+ on weekends** due to combo bundling |
| **Total Inventory Stock Valuation** | **$21,791.50** | Working capital tied up across 24 core ingredients & packaging |
| **Annual Inventory Turnover Ratio** | **14.61x** | Healthy stock turns every ~25.0 days |
| **Annual Kitchen Wastage Loss** | **$25,202.93** | 2.36% of net sales (Primary culprit: expired produce shelf-life) |

---

## 🎯 Business Problem & Core Objectives

High-volume Quick Service Restaurants face a dual operational challenge:
1. **Kitchen Throughput Bottlenecks:** Concentrated lunch and dinner peak hours create prep delays and customer friction if ingredient mise-en-place is not calibrated in advance.
2. **Perishable Shrinkage vs. Stockout Risk:** Carrying excess perishable inventory leads to food spoilage, while carrying too little causes devastating stockouts of core signature revenue drivers.

This project delivers actionable data solutions to resolve these challenges:
- **Sales Performance Tracking:** Evaluate revenue, AOV, and category volume across 4 operating locations.
- **Pareto Menu Optimization:** Identify the core SKUs driving 80% of revenue versus low-velocity long-tail items.
- **Day-Part Labor Scheduling:** Map hourly transaction volume to optimize kitchen prep and staff allocation.
- **Rule-Based Inventory Optimization:** Implement dynamic **Reorder Points (ROP)** and **Safety Stock** formulas to eliminate stockouts while curtailing food waste.
- **Executive BI Reporting:** Provide a 4-page interactive Power BI star schema dashboard and an executive findings report.

---

## 🛠️ Technology Stack & Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                    QSR Data Analytics Architecture                           │
├───────────────────┬───────────────────┬───────────────────┬──────────────────┤
│  Data Layer       │ Analytics Layer   │ SQL / Database    │ BI & Reporting   │
├───────────────────┼───────────────────┼───────────────────┼──────────────────┤
│ • 7 Relational    │ • Pandas 2.2      │ • SQLite DB       │ • Power BI Model │
│   QSR Tables      │ • NumPy 1.26      │ • 6 SQL Modules   │ • 20+ DAX Meas.  │
│ • Data Hygiene &  │ • Matplotlib 3.9  │ • 28 Queries      │ • 14 Publication │
│   Type Validation │ • Seaborn 0.13    │ • CTEs, Window    │   EDA Charts     │
│ • Feature Eng.    │ • Pytest (17/17)  │   Functions, ROPs │ • Exec Insights  │
│   (DayParts, ROP) │ • Python Logging  │ • Relational Views│   Markdown Doc   │
└───────────────────┴───────────────────┴───────────────────┴──────────────────┘
```

- **Python & Data Engineering:** Robust data loading, deduplication, datetime parsing, revenue verification, and feature engineering (`src/data_cleaning.py`).
- **SQL Analytics Engine:** 6 SQL scripts executing 28 queries covering sales performance, product Pareto ranking, time dynamics, inventory health, and margin optimization.
- **Python Exploratory Suite:** 14 high-resolution statistical charts saved to `dashboard/charts/`.
- **Power BI Data Model:** Star schema connecting fact tables (`FactOrders`, `FactOrderItems`, `FactWaste`) with dimension tables (`DimProducts`, `DimLocations`, `DimInventory`, `DimCalendar`).
- **Automated Test Suite:** 17 unit tests using `pytest` verifying 100% computational correctness.

---

## 📊 Core Business Insights & Analytical Findings

### 1. Pepperoni Feast & Signature Pizzas Dominate Revenue
- **Pepperoni Feast** is the single highest-performing menu item, generating **$197,134.07** (18.47% of total chain revenue) and **$138,704.37** in gross profit (70.36% margin).
- The top 3 pizzas (*Pepperoni Feast*, *BBQ Chicken Supreme*, and *Margherita Classic*) drive **$418,305.35** (39.19% of chain revenue).
- **Pareto Principle Validated:** Just **9 out of 32 menu items** account for over **80% of total revenue**.

### 2. Extreme Lunch and Dinner Demand Peaks
- **Lunch Rush (12:00 PM – 2:00 PM):** 9,932 orders (30.05% of daily volume). Peak hour is **12:00 PM** (5,300 orders).
- **Dinner Rush (6:00 PM – 8:00 PM):** 8,240 orders (24.93% of daily volume). Peak hour is **6:00 PM** (4,982 orders).
- **Afternoon Lull (2:00 PM – 4:00 PM):** Order volume drops below 1,900 orders/hr.
- *Operational Impact:* 55% of all daily orders occur within just 4 operating hours.

### 3. Significant Weekend Demand Premium
- **Sunday ($201,000.75)**, **Saturday ($199,691.52)**, and **Friday ($193,597.33)** generate **55.68% of total annual sales**.
- Weekend days average **~$66,000/day** combined across the chain compared to **~$29,000/day** on Monday–Thursday.
- Weekend AOV ($34.50+) is ~12% higher due to increased family combo orders.

### 4. Perishable Inventory Vulnerabilities & Kitchen Wastage
- Annual kitchen wastage totaled **$25,202.93** across 1,094 incidents.
- **Expired Shelf-Life** is the #1 driver of food waste, accounting for **$11,861.39 (47.06%)**, followed by **Preparation Trim / Spillage ($6,321.50, 25.08%)**.
- Three produce items require immediate reorder replenishment:
  1. *Fresh Genovese Basil (`INV-017`):* Stock = 8 kg vs Reorder Level = 12 kg (Critical).
  2. *Fresh Romaine Hearts (`INV-016`):* Stock = 20 cases vs Reorder Level = 25 cases (Low).
  3. *Fresh White Button Mushrooms (`INV-013`):* Stock = 32 kg vs Reorder Level = 40 kg (Low).
- Non-perishable items (*Kraft Carryout Bags* at 92% capacity and *Pizza Flour* at 94% capacity) are overstocked, tying up excess working capital.

---

## 💡 Strategic Business Recommendations & ROI

| Strategic Action | Target Area | Implementation Plan | Projected EBITDA Impact |
|:---|:---|:---|:---:|
| **1. 2x/Week Fresh Produce Delivery** | Perishable Waste Reduction | Shift produce supplier `SUP-04` from 1x weekly bulk drops to 2x weekly scheduled deliveries. Enforce strict First-In, First-Out (FIFO) kitchen staging. | **+$12,600 / year** (50% reduction in expired spoilage) |
| **2. Midweek Lunch Combo Promotion** | Mon–Thu Revenue Expansion | Launch a targeted $12.99 "Lunch Express Slice & Soda" combo between 11:30 AM and 1:30 PM Mon–Thu to boost office worker traffic. | **+$42,000 / year** (5% lift in Mon–Thu lunch revenue) |
| **3. POS Beverage & Dessert Add-ons** | Attach Rate Optimization | Program touch-screen ordering kiosks and staff POS to prompt for high-margin ($2.75 fountain soda, 87% margin) add-ons on single pizza orders. | **+$24,500 / year** (+4% lift in drink attach rates) |
| **4. Peak Rush Kitchen Mise-en-Place** | Operational Efficiency | Complete 100% of dough portioning, cheese shredding, and topping prep by 11:30 AM and 5:00 PM to eliminate rush bottlenecks. | **Protects ~$35,000** in peak-hour throughput |
| **Total Annualized Projected Value** | — | — | **+$79,100 / year** |

---

## 📁 Repository Directory Structure

```
qsr-sales-inventory-optimization/
├── dashboard/                      # Power BI Assets & Data Model Documentation
│   ├── charts/                     # 14 Publication-Grade Visualizations
│   │   ├── 01_monthly_revenue_trend.png
│   │   ├── 02_daily_revenue_trend.png
│   │   ├── 03_hourly_sales_distribution.png
│   │   ├── 04_weekday_vs_weekend_sales.png
│   │   ├── 05_revenue_by_product_category.png
│   │   ├── 06_top_10_products_by_revenue.png
│   │   ├── 07_top_10_products_by_quantity.png
│   │   ├── 08_aov_trends.png
│   │   ├── 09_payment_method_distribution.png
│   │   ├── 10_product_performance_comparison.png
│   │   ├── 11_inventory_stock_distribution.png
│   │   ├── 12_inventory_wastage_analysis.png
│   │   ├── 13_inventory_turnover_comparison.png
│   │   └── 14_gross_margin_by_category.png
│   ├── exports/                    # Star-Schema CSV Tables for Power BI
│   │   ├── FactOrders.csv
│   │   ├── FactOrderItems.csv
│   │   ├── DimProducts.csv
│   │   ├── DimLocations.csv
│   │   ├── DimInventory.csv
│   │   ├── FactWaste.csv
│   │   └── DimCalendar.csv
│   └── dax_measures.md             # Star schema guide & 20+ DAX formulas
├── data/                           # Data Storage
│   ├── raw/                        # 7 Normalized Raw Relational Tables
│   └── processed/                  # Cleaned Tables + Denormalized Master
├── notebooks/                      # 5 Interactive Analytical Jupyter Notebooks
│   ├── 01_data_cleaning.ipynb
│   ├── 02_sales_analysis.ipynb
│   ├── 03_product_analysis.ipynb
│   ├── 04_inventory_analysis.ipynb
│   └── 05_business_insights.ipynb
├── reports/                        # Executive Strategic Reports
│   └── business_insights.md        # Comprehensive 12-Question Decision Report
├── sql/                            # 6 Production SQL Analytics Scripts
│   ├── 01_kpi_metrics.sql          # 6 queries: Top-line executive KPIs
│   ├── 02_sales_analysis.sql       # 6 queries: Monthly MoM, channels, locations
│   ├── 03_product_analysis.sql     # 6 queries: Best/worst sellers, Pareto 80/20
│   ├── 04_time_analysis.sql        # 5 queries: Hourly rush, day-parts, weekend
│   ├── 05_inventory_analysis.sql   # 6 queries: ROP, valuation, wastage, suppliers
│   └── 06_profitability_analysis.sql # 5 queries: P&L bridge, item margins, COGS
├── src/                            # Modular Python Analytics Source Code
│   ├── __init__.py
│   ├── data_generation.py          # Benchmark QSR dataset generator
│   ├── data_cleaning.py            # Data cleaning & feature engineering
│   ├── sales_analysis.py           # Macro sales KPIs & location metrics
│   ├── product_analysis.py         # Product velocity & Pareto calculation
│   ├── time_analysis.py            # Hourly & day-part operational dynamics
│   ├── inventory_analysis.py       # Dynamic ROP & stock health modeling
│   ├── profitability_analysis.py   # Margin & P&L bridge calculations
│   ├── visualization.py            # 14 Matplotlib/Seaborn visualization suite
│   └── generate_notebooks.py       # Notebook generation utility
├── tests/                          # Automated Pytest Suite
│   ├── test_data_cleaning.py       # Data validation & feature tests
│   ├── test_sales_analysis.py      # Sales KPIs & Pareto logic tests
│   ├── test_inventory_analysis.py  # Inventory ROP & turnover tests
│   └── test_sql.py                 # SQLite database & query integrity tests
├── .gitignore                      # Environment ignore rules
├── main.py                         # Single-command pipeline orchestrator
├── README.md                       # Comprehensive project documentation
├── requirements.txt                # Production Python dependencies
└── qsr_analytics.db                # SQLite database (generated by main.py)
```

---

## 🚀 Installation & Execution

### 1. Clone the Repository
```bash
git clone https://github.com/NimaiGaba/qsr-sales-inventory-optimization.git
cd qsr-sales-inventory-optimization
```

### 2. Set Up Virtual Environment & Dependencies
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Run the Automated Analytics Pipeline
Execute the full data analytics pipeline with a single command:
```bash
python main.py
```
**Execution Sequence:**
1. Validates and ingests raw operational tables (`data/raw/`).
2. Cleanses records and engineers temporal features (`data/processed/`).
3. Builds SQLite relational database (`qsr_analytics.db`).
4. Executes all 28 queries across 6 SQL modules.
5. Performs Python sales, product, time, inventory, and margin analytics.
6. Generates 14 high-resolution charts (`dashboard/charts/`).
7. Exports 7 star-schema tables for Power BI (`dashboard/exports/`).
8. Validates the executive business report (`reports/business_insights.md`).
*Execution time: ~5.8 seconds.*

### 4. Run the Pytest Test Suite
Validate computational logic, data schemas, and SQL integrity:
```bash
pytest tests/ -v
```
*Result: 17 passed tests in ~1.2s.*

---

## 📈 Power BI Interactive Dashboard Setup

Complete DAX measure code and star-schema relationships are documented in [`dashboard/dax_measures.md`](dashboard/dax_measures.md).

### Quick Setup:
1. Open **Power BI Desktop**.
2. Select **Get Data** > **Text/CSV** and import all 7 files from `dashboard/exports/`.
3. In **Model View**, verify relationships connect dimensions (`DimCalendar`, `DimProducts`, `DimLocations`, `DimInventory`) to fact tables (`FactOrders`, `FactOrderItems`, `FactWaste`).
4. Create the `_Measures` table and copy the DAX measures from [`dashboard/dax_measures.md`](dashboard/dax_measures.md).
5. Build the 4 pages following the visual blueprint:
   - **Page 1: Executive Sales Overview**
   - **Page 2: Product Performance & Pareto**
   - **Page 3: Inventory Management & Supply Chain**
   - **Page 4: Operational & Time Performance**

---

## 📄 License & Attribution

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. Developed for Data Analyst, Business Analyst, and Business Intelligence portfolio demonstrations.
