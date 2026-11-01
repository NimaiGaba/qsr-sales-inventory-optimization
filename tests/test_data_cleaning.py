"""
Unit Tests for Data Cleaning & Feature Engineering Pipeline
"""

import os
import sys
import pytest
import pandas as pd
import numpy as np

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from src.data_cleaning import (
    clean_products,
    clean_locations,
    clean_inventory,
    clean_orders,
    clean_order_details,
    clean_waste_log,
    get_meal_period,
    run_data_cleaning_pipeline
)

RAW_DIR = os.path.join(PROJECT_ROOT, "data", "raw")


def test_meal_period_classification():
    """Verify hour to meal period mapping."""
    assert get_meal_period(8) == "Breakfast"
    assert get_meal_period(12) == "Lunch Rush"
    assert get_meal_period(16) == "Afternoon Snack"
    assert get_meal_period(19) == "Dinner Rush"
    assert get_meal_period(23) == "Late Night"


def test_clean_products():
    """Verify product cleaning, positive prices, and margins."""
    df_raw = pd.DataFrame([
        {"ProductID": "PRD-001", "ProductName": "Test Pizza", "Category": "Pizza", "Size": "Reg", "UnitPrice": 10.0, "UnitCost": 3.0},
        {"ProductID": "PRD-001", "ProductName": "Test Pizza", "Category": "Pizza", "Size": "Reg", "UnitPrice": 10.0, "UnitCost": 3.0}, # Dupe
        {"ProductID": "PRD-002", "ProductName": "Bad Item", "Category": "Sides", "Size": "Std", "UnitPrice": -5.0, "UnitCost": 2.0},  # Invalid
    ])
    df_clean = clean_products(df_raw)
    assert len(df_clean) == 1
    assert df_clean["GrossMarginDollar"].iloc[0] == 7.0
    assert df_clean["GrossMarginPct"].iloc[0] == 70.0


def test_clean_orders_revenue_integrity():
    """Verify NetSales = GrossSales - DiscountAmount."""
    df_raw = pd.DataFrame([
        {
            "OrderID": "ORD-001", "OrderDate": "2024-05-15", "OrderTime": "12:30:00",
            "LocationID": "LOC-01", "PaymentMethod": "Credit Card", "OrderType": "Dine-In",
            "ItemCount": 2, "GrossSales": 30.0, "DiscountAmount": 5.0, "NetSales": 20.0, # Intentional mismatch
            "TotalCost": 8.0, "GrossProfit": 17.0
        }
    ])
    df_clean = clean_orders(df_raw)
    assert len(df_clean) == 1
    # Check that NetSales is corrected to GrossSales - DiscountAmount (25.0)
    assert df_clean["NetSales"].iloc[0] == 25.0
    assert df_clean["OrderHour"].iloc[0] == 12
    assert df_clean["MealPeriod"].iloc[0] == "Lunch Rush"
    assert df_clean["DayName"].iloc[0] == "Wednesday"
    assert df_clean["IsWeekend"].iloc[0] == 0


def test_clean_inventory_status():
    """Verify inventory health classifications."""
    df_raw = pd.DataFrame([
        {"InventoryID": "INV-001", "ItemName": "Basil", "Category": "Produce", "CurrentStock": 5, "Unit": "kg", "ReorderLevel": 10, "SafetyStock": 3, "MaxStock": 30, "UnitCost": 10.0, "SupplierID": "SUP-01"},
        {"InventoryID": "INV-002", "ItemName": "Flour", "Category": "Dry Goods", "CurrentStock": 95, "Unit": "kg", "ReorderLevel": 20, "SafetyStock": 10, "MaxStock": 100, "UnitCost": 1.0, "SupplierID": "SUP-02"},
        {"InventoryID": "INV-003", "ItemName": "Cheese", "Category": "Dairy", "CurrentStock": 40, "Unit": "kg", "ReorderLevel": 20, "SafetyStock": 10, "MaxStock": 100, "UnitCost": 5.0, "SupplierID": "SUP-01"}
    ])
    df_clean = clean_inventory(df_raw)
    assert df_clean.loc[0, "StockStatus"] == "Low Stock (Reorder Alert)"
    assert df_clean.loc[1, "StockStatus"] == "Overstocked"
    assert df_clean.loc[2, "StockStatus"] == "Optimal Stock"
    assert df_clean.loc[0, "InventoryValuation"] == 50.0
