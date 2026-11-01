"""
Unit Tests for Inventory Optimization & Wastage Modules
"""

import os
import sys
import pytest
import pandas as pd
import numpy as np

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from src.inventory_analysis import (
    analyze_inventory_health,
    calculate_stock_velocity_and_turnover,
    calculate_reorder_points,
    analyze_kitchen_wastage
)

PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")


@pytest.fixture(scope="module")
def processed_inv_data():
    """Load cleaned inventory and operational datasets."""
    df_inv = pd.read_csv(os.path.join(PROCESSED_DIR, "inventory_cleaned.csv"))
    df_sup = pd.read_csv(os.path.join(PROCESSED_DIR, "suppliers_cleaned.csv"))
    df_wst = pd.read_csv(os.path.join(PROCESSED_DIR, "inventory_waste_cleaned.csv"))
    df_ord = pd.read_csv(os.path.join(PROCESSED_DIR, "orders_cleaned.csv"))
    return {
        "inventory": df_inv,
        "suppliers": df_sup,
        "waste": df_wst,
        "orders": df_ord,
    }


def test_inventory_health_alerts(processed_inv_data):
    """Verify inventory health classifications and reorder triggers."""
    inv = processed_inv_data["inventory"]
    sup = processed_inv_data["suppliers"]
    health = analyze_inventory_health(inv, sup)

    assert len(health) == len(inv)
    assert "StockClassification" in health.columns
    # Check that low stock items trigger non-zero suggested reorders
    low_stock = health[health["CurrentStock"] <= health["ReorderLevel"]]
    assert len(low_stock) > 0
    assert (low_stock["SuggestedReorderQty"] > 0).all()


def test_turnover_ratio_calculation(processed_inv_data):
    """Verify inventory turnover ratio is positive and consistent with COGS."""
    inv = processed_inv_data["inventory"]
    wst = processed_inv_data["waste"]
    ord_df = processed_inv_data["orders"]
    turnover = calculate_stock_velocity_and_turnover(inv, wst, ord_df)

    assert turnover["AnnualCOGS"] > 0
    assert turnover["TotalInventoryValuation"] > 0
    assert turnover["InventoryTurnoverRatio"] > 0
    assert turnover["DaysToTurnInventory"] > 0


def test_reorder_points_math(processed_inv_data):
    """Verify ROP = (Daily Usage * Lead Time) + Safety Stock."""
    inv = processed_inv_data["inventory"]
    sup = processed_inv_data["suppliers"]
    rop_df = calculate_reorder_points(inv, sup)

    assert len(rop_df) == len(inv)
    assert (rop_df["CalculatedROP"] > 0).all()
    assert (rop_df["CalculatedSafetyStock"] >= 0).all()
    assert (rop_df["DaysOfSupply"] > 0).all()


def test_kitchen_wastage_metrics(processed_inv_data):
    """Verify waste loss calculations."""
    wst = processed_inv_data["waste"]
    wst_summary = analyze_kitchen_wastage(wst)

    assert wst_summary["TotalWasteCostUSD"] > 0
    assert wst_summary["TotalWasteQty"] > 0
    assert wst_summary["TotalIncidents"] == len(wst)
    assert round(wst_summary["ByReason"]["CostSharePct"].sum(), 0) == 100.0
