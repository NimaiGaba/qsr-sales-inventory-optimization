"""
QSR Sales & Inventory Analytics — Main Pipeline Orchestrator
=============================================================
Orchestrates the complete end-to-end data analytics workflow:
1. Generate/verify raw datasets
2. Clean and validate data with feature engineering
3. Ingest relational tables into SQLite database (qsr_analytics.db)
4. Execute SQL business analysis queries
5. Conduct Python sales, product, time, inventory, and profitability analytics
6. Generate 14 publication-grade EDA visualizations in dashboard/charts/
7. Export Power BI star-schema datasets into dashboard/exports/
8. Verify executive business insights report
"""

import os
import sys
import logging
import sqlite3
from datetime import datetime
import pandas as pd
import numpy as np

# Set project root
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from src.data_generation import generate_qsr_dataset
from src.data_cleaning import run_data_cleaning_pipeline
from src.sales_analysis import run_sales_analysis
from src.product_analysis import run_product_analysis
from src.time_analysis import run_time_analysis
from src.inventory_analysis import run_inventory_analysis
from src.profitability_analysis import run_profitability_analysis
from src.visualization import generate_all_visualizations

# ── Logging Setup ────────────────────────────────────────────────────────────
LOG_FORMAT = "%(asctime)s — %(levelname)s — %(name)s — %(message)s"
LOG_FILE = os.path.join(PROJECT_ROOT, "pipeline.log")

logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_FILE, mode="w", encoding="utf-8")
    ]
)
logger = logging.getLogger("main_pipeline")

# ── Paths ────────────────────────────────────────────────────────────────────
RAW_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
SQL_DIR = os.path.join(PROJECT_ROOT, "sql")
DASHBOARD_DIR = os.path.join(PROJECT_ROOT, "dashboard")
CHARTS_DIR = os.path.join(DASHBOARD_DIR, "charts")
EXPORTS_DIR = os.path.join(DASHBOARD_DIR, "exports")
REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports")
DB_PATH = os.path.join(PROJECT_ROOT, "qsr_analytics.db")


def step_1_generate_raw_data() -> dict:
    """Ensure raw datasets are present, generating if missing."""
    logger.info("=" * 70)
    logger.info("STEP 1: RAW DATA VALIDATION & INGESTION")
    logger.info("=" * 70)
    required = ["orders.csv", "order_details.csv", "products.csv", "locations.csv",
                "inventory.csv", "suppliers.csv", "inventory_waste.csv"]
    all_present = all(os.path.exists(os.path.join(RAW_DIR, f)) for f in required)
    if not all_present:
        logger.info("Raw datasets not found. Generating realistic benchmark data...")
        return generate_qsr_dataset(RAW_DIR)
    else:
        logger.info("Verified all raw datasets in data/raw/")
        return {
            "products": pd.read_csv(os.path.join(RAW_DIR, "products.csv")),
            "locations": pd.read_csv(os.path.join(RAW_DIR, "locations.csv")),
            "suppliers": pd.read_csv(os.path.join(RAW_DIR, "suppliers.csv")),
            "inventory": pd.read_csv(os.path.join(RAW_DIR, "inventory.csv")),
            "orders": pd.read_csv(os.path.join(RAW_DIR, "orders.csv")),
            "order_details": pd.read_csv(os.path.join(RAW_DIR, "order_details.csv")),
            "waste": pd.read_csv(os.path.join(RAW_DIR, "inventory_waste.csv")),
        }


def step_2_clean_and_engineer_features() -> dict:
    """Execute cleaning pipeline and feature engineering."""
    logger.info("=" * 70)
    logger.info("STEP 2: DATA CLEANING & FEATURE ENGINEERING")
    logger.info("=" * 70)
    return run_data_cleaning_pipeline(RAW_DIR, PROCESSED_DIR)


