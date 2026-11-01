"""
QSR Sales Performance Analysis Module
=====================================
Analyzes macro sales KPIs, location performance, order types,
and promotional discount impacts using Pandas and NumPy.
"""

import logging
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


def calculate_sales_kpis(df_orders: pd.DataFrame, df_details: pd.DataFrame) -> dict:
    """Calculate core top-line sales KPIs."""
    total_orders = len(df_orders)
    total_items = int(df_details["Quantity"].sum())
    gross_sales = round(float(df_orders["GrossSales"].sum()), 2)
    discounts = round(float(df_orders["DiscountAmount"].sum()), 2)
    net_sales = round(float(df_orders["NetSales"].sum()), 2)
    aov = round(float(df_orders["NetSales"].mean()), 2)
    items_per_order = round(total_items / total_orders, 2) if total_orders > 0 else 0.0

    kpis = {
        "TotalOrders": total_orders,
        "TotalItemsSold": total_items,
        "GrossSales": gross_sales,
        "DiscountAmount": discounts,
        "NetSales": net_sales,
        "AverageOrderValue": aov,
        "ItemsPerOrder": items_per_order,
    }
    logger.info(f"Sales KPIs: Net Sales=${net_sales:,.2f} | Orders={total_orders:,} | AOV=${aov:.2f}")
    return kpis


def analyze_monthly_trends(df_orders: pd.DataFrame) -> pd.DataFrame:
    """Analyze monthly sales performance and MoM growth."""
    monthly = df_orders.groupby(["OrderYear", "OrderMonth", "OrderMonthName"]).agg(
        OrderCount=("OrderID", "count"),
        NetRevenue=("NetSales", "sum"),
        GrossRevenue=("GrossSales", "sum"),
        DiscountsGiven=("DiscountAmount", "sum"),
        AOV=("NetSales", "mean"),
    ).round(2).reset_index()

    monthly["PriorMonthRevenue"] = monthly["NetRevenue"].shift(1)
    monthly["MoMGrowthPct"] = (
        (monthly["NetRevenue"] - monthly["PriorMonthRevenue"]) / monthly["PriorMonthRevenue"] * 100
    ).round(2).fillna(0.0)

    logger.info(f"Monthly trends computed for {len(monthly)} months")
    return monthly


def analyze_location_performance(df_orders: pd.DataFrame, df_locations: pd.DataFrame) -> pd.DataFrame:
    """Analyze sales, AOV, and revenue share by restaurant location."""
    merged = df_orders.merge(df_locations, on="LocationID", how="left")
    loc_summary = merged.groupby(["LocationID", "LocationName", "District", "StoreType"]).agg(
        OrderCount=("OrderID", "count"),
        TotalRevenue=("NetSales", "sum"),
        AverageAOV=("NetSales", "mean"),
        GrossProfit=("GrossProfit", "sum"),
        SeatingCapacity=("SeatingCapacity", "first"),
    ).round(2).reset_index()

    loc_summary["RevenueSharePct"] = (
        loc_summary["TotalRevenue"] / loc_summary["TotalRevenue"].sum() * 100
    ).round(2)
    loc_summary["MarginPct"] = (
        loc_summary["GrossProfit"] / loc_summary["TotalRevenue"] * 100
    ).round(2)

    loc_summary = loc_summary.sort_values("TotalRevenue", ascending=False).reset_index(drop=True)
    logger.info(f"Location performance computed for {len(loc_summary)} locations")
    return loc_summary


def analyze_order_types_and_channels(df_orders: pd.DataFrame) -> pd.DataFrame:
    """Analyze sales distribution across order fulfillment channels."""
    channels = df_orders.groupby("OrderType").agg(
        OrderCount=("OrderID", "count"),
        TotalRevenue=("NetSales", "sum"),
        AverageAOV=("NetSales", "mean"),
        TotalDiscounts=("DiscountAmount", "sum"),
    ).round(2).reset_index()

    channels["OrderSharePct"] = (channels["OrderCount"] / channels["OrderCount"].sum() * 100).round(2)
    channels["RevenueSharePct"] = (channels["TotalRevenue"] / channels["TotalRevenue"].sum() * 100).round(2)
    channels = channels.sort_values("TotalRevenue", ascending=False).reset_index(drop=True)
    return channels


def analyze_payment_methods(df_orders: pd.DataFrame) -> pd.DataFrame:
    """Analyze payment method preferences and average basket sizes."""
    payments = df_orders.groupby("PaymentMethod").agg(
        OrderCount=("OrderID", "count"),
        TotalRevenue=("NetSales", "sum"),
        AverageAOV=("NetSales", "mean"),
    ).round(2).reset_index()

    payments["VolumeSharePct"] = (payments["OrderCount"] / payments["OrderCount"].sum() * 100).round(2)
    payments["RevenueSharePct"] = (payments["TotalRevenue"] / payments["TotalRevenue"].sum() * 100).round(2)
    payments = payments.sort_values("TotalRevenue", ascending=False).reset_index(drop=True)
    return payments


def run_sales_analysis(df_orders: pd.DataFrame, df_details: pd.DataFrame, df_locations: pd.DataFrame) -> dict:
    """Execute all sales analysis functions."""
    logger.info("Executing comprehensive sales performance analysis...")
    return {
        "kpis": calculate_sales_kpis(df_orders, df_details),
        "monthly": analyze_monthly_trends(df_orders),
        "locations": analyze_location_performance(df_orders, df_locations),
        "channels": analyze_order_types_and_channels(df_orders),
        "payments": analyze_payment_methods(df_orders),
    }
