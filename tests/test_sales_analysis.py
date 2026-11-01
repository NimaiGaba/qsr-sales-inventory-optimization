"""
Unit Tests for Sales & Product Analytics Modules
"""

import os
import sys
import pytest
import pandas as pd
import numpy as np

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from src.sales_analysis import calculate_sales_kpis, analyze_monthly_trends, analyze_location_performance
from src.product_analysis import get_top_and_bottom_products, compute_pareto_analysis
from src.time_analysis import analyze_hourly_distribution, analyze_weekday_vs_weekend

PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")


@pytest.fixture(scope="module")
def processed_sales_data():
    """Load cleaned transaction data for testing."""
    df_orders = pd.read_csv(os.path.join(PROCESSED_DIR, "orders_cleaned.csv"))
    df_details = pd.read_csv(os.path.join(PROCESSED_DIR, "order_details_cleaned.csv"))
    df_locations = pd.read_csv(os.path.join(PROCESSED_DIR, "locations_cleaned.csv"))
    return {
        "orders": df_orders,
        "details": df_details,
        "locations": df_locations,
    }


def test_sales_kpi_calculations(processed_sales_data):
    """Verify macro sales KPI math."""
    orders = processed_sales_data["orders"]
    details = processed_sales_data["details"]
    kpis = calculate_sales_kpis(orders, details)

    assert kpis["TotalOrders"] == len(orders)
    assert kpis["TotalItemsSold"] == int(details["Quantity"].sum())
    assert round(kpis["NetSales"], 1) == round(orders["NetSales"].sum(), 1)
    assert kpis["AverageOrderValue"] > 0
    assert kpis["ItemsPerOrder"] > 0


def test_monthly_trends(processed_sales_data):
    """Verify monthly aggregation covers all 12 calendar months."""
    orders = processed_sales_data["orders"]
    monthly = analyze_monthly_trends(orders)
    assert len(monthly) == 12
    assert (monthly["NetRevenue"] > 0).all()
    assert monthly["NetRevenue"].sum().round(1) == orders["NetSales"].sum().round(1)


def test_location_performance(processed_sales_data):
    """Verify location sales aggregate to 100% share."""
    orders = processed_sales_data["orders"]
    locations = processed_sales_data["locations"]
    loc_summary = analyze_location_performance(orders, locations)

    assert len(loc_summary) == 4
    assert round(loc_summary["RevenueSharePct"].sum(), 0) == 100.0


def test_pareto_analysis(processed_sales_data):
    """Verify Pareto 80/20 ranking segments."""
    details = processed_sales_data["details"]
    pareto = compute_pareto_analysis(details)

    assert len(pareto) > 0
    assert pareto["ProductRank"].tolist() == list(range(1, len(pareto) + 1))
    assert (pareto["CumulativeRevenuePct"] <= 100.0).all()
    # Check that segments exist
    segments = set(pareto["ParetoSegment"].unique())
    assert "Core Revenue Driver (Top 80%)" in segments


def test_time_analysis_hours_and_weekends(processed_sales_data):
    """Verify hourly rush and weekend sales comparisons."""
    orders = processed_sales_data["orders"]
    hourly = analyze_hourly_distribution(orders)
    assert len(hourly) > 0
    assert hourly["OrderCount"].sum() == len(orders)

    weekday_comp = analyze_weekday_vs_weekend(orders)
    assert len(weekday_comp) == 2
    # Weekends should have higher daily average revenue
    weekend_row = weekday_comp[weekday_comp["DayType"].str.contains("Weekend")].iloc[0]
    weekday_row = weekday_comp[weekday_comp["DayType"].str.contains("Weekday")].iloc[0]
    assert weekend_row["AvgRevenuePerDay"] > weekday_row["AvgRevenuePerDay"]
