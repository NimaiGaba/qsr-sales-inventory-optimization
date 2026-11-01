"""
QSR Time-Based Operational Analysis Module
==========================================
Analyzes peak dining hours, meal period day-parts, day-of-week demand,
and weekday versus weekend operational patterns.
"""

import logging
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


def analyze_hourly_distribution(df_orders: pd.DataFrame) -> pd.DataFrame:
    """Analyze order volume, revenue, and AOV by operating hour."""
    hourly = df_orders.groupby("OrderHour").agg(
        OrderCount=("OrderID", "count"),
        TotalRevenue=("NetSales", "sum"),
        AverageAOV=("NetSales", "mean"),
    ).round(2).reset_index()

    total_orders = hourly["OrderCount"].sum()
    total_rev = hourly["TotalRevenue"].sum()
    hourly["OrderSharePct"] = (hourly["OrderCount"] / total_orders * 100).round(2)
    hourly["RevenueSharePct"] = (hourly["TotalRevenue"] / total_rev * 100).round(2)

    # Classify operating period
    conditions = [
        hourly["OrderHour"].isin([12, 13]),
        hourly["OrderHour"].isin([18, 19]),
        hourly["OrderHour"].between(14, 16),
    ]
    choices = ["Lunch Peak Rush", "Dinner Peak Rush", "Afternoon Lull"]
    hourly["OperationalPeriod"] = np.select(conditions, choices, default="Normal Operating Flow")

    logger.info(f"Hourly analysis completed across {len(hourly)} hours")
    return hourly


def analyze_meal_periods(df_orders: pd.DataFrame) -> pd.DataFrame:
    """Analyze sales and profitability by meal period day-part."""
    periods = df_orders.groupby("MealPeriod").agg(
        OrderCount=("OrderID", "count"),
        TotalRevenue=("NetSales", "sum"),
        AverageAOV=("NetSales", "mean"),
        GrossProfit=("GrossProfit", "sum"),
    ).round(2).reset_index()

    total_orders = periods["OrderCount"].sum()
    total_rev = periods["TotalRevenue"].sum()
    periods["OrderSharePct"] = (periods["OrderCount"] / total_orders * 100).round(2)
    periods["RevenueSharePct"] = (periods["TotalRevenue"] / total_rev * 100).round(2)
    periods["MarginPct"] = (periods["GrossProfit"] / periods["TotalRevenue"] * 100).round(2)

    # Sort logically by time of day
    order_map = {"Breakfast": 1, "Lunch Rush": 2, "Afternoon Snack": 3, "Dinner Rush": 4, "Late Night": 5}
    periods["SortKey"] = periods["MealPeriod"].map(order_map).fillna(99)
    periods = periods.sort_values("SortKey").drop(columns=["SortKey"]).reset_index(drop=True)

    return periods


def analyze_day_of_week(df_orders: pd.DataFrame) -> pd.DataFrame:
    """Analyze sales trends from Monday through Sunday."""
    dow = df_orders.groupby(["DayOfWeek", "DayName"]).agg(
        OrderCount=("OrderID", "count"),
        TotalRevenue=("NetSales", "sum"),
        AverageAOV=("NetSales", "mean"),
        GrossProfit=("GrossProfit", "sum"),
    ).round(2).reset_index()

    total_orders = dow["OrderCount"].sum()
    total_rev = dow["TotalRevenue"].sum()
    dow["OrderSharePct"] = (dow["OrderCount"] / total_orders * 100).round(2)
    dow["RevenueSharePct"] = (dow["TotalRevenue"] / total_rev * 100).round(2)
    dow = dow.sort_values("DayOfWeek").reset_index(drop=True)

    return dow


def analyze_weekday_vs_weekend(df_orders: pd.DataFrame) -> pd.DataFrame:
    """Compare weekday (Mon-Thu) vs weekend (Fri-Sun) dynamics."""
    df = df_orders.copy()
    df["DayType"] = np.where(df["IsWeekend"] == 1, "Weekend (Fri-Sun)", "Weekday (Mon-Thu)")

    comparison = df.groupby("DayType").agg(
        TotalDays=("OrderDate", "nunique"),
        TotalOrders=("OrderID", "count"),
        TotalRevenue=("NetSales", "sum"),
        AverageAOV=("NetSales", "mean"),
        GrossProfit=("GrossProfit", "sum"),
    ).round(2).reset_index()

    comparison["AvgOrdersPerDay"] = (comparison["TotalOrders"] / comparison["TotalDays"]).round(1)
    comparison["AvgRevenuePerDay"] = (comparison["TotalRevenue"] / comparison["TotalDays"]).round(2)
    comparison["MarginPct"] = (comparison["GrossProfit"] / comparison["TotalRevenue"] * 100).round(2)

    return comparison


def run_time_analysis(df_orders: pd.DataFrame) -> dict:
    """Execute all time-based operational analyses."""
    logger.info("Executing time-based operational sales analysis...")
    return {
        "hourly": analyze_hourly_distribution(df_orders),
        "meal_periods": analyze_meal_periods(df_orders),
        "day_of_week": analyze_day_of_week(df_orders),
        "weekday_vs_weekend": analyze_weekday_vs_weekend(df_orders),
    }
