"""
Notebook Generator Utility
==========================
Creates clean, interactive Jupyter Notebooks (.ipynb) in notebooks/
demonstrating step-by-step analytical workflows.
"""

import os
import json


def make_cell(cell_type: str, source: list) -> dict:
    """Create a Jupyter notebook cell dictionary."""
    if cell_type == "markdown":
        return {
            "cell_type": "markdown",
            "metadata": {},
            "source": [s + "\n" for s in source]
        }
    else:
        return {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [s + "\n" for s in source]
        }


def create_notebook(cells: list) -> dict:
    """Create a standard Jupyter notebook structure."""
    return {
        "cells": cells,
        "metadata": {
            "language_info": {
                "name": "python",
                "version": "3.10"
            },
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 5
    }


def build_all_notebooks(output_dir: str = "notebooks"):
    """Build all 5 required analytical Jupyter notebooks."""
    os.makedirs(output_dir, exist_ok=True)

    # 1. 01_data_cleaning.ipynb
    nb1_cells = [
        make_cell("markdown", [
            "# 01: QSR Transactional & Operational Data Cleaning",
            "This notebook demonstrates the end-to-end data hygiene, type casting, validation checks, and feature engineering process for **Artisan Crust Co.**"
        ]),
        make_cell("code", [
            "import os",
            "import sys",
            "import pandas as pd",
            "import numpy as np",
            "",
            "# Add project root to sys.path",
            "sys.path.append(os.path.abspath('..'))",
            "from src.data_cleaning import run_data_cleaning_pipeline",
            "",
            "processed_tables = run_data_cleaning_pipeline(raw_dir='../data/raw', processed_dir='../data/processed')",
            "df_master = processed_tables['master']",
            "df_master.info()"
        ]),
        make_cell("markdown", [
            "### Data Hygiene & Validation Checks",
            "Verify missing values, duplicates, and check that NetSales = GrossSales - Discount."
        ]),
        make_cell("code", [
            "print('Missing Values Count in Master Dataset:')",
            "print(df_master.isnull().sum()[df_master.isnull().sum() > 0])",
            "print('\\nMaster Record Count:', len(df_master))",
            "df_master[['GrossSales', 'DiscountAmount', 'NetSales', 'LineProfit']].describe()"
        ])
    ]
    with open(os.path.join(output_dir, "01_data_cleaning.ipynb"), "w", encoding="utf-8") as f:
        json.dump(create_notebook(nb1_cells), f, indent=2)

    # 2. 02_sales_analysis.ipynb
    nb2_cells = [
        make_cell("markdown", [
            "# 02: QSR Sales Performance & Channel Analysis",
            "Exploration of macro sales metrics, monthly trends, restaurant location revenue, and fulfillment channels."
        ]),
        make_cell("code", [
            "import os",
            "import sys",
            "import pandas as pd",
            "import matplotlib.pyplot as plt",
            "sys.path.append(os.path.abspath('..'))",
            "",
            "from src.sales_analysis import run_sales_analysis",
            "",
            "df_orders = pd.read_csv('../data/processed/orders_cleaned.csv')",
            "df_details = pd.read_csv('../data/processed/order_details_cleaned.csv')",
            "df_locations = pd.read_csv('../data/processed/locations_cleaned.csv')",
            "",
            "sales_res = run_sales_analysis(df_orders, df_details, df_locations)",
            "print('Sales KPIs:', sales_res['kpis'])",
            "sales_res['locations']"
        ]),
        make_cell("markdown", [
            "### Monthly Revenue Trend & MoM Growth",
            "Review monthly performance over the full 2024 calendar year."
        ]),
        make_cell("code", [
            "monthly_df = sales_res['monthly']",
            "monthly_df[['OrderMonthName', 'Monthly_Orders', 'NetRevenue', 'Monthly_AOV', 'MoMGrowthPct']]"
        ])
    ]
    with open(os.path.join(output_dir, "02_sales_analysis.ipynb"), "w", encoding="utf-8") as f:
        json.dump(create_notebook(nb2_cells), f, indent=2)

    # 3. 03_product_analysis.ipynb
    nb3_cells = [
        make_cell("markdown", [
            "# 03: Product Performance & Pareto 80/20 Analysis",
            "Analyzes best-sellers, category mix, and Pareto cumulative revenue contribution."
        ]),
        make_cell("code", [
            "import os",
            "import sys",
            "import pandas as pd",
            "sys.path.append(os.path.abspath('..'))",
            "from src.product_analysis import run_product_analysis",
            "",
            "df_details = pd.read_csv('../data/processed/order_details_cleaned.csv')",
            "prod_res = run_product_analysis(df_details)",
            "print('Top 5 Menu Items by Revenue:')",
            "prod_res['top_by_revenue'].head(5)"
        ]),
        make_cell("markdown", [
            "### Pareto 80/20 Cumulative Distribution",
            "Identify the core SKUs that generate 80% of total revenue."
        ]),
        make_cell("code", [
            "pareto = prod_res['pareto']",
            "print(f\"Total SKUs driving 80% of revenue: {sum(pareto['ParetoSegment'] == 'Core Revenue Driver (Top 80%)')}\")",
            "pareto.head(10)"
        ])
    ]
    with open(os.path.join(output_dir, "03_product_analysis.ipynb"), "w", encoding="utf-8") as f:
        json.dump(create_notebook(nb3_cells), f, indent=2)

    # 4. 04_inventory_analysis.ipynb
    nb4_cells = [
        make_cell("markdown", [
            "# 04: Inventory Optimization & Kitchen Wastage Analysis",
            "Evaluates stock health, calculates reorder points (ROP), turnover velocity, and wastage costs."
        ]),
        make_cell("code", [
            "import os",
            "import sys",
            "import pandas as pd",
            "sys.path.append(os.path.abspath('..'))",
            "from src.inventory_analysis import run_inventory_analysis",
            "",
            "df_inv = pd.read_csv('../data/processed/inventory_cleaned.csv')",
            "df_sup = pd.read_csv('../data/processed/suppliers_cleaned.csv')",
            "df_wst = pd.read_csv('../data/processed/inventory_waste_cleaned.csv')",
            "df_ord = pd.read_csv('../data/processed/orders_cleaned.csv')",
            "",
            "inv_res = run_inventory_analysis(df_inv, df_sup, df_wst, df_ord)",
            "print('Inventory Turnover Ratio:', inv_res['turnover']['InventoryTurnoverRatio'], 'x')",
            "print('Total Inventory Capital Valuation: $', inv_res['turnover']['TotalInventoryValuation'])",
            "inv_res['health'][['ItemName', 'Category', 'CurrentStock', 'ReorderLevel', 'StockClassification']].head(10)"
        ]),
        make_cell("markdown", [
            "### Food Wastage Breakdown",
            "Examine root causes and financial impact of food wastage."
        ]),
        make_cell("code", [
            "wst_summary = inv_res['wastage']",
            "print('Total Kitchen Wastage Cost: $', wst_summary['TotalWasteCostUSD'])",
            "wst_summary['ByReason']"
        ])
    ]
    with open(os.path.join(output_dir, "04_inventory_analysis.ipynb"), "w", encoding="utf-8") as f:
        json.dump(create_notebook(nb4_cells), f, indent=2)

    # 5. 05_business_insights.ipynb
    nb5_cells = [
        make_cell("markdown", [
            "# 05: Business Insights & Strategic Recommendations",
            "Executive synthesis answering key management questions with computed KPIs and actionable financial proposals."
        ]),
        make_cell("code", [
            "import os",
            "import sys",
            "import pandas as pd",
            "sys.path.append(os.path.abspath('..'))",
            "from src.profitability_analysis import run_profitability_analysis",
            "",
            "df_orders = pd.read_csv('../data/processed/orders_cleaned.csv')",
            "df_details = pd.read_csv('../data/processed/order_details_cleaned.csv')",
            "df_locations = pd.read_csv('../data/processed/locations_cleaned.csv')",
            "",
            "prof_res = run_profitability_analysis(df_orders, df_details, df_locations)",
            "print('P&L Summary:', prof_res['pl_summary'])",
            "prof_res['locations']"
        ])
    ]
    with open(os.path.join(output_dir, "05_business_insights.ipynb"), "w", encoding="utf-8") as f:
        json.dump(create_notebook(nb5_cells), f, indent=2)

    print(f"Created all 5 interactive notebooks in {output_dir}")


if __name__ == "__main__":
    build_all_notebooks()