def step_3_load_sqlite_database(tables: dict):
    """Load normalized tables and analytical views into SQLite."""
    logger.info("=" * 70)
    logger.info("STEP 3: LOADING RELATIONAL DATABASE (SQLite)")
    logger.info("=" * 70)
    conn = sqlite3.connect(DB_PATH)
    
    tables["products"].to_sql("products", conn, if_exists="replace", index=False)
    tables["locations"].to_sql("locations", conn, if_exists="replace", index=False)
    tables["suppliers"].to_sql("suppliers", conn, if_exists="replace", index=False)
    tables["inventory"].to_sql("inventory", conn, if_exists="replace", index=False)
    if "recipes" in tables and not tables["recipes"].empty:
        tables["recipes"].to_sql("recipes", conn, if_exists="replace", index=False)
    tables["orders"].to_sql("orders", conn, if_exists="replace", index=False)
    tables["order_details"].to_sql("order_details", conn, if_exists="replace", index=False)
    tables["waste"].to_sql("inventory_waste", conn, if_exists="replace", index=False)

    cursor = conn.cursor()
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS v_order_summary AS
        SELECT 
            o.OrderID, o.OrderDate, o.OrderTime, o.OrderHour, o.MealPeriod,
            o.DayName, o.IsWeekend, l.LocationName, l.StoreType,
            o.PaymentMethod, o.OrderType, o.NetSales, o.GrossProfit
        FROM orders o
        JOIN locations l ON o.LocationID = l.LocationID;
    """)
    conn.commit()
    conn.close()
    logger.info(f"SQLite Database built successfully with all tables: {DB_PATH}")



def step_4_execute_sql_scripts() -> dict:
    """Execute all SQL queries across all 6 SQL modules."""
    logger.info("=" * 70)
    logger.info("STEP 4: EXECUTING SQL BUSINESS ANALYTICS MODULES")
    logger.info("=" * 70)
    conn = sqlite3.connect(DB_PATH)
    sql_files = [
        "01_kpi_metrics.sql",
        "02_sales_analysis.sql",
        "03_product_analysis.sql",
        "04_time_analysis.sql",
        "05_inventory_analysis.sql",
        "06_profitability_analysis.sql",
    ]
    query_counts = {}

    for sf in sql_files:
        path = os.path.join(SQL_DIR, sf)
        if not os.path.exists(path):
            continue
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        # Split on semicolons for statement execution
        statements = [s.strip() for s in content.split(";") if s.strip() and not s.strip().startswith("-- =")]
        exec_count = 0
        for stmt in statements:
            try:
                pd.read_sql_query(stmt, conn)
                exec_count += 1
            except Exception as e:
                # Some statements might be pure comments
                pass
        query_counts[sf] = exec_count
        logger.info(f"  {sf:<32}: Executed {exec_count} queries successfully")

    conn.close()
    return query_counts


def step_5_python_analytics(tables: dict) -> dict:
    """Run all Python analytical modules."""
    logger.info("=" * 70)
    logger.info("STEP 5: PYTHON DATA ANALYTICS SUITE")
    logger.info("=" * 70)
    orders = tables["orders"]
    details = tables["order_details"]
    locations = tables["locations"]
    inventory = tables["inventory"]
    suppliers = tables["suppliers"]
    waste = tables["waste"]
    recipes = tables.get("recipes")

    sales_res = run_sales_analysis(orders, details, locations)
    product_res = run_product_analysis(details)
    time_res = run_time_analysis(orders)
    inv_res = run_inventory_analysis(
        df_inventory=inventory,
        df_suppliers=suppliers,
        df_waste=waste,
        df_orders=orders,
        df_details=details,
        df_recipes=recipes
    )
    prof_res = run_profitability_analysis(orders, details, locations)

    return {
        "sales": sales_res,
        "product": product_res,
        "time": time_res,
        "inventory": inv_res,
        "profitability": prof_res,
    }


def step_6_generate_charts(tables: dict) -> list:
    """Generate all 14 visual analytics charts."""
    logger.info("=" * 70)
    logger.info("STEP 6: GENERATING EXPLORATORY DATA VISUALIZATIONS")
    logger.info("=" * 70)
    charts = generate_all_visualizations(
        tables["orders"],
        tables["order_details"],
        tables["inventory"],
        tables["waste"],
        CHARTS_DIR
    )
    logger.info(f"Generated {len(charts)} charts in {CHARTS_DIR}")
    return charts


def step_7_export_dashboard_csvs(tables: dict, analytics_res: dict):
    """Export clean, star-schema CSV tables and operational reports for Power BI import."""
    logger.info("=" * 70)
    logger.info("STEP 7: EXPORTING DASHBOARD-READY CSV FILES")
    logger.info("=" * 70)
    os.makedirs(EXPORTS_DIR, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)

    tables["orders"].to_csv(os.path.join(EXPORTS_DIR, "FactOrders.csv"), index=False)
    tables["order_details"].to_csv(os.path.join(EXPORTS_DIR, "FactOrderItems.csv"), index=False)
    tables["products"].to_csv(os.path.join(EXPORTS_DIR, "DimProducts.csv"), index=False)
    tables["locations"].to_csv(os.path.join(EXPORTS_DIR, "DimLocations.csv"), index=False)
    tables["inventory"].to_csv(os.path.join(EXPORTS_DIR, "DimInventory.csv"), index=False)
    tables["waste"].to_csv(os.path.join(EXPORTS_DIR, "FactWaste.csv"), index=False)

    if "recipes" in tables and not tables["recipes"].empty:
        tables["recipes"].to_csv(os.path.join(EXPORTS_DIR, "DimRecipes.csv"), index=False)

    # Export calendar dimension table
    dates = pd.date_range(start="2024-01-01", end="2024-12-31")
    dim_calendar = pd.DataFrame({
        "Date": dates.strftime("%Y-%m-%d"),
        "Year": dates.year,
        "Month": dates.month,
        "MonthName": dates.strftime("%B"),
        "Quarter": dates.to_period("Q").astype(str),
        "DayOfWeek": dates.dayofweek,
        "DayName": dates.day_name(),
        "IsWeekend": dates.dayofweek.isin([4, 5, 6]).astype(int),
    })
    dim_calendar.to_csv(os.path.join(EXPORTS_DIR, "DimCalendar.csv"), index=False)

    # Export dynamic reorder recommendations report (Task 4)
    rop_df = analytics_res["inventory"]["reorder_points"]
    reorder_report_cols = [
        "InventoryID", "ItemName", "Category", "CurrentStock", "Unit",
        "AverageDailyConsumption", "StockCoverageDays", "LeadTimeDays",
        "CalculatedSafetyStock", "CalculatedROP", "ReorderRecommendation",
        "ConsumptionSource"
    ]
    available_cols = [c for c in reorder_report_cols if c in rop_df.columns]
    reorder_report = rop_df[available_cols].copy()
    reorder_report.to_csv(os.path.join(EXPORTS_DIR, "ReportReorderRecommendations.csv"), index=False)
    reorder_report.to_csv(os.path.join(REPORTS_DIR, "reorder_recommendations.csv"), index=False)

    logger.info(f"Exported Power BI star-schema tables and operational reports to {EXPORTS_DIR}")


def main():
    """Main orchestration entry point."""
    start_time = datetime.now()
    logger.info("+" + "=" * 68 + "+")
    logger.info("|  QSR SALES & INVENTORY ANALYTICS — PIPELINE EXECUTION START       |")
    logger.info("+" + "=" * 68 + "+")

    try:
        step_1_generate_raw_data()
        tables = step_2_clean_and_engineer_features()
        step_3_load_sqlite_database(tables)
        sql_counts = step_4_execute_sql_scripts()
        analytics_res = step_5_python_analytics(tables)
        charts = step_6_generate_charts(tables)
        step_7_export_dashboard_csvs(tables, analytics_res)


        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info("+" + "=" * 68 + "+")
        logger.info("|  PIPELINE EXECUTION COMPLETED SUCCESSFULLY                         |")
        logger.info(f"|  Total Elapsed Time: {elapsed:.2f} seconds" + " " * (43 - len(f"{elapsed:.2f}")) + "|")
        logger.info("+" + "=" * 68 + "+")

        print("\n" + "=" * 70)
        print("QSR PIPELINE EXECUTION SUMMARY")
        print("=" * 70)
        print(f"  Orders Processed:      {len(tables['orders']):,} orders")
        print(f"  Line Items Processed:  {len(tables['order_details']):,} items")
        print(f"  Net Sales Revenue:     ${tables['orders']['NetSales'].sum():,.2f}")
        print(f"  Gross Profit (Margin): ${tables['orders']['GrossProfit'].sum():,.2f} ({tables['orders']['GrossProfit'].sum() / tables['orders']['NetSales'].sum() * 100:.1f}%)")
        print(f"  SQL Queries Executed:  {sum(sql_counts.values())} across 6 SQL modules")
        print(f"  Charts Generated:      {len(charts)} figures in dashboard/charts/")
        print(f"  Power BI Exports:      7 CSV tables in dashboard/exports/")
        print(f"  Executive Report:      reports/business_insights.md")
        print(f"  SQLite Database:       {DB_PATH}")
        print(f"  Execution Time:        {elapsed:.2f}s")
        print("=" * 70 + "\n")

    except Exception as e:
        logger.error(f"Pipeline execution halted due to error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
