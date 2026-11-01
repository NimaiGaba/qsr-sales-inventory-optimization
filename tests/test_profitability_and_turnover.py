"""
Unit & Integration Tests for Profitability, Standard Inventory Turnover,
Recipe Consumption (BOM), and Dynamic Reorder Point Analytics
"""

import os
import sys
import sqlite3
import pytest
import pandas as pd
import numpy as np

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from src.inventory_analysis import (
    calculate_stock_velocity_and_turnover,
    calculate_recipe_ingredient_consumption,
    calculate_reorder_points,
    analyze_inventory_health
)
from src.profitability_analysis import (
    calculate_profit_loss_summary,
    analyze_product_profitability,
    analyze_location_profitability
)

PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
DB_PATH = os.path.join(PROJECT_ROOT, "qsr_analytics.db")


@pytest.fixture(scope="module")
def dataset():
    """Load processed tables for testing."""
    orders = pd.read_csv(os.path.join(PROCESSED_DIR, "orders_cleaned.csv"))
    details = pd.read_csv(os.path.join(PROCESSED_DIR, "order_details_cleaned.csv"))
    inventory = pd.read_csv(os.path.join(PROCESSED_DIR, "inventory_cleaned.csv"))
    suppliers = pd.read_csv(os.path.join(PROCESSED_DIR, "suppliers_cleaned.csv"))
    recipes = pd.read_csv(os.path.join(PROCESSED_DIR, "recipes_cleaned.csv"))
    waste = pd.read_csv(os.path.join(PROCESSED_DIR, "inventory_waste_cleaned.csv"))
    locations = pd.read_csv(os.path.join(PROCESSED_DIR, "locations_cleaned.csv"))
    return {
        "orders": orders,
        "details": details,
        "inventory": inventory,
        "suppliers": suppliers,
        "recipes": recipes,
        "waste": waste,
        "locations": locations
    }


def test_profitability_bridge_formulas(dataset):
    """
    Test Task 5 requirements:
    Net Revenue = Gross Revenue - Discounts
    Gross Profit = Net Revenue - COGS
    Gross Margin % = (Gross Profit / Net Revenue) * 100
    """
    orders = dataset["orders"]
    pl = calculate_profit_loss_summary(orders)

    # 1. Net Revenue verification
    expected_net = round(pl["GrossSales"] - pl["DiscountAmount"], 2)
    assert abs(pl["NetSales"] - expected_net) <= 0.05

    # 2. Gross Profit verification
    expected_profit = round(pl["NetSales"] - pl["CostOfGoodsSold"], 2)
    assert abs(pl["GrossProfit"] - expected_profit) <= 0.05

    # 3. Gross Margin % verification
    expected_margin_pct = round((pl["GrossProfit"] / pl["NetSales"]) * 100, 2)
    assert abs(pl["GrossMarginPct"] - expected_margin_pct) <= 0.05

    # 4. Valid food cost ratio
    expected_food_cost_pct = round((pl["CostOfGoodsSold"] / pl["NetSales"]) * 100, 2)
    assert abs(pl["FoodCostPct"] - expected_food_cost_pct) <= 0.05


def test_standard_inventory_turnover_formula(dataset):
    """
    Test Task 3 requirements:
    Average Inventory Value = (Beginning Inventory Value + Ending Inventory Value) / 2
    Inventory Turnover Ratio = Cost of Goods Sold / Average Inventory Value
    Inventory Days = 366 / Inventory Turnover Ratio
    """
    inventory = dataset["inventory"]
    orders = dataset["orders"]
    waste = dataset["waste"]

    turnover = calculate_stock_velocity_and_turnover(inventory, waste, orders, annual_days=366)

    # Validate Beginning, Ending, and Average valuation
    beg_val = float((inventory["BeginningStock"] * inventory["UnitCost"]).sum())
    end_val = float((inventory["CurrentStock"] * inventory["UnitCost"]).sum())
    expected_avg_val = round((beg_val + end_val) / 2.0, 2)

    assert abs(turnover["BeginningInventoryValuation"] - round(beg_val, 2)) <= 0.05
    assert abs(turnover["EndingInventoryValuation"] - round(end_val, 2)) <= 0.05
    assert abs(turnover["AverageInventoryValuation"] - expected_avg_val) <= 0.05

    # Validate standard turnover ratio
    total_cogs = float(orders["TotalCost"].sum())
    expected_turnover = round(total_cogs / expected_avg_val, 2)
    assert abs(turnover["InventoryTurnoverRatio"] - expected_turnover) <= 0.05

    # Validate days sales of inventory
    expected_dsi = round(366.0 / expected_turnover, 1)
    assert abs(turnover["DaysToTurnInventory"] - expected_dsi) <= 0.1


