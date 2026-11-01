"""
QSR Product Performance & Pareto Analysis Module
================================================
Analyzes menu item velocity, revenue generation, category contributions,
and 80/20 Pareto revenue concentration.
"""

import logging
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


def get_top_and_bottom_products(df_details: pd.DataFrame, n: int = 10) -> dict:
    """Identify top best-sellers and bottom underperforming menu items."""
    product_totals = df_details.groupby(["ProductID", "ProductName", "Category"]).agg(
        UnitsSold=("Quantity", "sum"),
        RevenueGenerated=("TotalPrice", "sum"),
        GrossProfitContributed=("LineProfit", "sum"),
        AvgPriceRealized=("UnitPrice", "mean"),
    ).round(2).reset_index()

    total_revenue = product_totals["RevenueGenerated"].sum()
    product_totals["RevenueSharePct"] = (product_totals["RevenueGenerated"] / total_revenue * 100).round(2)
    product_totals["MarginPct"] = (
        product_totals["GrossProfitContributed"] / product_totals["RevenueGenerated"] * 100
    ).round(1)

    top_by_revenue = product_totals.sort_values("RevenueGenerated", ascending=False).head(n).reset_index(drop=True)
    top_by_units = product_totals.sort_values("UnitsSold", ascending=False).head(n).reset_index(drop=True)
    bottom_performers = product_totals.sort_values("RevenueGenerated", ascending=True).head(5).reset_index(drop=True)

    return {
        "all_products": product_totals,
        "top_by_revenue": top_by_revenue,
        "top_by_units": top_by_units,
        "bottom_performers": bottom_performers,
    }


def analyze_category_performance(df_details: pd.DataFrame) -> pd.DataFrame:
    """Analyze sales, unit volumes, and margins by product category."""
    cat_summary = df_details.groupby("Category").agg(
        ItemCount=("ProductID", "nunique"),
        TotalUnitsSold=("Quantity", "sum"),
        TotalRevenue=("TotalPrice", "sum"),
        TotalCOGS=("LineCost", "sum"),
        TotalGrossProfit=("LineProfit", "sum"),
    ).round(2).reset_index()

    total_rev = cat_summary["TotalRevenue"].sum()
    cat_summary["RevenueSharePct"] = (cat_summary["TotalRevenue"] / total_rev * 100).round(2)
    cat_summary["MarginPct"] = (cat_summary["TotalGrossProfit"] / cat_summary["TotalRevenue"] * 100).round(2)
    cat_summary = cat_summary.sort_values("TotalRevenue", ascending=False).reset_index(drop=True)

    logger.info(f"Category performance analyzed across {len(cat_summary)} categories")
    return cat_summary


def compute_pareto_analysis(df_details: pd.DataFrame) -> pd.DataFrame:
    """Perform Pareto 80/20 analysis on product revenue concentration."""
    p_agg = df_details.groupby(["ProductID", "ProductName", "Category"]).agg(
        Revenue=("TotalPrice", "sum"),
        Units=("Quantity", "sum"),
    ).reset_index()

    p_agg = p_agg.sort_values("Revenue", ascending=False).reset_index(drop=True)
    total_rev = p_agg["Revenue"].sum()
    p_agg["CumulativeRevenue"] = p_agg["Revenue"].cumsum()
    p_agg["CumulativeRevenuePct"] = (p_agg["CumulativeRevenue"] / total_rev * 100).round(2)
    p_agg["ProductRank"] = range(1, len(p_agg) + 1)
    p_agg["ProductPercentile"] = (p_agg["ProductRank"] / len(p_agg) * 100).round(1)

    p_agg["ParetoSegment"] = np.where(
        p_agg["CumulativeRevenuePct"] <= 80.0,
        "Core Revenue Driver (Top 80%)",
        "Long-Tail Product (Bottom 20%)"
    )

    core_count = sum(p_agg["ParetoSegment"] == "Core Revenue Driver (Top 80%)")
    logger.info(f"Pareto analysis: {core_count} out of {len(p_agg)} SKUs drive 80% of total revenue")
    return p_agg


def run_product_analysis(df_details: pd.DataFrame) -> dict:
    """Execute all product performance analysis functions."""
    logger.info("Executing product performance & Pareto analysis...")
    p_dict = get_top_and_bottom_products(df_details)
    return {
        "summary": p_dict["all_products"],
        "top_by_revenue": p_dict["top_by_revenue"],
        "top_by_units": p_dict["top_by_units"],
        "bottom_performers": p_dict["bottom_performers"],
        "categories": analyze_category_performance(df_details),
        "pareto": compute_pareto_analysis(df_details),
    }
