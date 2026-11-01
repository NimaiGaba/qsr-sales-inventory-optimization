# QSR Sales & Inventory Optimization

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![SQL](https://img.shields.io/badge/SQL-SQLite%20%7C%20ANSI%20SQL-orange.svg)](https://www.sqlite.org/)
[![Power BI](https://img.shields.io/badge/Power%20BI-Star%20Schema%20%26%20DAX-yellow.svg)](https://powerbi.microsoft.com/)
[![Tests](https://img.shields.io/badge/Tests-Pytest%2022%2F22%20Passing-brightgreen.svg)](https://pytest.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An enterprise-grade, end-to-end **Data Analytics, SQL, and Business Intelligence project** modeling transactional sales, consumer dining day-parts, recipe-level ingredient consumption, standard inventory turnover, and dynamic reorder-point optimization for **Artisan Crust Co.**, a simulated 4-unit regional Quick Service Restaurant (QSR) enterprise.

> [!IMPORTANT]
> **Synthetic Dataset & Simulation Disclosure:**  
> This project is conducted on a high-fidelity **synthetic business analytics dataset** generated via `data_generation.py`. The simulated restaurant enterprise models 33,051 customer transactions, 65,851 line items, 32 standardized menu items, a 127-link Bill of Materials (BOM) recipe architecture, 24 tracked inventory ingredients, 6 regional suppliers, and 1,094 kitchen waste logs across fiscal year 2024 (January 1 to December 31, 2024; 366 days).  
> **None of the records represent actual proprietary restaurant customer data.** All analytical findings, turnover rates, and financial opportunity models reflect this controlled business simulation, synthesized using empirical distributions informed by National Restaurant Association (NRA) industry operating benchmarks.
>
> **Pure Analytics Scope:** This repository contains **no machine learning models, predictive algorithms, or artificial neural networks**. All insights and optimizations are derived from rigorous SQL relational querying, Pandas data engineering, Bill of Materials recipe explosion, inventory turnover mathematics, and Power BI star-schema DAX architecture.

---

## 📌 Executive Summary & Verified Macro Financials

All metrics have been verified against the underlying SQLite database (`qsr_analytics.db`) and processed transactional tables:

| Executive Metric | Measured Value | Standard Formula / Operational Context |
| :--- | :---: | :--- |
| **Gross Revenue (Gross Merchandise Value)** | **$1,079,004.26** | $\sum \text{GrossSales}$ (Pre-discount transactional menu volume) |
| **Promotional Discounts Awarded** | **$11,716.24** | $\sum \text{DiscountAmount}$ (1.09% effective promotional discount rate) |
| **Net Operating Revenue (Net Sales)** | **$1,067,288.02** | $\text{Gross Revenue} - \text{Promotional Discounts}$ |
| **Cost of Goods Sold (COGS)** | **$318,309.00** | $\sum \text{TotalCost}$ (**29.82% food cost ratio**; NRA benchmark: 28–32%) |
| **Gross Profit** | **$748,979.02** | $\text{Net Revenue} - \text{COGS}$ (**70.18% gross margin**) |
| **Total Orders Fulfilled** | **33,051** | Distinct transaction tickets (~90.3 orders/day chain-wide) |
| **Total Menu Items Sold** | **65,851** | Distinct line item quantity sold across all tickets |
| **Average Order Value (AOV)** | **$32.29** | $\text{Net Revenue} / \text{Total Orders}$ ($34.50+ on weekend evenings) |
| **Average Basket Depth** | **1.99 items** | $\text{Total Units Sold} / \text{Total Orders}$ |
| **Beginning Inventory Valuation** | **$24,897.00** | $\sum (\text{BeginningStock} \times \text{UnitCost})$ (Jan 1, 2024) |
| **Ending Inventory Valuation** | **$22,882.40** | $\sum (\text{CurrentStock} \times \text{UnitCost})$ (Dec 31, 2024) |
| **Average Inventory Valuation** | **$23,889.70** | $(\text{Beginning Value} + \text{Ending Value}) / 2.0$ |
| **Standard Inventory Turnover Ratio** | **13.32x** | $\text{Annual COGS} / \text{Average Inventory Value}$ |
| **Days Sales of Inventory (DSI / Days to Turn)**| **27.5 days** | $366 / \text{Inventory Turnover Ratio}$ |
| **Annual Kitchen Wastage Dollar Loss** | **$25,202.93** | Across 1,094 recorded incidents (2.36% of net sales) |

---

## 🎯 Business Problem & Core Objectives

High-volume Quick Service Restaurants face severe margin pressures and supply chain volatility:
1. **Kitchen Rush Bottlenecks:** Concentrated lunch and dinner peak hours create oven queueing and prep delays when ingredient mise-en-place is uncalibrated.
2. **Perishable Shrinkage vs. Stockout Risk:** Excess perishable inventory leads to food spoilage, while carrying too little causes stockouts of core signature revenue drivers.
3. **Flawed Inventory Estimations:** Crude inventory assumptions (e.g. estimating daily consumption as $\text{MaxStock} / 20$) distort reorder timing and tie up working capital.

This project delivers end-to-end data analytics solutions:
- **Sales & Day-Part Analysis:** Map hourly transaction volume and weekday vs weekend dining patterns.
- **Recipe Bill of Materials (BOM) Consumption:** Calculate empirical ingredient depletion from sales order history multiplied by standardized recipe weights across all 366 days.
- **Standard Inventory Turnover:** Calculate opening, closing, and average inventory valuations to determine true turnover ratios and days sales of inventory.
- **Dynamic Reorder Point (ROP) Modeling:** Formulate demand-variability safety stock and dynamic reorder triggers to replace static gut-feel ordering.
- **Power BI Executive Intelligence:** Deliver a 4-page star-schema dashboard design with verified DAX measures and clean data exports.

---

## 🛠️ Technology Stack & Project Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                    QSR Data Analytics Architecture                           │
├───────────────────┬───────────────────┬───────────────────┬──────────────────┤
│  Data Layer       │ Analytics Layer   │ SQL / Database    │ BI & Reporting   │
├───────────────────┼───────────────────┼───────────────────┼──────────────────┤
│ • 8 Relational    │ • Pandas 2.2      │ • SQLite DB       │ • Power BI Model │
│   QSR Tables      │ • NumPy 1.26      │ • 6 SQL Modules   │ • 24 DAX Meas.   │
│ • Data Cleaning   │ • Matplotlib 3.9  │ • 29 Queries      │ • 14 Publication │
│   & Validation    │ • Seaborn 0.13    │ • Window Funcs,   │   EDA Charts     │
│ • Recipe BOM      │ • Pytest (22/22)  │   CTEs, Views     │ • Exec Insights  │
│   Explosion       │ • Python Logging  │ • Turnovers, ROP  │   Report (MD)    │
└───────────────────┴───────────────────┴───────────────────┴──────────────────┘
```

- **Python & Data Engineering:** Schema validation, type casting, date normalization, temporal feature engineering, and recipe consumption calculation (`src/data_cleaning.py`, `src/inventory_analysis.py`).
- **SQL Analytics Engine:** 6 SQL scripts executing 29 queries analyzing sales trends, product rankings, peak operating hours, standard inventory turnover, and location profitability (`sql/`).
- **Statistical Visualization Suite:** 14 high-resolution charts saved to `dashboard/charts/`.
- **Power BI Data Model:** Star schema connecting fact tables (`FactOrders`, `FactOrderItems`, `FactWaste`) with dimension tables (`DimProducts`, `DimLocations`, `DimInventory`, `DimRecipes`, `DimCalendar`).
- **Automated Test Suite:** 22 unit & integration tests using `pytest` verifying computational accuracy across profitability, inventory math, and SQL output.

---

## 🔬 Core Analytical Methodologies

### 1. Recipe Bill of Materials (BOM) Consumption Tracking
Instead of relying on crude heuristics, daily ingredient consumption is computed empirically:
$$\text{Line Ingredient Usage} = \text{Order Quantity} \times \text{Recipe Quantity Per Unit}$$
- Daily usage is aggregated across all 366 calendar days in 2024.
- Days with zero demand are explicitly indexed with $0.0$ to prevent upward skew of average daily consumption.
- Empirical mean ($\mu_{\text{daily}}$) and demand standard deviation ($\sigma_{\text{daily}}$) are computed directly from actual sales history.

### 2. Standard Inventory Turnover Ratio
Adhering to standard managerial accounting:
$$\text{Beginning Inventory Value} = \sum (\text{BeginningStock} \times \text{UnitCost}) = \$24,897.00$$
$$\text{Ending Inventory Value} = \sum (\text{CurrentStock} \times \text{UnitCost}) = \$22,882.40$$
$$\text{Average Inventory Value} = \frac{\text{Beginning Value} + \text{Ending Value}}{2} = \$23,889.70$$
$$\text{Inventory Turnover Ratio} = \frac{\text{Annual COGS}}{\text{Average Inventory Value}} = \frac{\$318,309.00}{\$23,889.70} = 13.32\times$$
$$\text{Days Sales of Inventory (DSI)} = \frac{366}{\text{Inventory Turnover Ratio}} = 27.5\text{ days}$$

### 3. Dynamic Reorder Point (ROP) & Safety Stock
To achieve a 95% cycle-service level ($Z = 1.65$):
$$\text{Safety Stock} = Z \times \sigma_{\text{daily}} \times \sqrt{\text{LeadTimeDays}}$$
$$\text{Reorder Point (ROP)} = (\mu_{\text{daily}} \times \text{LeadTimeDays}) + \text{Safety Stock}$$
$$\text{Stock Coverage (Days of Supply)} = \frac{\text{CurrentStock}}{\mu_{\text{daily}}}$$

### 4. Profitability Hierarchy
Profitability metrics are calculated without conflation:
$$\text{Net Revenue} = \text{Gross Revenue} - \text{Promotional Discounts}$$
$$\text{Gross Profit} = \text{Net Revenue} - \text{COGS}$$
$$\text{Gross Margin \%} = \frac{\text{Gross Profit}}{\text{Net Revenue}} \times 100$$
*(Operating expenses such as labor and rent are out of scope; EBITDA is explicitly not claimed).*

---

## 📊 Exploratory Visualizations & Dashboard Charts

The automated pipeline generates 14 publication-grade analytical charts in `dashboard/charts/`:

| Chart File | Visualization Title | Key Business Metric |
| :--- | :--- | :--- |
| `01_monthly_revenue_trend.png` | Monthly Net Sales Trend (2024) | Steady revenue ~$85k–$95k/month |
| `02_daily_revenue_trend.png` | Daily Net Sales & 7-Day Moving Avg | Clear cyclical weekend demand spikes |
| `03_hourly_sales_distribution.png` | Hourly Order Volume Distribution | Bi-modal peaks: 12:00 PM and 6:00 PM |
| `04_weekday_vs_weekend_sales.png` | Weekday vs Weekend Sales Performance | Weekends generate 55.68% of annual revenue |
| `05_revenue_by_product_category.png` | Revenue Contribution by Menu Category | Pizza (59.5%) & Combos (24.5%) lead |
| `06_top_10_products_by_revenue.png` | Top 10 Revenue-Generating Menu Items | Pepperoni Feast leads with $197,134 |
| `07_top_10_products_by_quantity.png` | Top 10 Menu Items by Volume Sold | Pepperoni Feast leads with 11,821 units |
| `08_aov_trends.png` | Average Order Value Distribution | Mean AOV $32.29 ($34.50+ on weekends) |
| `09_payment_method_distribution.png` | Payment Method Transaction Share | Credit Card (45.2%) and Mobile Wallet (28.4%) |
| `10_product_performance_comparison.png`| Product Volume vs Gross Margin Scatter | High-margin beverage vs volume pizza matrix |
| `11_inventory_stock_distribution.png` | Inventory Stock vs Par Reorder Levels | SKU health & low stock alert flags |
| `12_inventory_wastage_analysis.png` | Food Wastage Loss by Root Cause | Expired shelf-life accounts for 47.1% |
| `13_inventory_turnover_comparison.png`| Inventory Capital by Ingredient Category| Dry goods and dairy represent 68% capital |
| `14_gross_margin_by_category.png` | Gross Profit Margin % by Menu Category | Beverages (83.0%) and Pizza (70.0%) |

---

## 📈 Key Analytical Insights

### 1. Product Pareto Distribution
- **Pepperoni Feast** is the single highest-performing menu item, generating **$197,134.07** (18.47% of total sales) and **$138,704.37** in gross profit (70.36% margin).
- The top 3 signature pizzas (*Pepperoni Feast*, *BBQ Chicken Supreme*, and *Margherita Classic*) drive **$418,305.35** (39.19% of total revenue).
- **Pareto Principle Validated:** Just **9 of 32 menu items** account for over **80% of total revenue**.

### 2. Bi-Modal Day-Part Rushes
- **Lunch Rush (12:00 PM – 2:00 PM):** 9,932 orders (30.05% of volume). Peak hour is **12:00 PM** (5,300 orders; $171,190 annual sales).
- **Dinner Rush (6:00 PM – 8:00 PM):** 8,240 orders (24.93% of volume). Peak hour is **6:00 PM** (4,982 orders; $160,891 annual sales).
- Over **55% of all daily orders** occur within just 4 operating hours.

### 3. Weekend Revenue Concentration
- **Friday ($193,597.33)**, **Saturday ($199,691.52)**, and **Sunday ($201,000.75)** account for **55.68% of total annual sales** ($594,289.60).
- Weekend AOV ($34.42) is significantly higher than weekday AOV ($29.85) due to family bundle purchases.

### 4. Perishable Waste & Spoilage Root Causes
- Annual kitchen wastage totaled **$25,202.93** across 1,094 incidents.
- **Expired Shelf-Life** is the #1 driver of food waste, accounting for **$11,861.39 (47.06%)**, followed by **Preparation Trim / Spillage ($6,321.50, 25.08%)**.
- Fast-moving perishable herbs and produce (*Genovese Basil*, *Romaine Hearts*, *Button Mushrooms*) periodically fall below dynamic safety stock levels.

---

## 💡 Modeled Gross Profit Opportunity Scenarios

In initial exploratory planning, a hypothetical financial figure of "$79,100" was discussed. In accordance with rigorous financial analysis:
1. **Operating expenses (labor, rent, utilities) are not tracked** in raw ticket ledgers; hence claiming an "EBITDA lift" was an analytical error.
2. Below, we present modeled **Gross Profit Opportunity Scenarios** with full mathematical transparency:

| Opportunity Lever | Baseline Metric | Conservative (+20%) | Moderate (+35%) | Aggressive (+50%) | Methodology & Assumptions |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **A. Expired Waste Reduction** | $11,861.39 (Expired Waste) | **+$2,372 / yr** | **+$4,151 / yr** | **+$5,931 / yr** | COGS savings via twice-weekly deliveries and FIFO date-labeling. |
| **B. Midweek Lunch Volume Lift** | $472,998.42 (Mon–Thu Sales) | **+$6,640 / yr** | **+$11,620 / yr** | **+$16,600 / yr** | Gross profit from incremental lunch combo sales (2%–5% lift @ 70.2% margin). |
| **C. Beverage Attach Optimization**| $38,420.42 (Beverage Sales) | **+$3,188 / yr** | **+$6,375 / yr** | **+$9,563 / yr** | Gross profit from prompt-driven drink attach (10%–30% lift @ 83.0% margin). |
| **Total Estimated Gross Profit Opportunity** | — | **+$12,200 / yr** | **+$22,146 / yr** | **+$32,094 / yr** | **Non-guaranteed exploratory projection across 4 locations.** |

---

## 📊 Power BI Dashboard Architecture

> **Implementation Note:** Power BI Desktop is not installed on this headless execution environment. Therefore, this repository provides complete star-schema CSV exports in `dashboard/exports/`, full data modeling specifications, and verified DAX formulas in [`dashboard/dax_measures.md`](dashboard/dax_measures.md).

### Star Schema Architecture
```
                     ┌──────────────────┐
                     │   DimCalendar    │
                     │      (Date)      │
                     └────────┬─────────┘
                              │ 1
                              │
                              │ * (OrderDate)
┌──────────────────┐          ▼          ┌──────────────────┐
│   DimLocations   │1 ────────*──────── 1│   DimProducts    │
│   (LocationID)   │      FactOrders     │   (ProductID)    │
└──────────────────┘     (Gross, Net)    └────────┬─────────┘
                              │ 1                 │ 1
                              │                   │
                              │ * (OrderID)       │ * (ProductID)
                              ▼                   ▼
                     ┌──────────────────────────────┐
                     │        FactOrderItems        │
                     │ (Qty, TotalPrice, LineProfit)│
                     └──────────────────────────────┘
                              ▲
                              │ 1 (InventoryID)
                     ┌────────┴─────────┐
                     │   DimInventory   │
                     │  (Beginning/End) │
                     └────────┬─────────┘
                              │ 1
                              │ * (InventoryID)
                     ┌────────┴─────────┐
                     │    FactWaste     │
                     │(WasteCost, Reason│
                     └──────────────────┘
```

### 4-Page Dashboard Layout:
- **Page 1: Executive Overview:** Top KPI ribbon (`Total Revenue`, `Total Net Sales`, `Gross Profit`, `Gross Margin %`, `Total Orders`, `AOV`), monthly revenue spline trend, category donut chart, location performance matrix.
- **Page 2: Sales & Product Performance:** Top 10 products bar chart, bottom 5 slow-moving SKUs, quantity analysis grid, day-of-week sales, hourly order heatmap.
- **Page 3: Inventory Management:** Ending inventory value, standard inventory turnover ratio, inventory days (DSI), low stock alert items, kitchen waste breakdown by root cause, dynamic reorder recommendations table.
- **Page 4: Operational Performance:** Peak operating hours distribution, payment method split, location revenue by channel (Dine-in vs Delivery vs Takeout), basket depth metrics.

---

## 📁 Repository Structure

```
qsr-sales-inventory-optimization/
├── dashboard/                      # Power BI Assets & Data Model Documentation
│   ├── charts/                     # 14 Publication-Grade Visualizations (PNG)
│   ├── exports/                    # Star-Schema CSV Tables for Power BI
│   │   ├── FactOrders.csv
│   │   ├── FactOrderItems.csv
│   │   ├── DimProducts.csv
│   │   ├── DimLocations.csv
│   │   ├── DimInventory.csv
│   │   ├── DimRecipes.csv
│   │   ├── FactWaste.csv
│   │   ├── DimCalendar.csv
│   │   └── ReportReorderRecommendations.csv
│   └── dax_measures.md             # Star schema guide & 24 DAX formulas
├── data/                           # Data Storage
│   ├── raw/                        # 8 Raw Relational Tables
│   └── processed/                  # Cleaned Tables + Master Denormalized CSV
├── notebooks/                      # 5 Interactive Analytical Jupyter Notebooks
│   ├── 01_data_cleaning.ipynb
│   ├── 02_sales_analysis.ipynb
│   ├── 03_product_analysis.ipynb
│   ├── 04_inventory_analysis.ipynb
│   └── 05_profitability_analysis.ipynb
├── reports/                        # Executive Analytical Reports
│   ├── business_insights.md        # Comprehensive 12-question analytical report
│   └── reorder_recommendations.csv # SKU-level reorder actions & safety stock
├── sql/                            # 6 Modular Relational SQL Scripts (29 queries)
│   ├── 01_kpi_metrics.sql
│   ├── 02_sales_analysis.sql
│   ├── 03_product_analysis.sql
│   ├── 04_time_analysis.sql
│   ├── 05_inventory_analysis.sql
│   └── 06_profitability_analysis.sql
├── src/                            # Production Python Analytics Modules
│   ├── data_generation.py          # Realistic QSR benchmark data generator
│   ├── data_cleaning.py            # Cleaning, type casting, feature engineering
│   ├── sales_analysis.py           # Core sales and location analytics
│   ├── product_analysis.py         # Pareto analysis and menu metrics
│   ├── time_analysis.py            # Hourly and day-of-week dynamics
│   ├── inventory_analysis.py       # BOM consumption, standard turnover, dynamic ROP
│   ├── profitability_analysis.py   # Gross margins and P&L bridge
│   ├── visualization.py            # 14 Matplotlib/Seaborn charts
│   └── generate_notebooks.py       # Automated Jupyter notebook generator
├── tests/                          # Automated Pytest Test Suite
│   ├── test_data_cleaning.py
│   ├── test_inventory_analysis.py
│   ├── test_sales_analysis.py
│   ├── test_profitability_and_turnover.py
│   └── test_sql.py
├── main.py                         # Automated end-to-end pipeline orchestrator
├── pipeline.log                    # Execution log file
├── qsr_analytics.db                # SQLite database with all tables and views
├── requirements.txt                # Python package dependencies
└── README.md                       # Comprehensive project documentation
```

---

## 🚀 Installation & Execution

### 1. Clone Repository & Setup Virtual Environment
```bash
git clone https://github.com/NimaiGaba/qsr-sales-inventory-optimization.git
cd qsr-sales-inventory-optimization

python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Complete End-to-End Analytics Pipeline
```bash
python main.py
```
*Executes raw data generation, data hygiene, SQLite database loading, 29 SQL queries, Python analytics, 14 chart generations, and Power BI star-schema CSV exports in ~6 seconds.*

### 4. Run Pytest Test Suite
```bash
pytest tests/ -v
```
*Executes all 22 unit and integration tests verifying revenue integrity, net sales math, standard inventory turnover, recipe BOM consumption, safety stock ROP, and SQL queries.*

---

## ⚖️ Assumptions & Limitations

1. **Synthetic Dataset Nature:** The dataset is a mathematically controlled simulation. While modeled upon realistic QSR operational parameters (e.g., NRA food cost benchmarks), it does not account for real-world supplier stockouts, localized weather disruptions, or economic inflation.
2. **Deterministic Lead Times:** Supplier lead times are modeled as contractually fixed intervals (2 to 5 days). In live restaurant environments, lead times fluctuate based on transit conditions.
3. **Absence of Operating Expenses:** The dataset contains ticket-level sales and ingredient COGS. It does not track kitchen hourly wages, store leases, or franchise fees; therefore, EBITDA cannot be computed.
4. **Normal Demand Distribution Assumption:** Safety stock calculations assume daily ingredient demand follows an approximately normal distribution.

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