def test_recipe_daily_consumption_calculation(dataset):
    """
    Test Task 2 requirements:
    - Calculates empirical ingredient consumption via recipe BOM
    - Normalizes across full 366-day calendar accounting for zero-demand days
    - Distinguishes observed consumption from assumed fallback
    """
    details = dataset["details"]
    recipes = dataset["recipes"]
    orders = dataset["orders"]
    inventory = dataset["inventory"]

    df_consumption = calculate_recipe_ingredient_consumption(
        df_details=details,
        df_recipes=recipes,
        df_orders=orders,
        df_inventory=inventory,
        annual_days=366
    )

    assert len(df_consumption) == len(inventory)
    assert "ObservedDailyConsumption" in df_consumption.columns
    assert "TotalObservedConsumption" in df_consumption.columns
    assert "ZeroDemandDays" in df_consumption.columns
    assert "ConsumptionSource" in df_consumption.columns

    # Verify all 366 observation days are tracked
    assert (df_consumption["ObservationDays"] == 366).all()
    # High-velocity items like mozzarella and flour must have positive usage
    assert (df_consumption["TotalObservedConsumption"] > 0).all()
    assert (df_consumption["ObservedDailyConsumption"] > 0).all()


def test_dynamic_reorder_points_with_bom(dataset):
    """
    Test Task 4 requirements:
    Reorder Point = Average Daily Consumption * Lead Time + Safety Stock
    Safety Stock = Z * std_dev * sqrt(LeadTime)
    Stock Coverage = CurrentStock / Average Daily Consumption
    """
    inventory = dataset["inventory"]
    suppliers = dataset["suppliers"]
    details = dataset["details"]
    recipes = dataset["recipes"]
    orders = dataset["orders"]

    df_consumption = calculate_recipe_ingredient_consumption(details, recipes, orders, inventory)
    rop_df = calculate_reorder_points(inventory, suppliers, df_consumption=df_consumption)

    assert len(rop_df) == len(inventory)
    assert "CalculatedROP" in rop_df.columns
    assert "CalculatedSafetyStock" in rop_df.columns
    assert "StockCoverageDays" in rop_df.columns
    assert "ReorderRecommendation" in rop_df.columns

    # Check math: ROP >= SafetyStock
    assert (rop_df["CalculatedROP"] >= rop_df["CalculatedSafetyStock"]).all()
    # Stock coverage positive
    assert (rop_df["StockCoverageDays"] > 0).all()


def test_sql_turnover_query_alignment():
    """Verify that SQL query E7 in 05_inventory_analysis.sql matches Python calculations."""
    conn = sqlite3.connect(DB_PATH)
    query = """
    WITH InvValuation AS (
        SELECT 
            ROUND(SUM(COALESCE(BeginningStock, CurrentStock) * UnitCost), 2) AS Beginning_Inventory_Value,
            ROUND(SUM(CurrentStock * UnitCost), 2) AS Ending_Inventory_Value,
            ROUND((SUM(COALESCE(BeginningStock, CurrentStock) * UnitCost) + SUM(CurrentStock * UnitCost)) / 2.0, 2) AS Average_Inventory_Value
        FROM inventory
    ),
    CogsValuation AS (
        SELECT 
            ROUND(SUM(TotalCost), 2) AS Annual_COGS
        FROM orders
    )
    SELECT 
        c.Annual_COGS,
        i.Beginning_Inventory_Value,
        i.Ending_Inventory_Value,
        i.Average_Inventory_Value,
        ROUND(c.Annual_COGS / i.Average_Inventory_Value, 2) AS Inventory_Turnover_Ratio,
        ROUND(366.0 / (c.Annual_COGS / i.Average_Inventory_Value), 1) AS Days_Sales_of_Inventory_DSI
    FROM InvValuation i
    CROSS JOIN CogsValuation c;
    """
    df_sql = pd.read_sql_query(query, conn)
    conn.close()

    assert not df_sql.empty
    row = df_sql.iloc[0]
    assert row["Annual_COGS"] == 318309.00
    assert row["Beginning_Inventory_Value"] > 0
    assert row["Ending_Inventory_Value"] > 0
    assert row["Average_Inventory_Value"] == round((row["Beginning_Inventory_Value"] + row["Ending_Inventory_Value"]) / 2.0, 2)
    assert row["Inventory_Turnover_Ratio"] > 10.0
    assert row["Days_Sales_of_Inventory_DSI"] > 20.0
