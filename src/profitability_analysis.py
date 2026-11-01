"""
QSR Profitability & Margin Optimization Module
==============================================
Calculates product, category, and location gross profit margins,
food cost percentages (COGS), and discount erosion impacts.
"""

import logging
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


def calculate_profit_loss_summary(df_orders: pd.DataFrame) -> dict:
    """Calculate overall P&L bridge metrics."""
    gross = round(float(df_orders["GrossSales"].sum()), 2)
    discounts = round(float(df_orders["DiscountAmount"].sum()), 2)
    net = round(float(df_orders["NetSales"].sum()), 2)
    cogs = round(float(df_orders["TotalCost"].sum()), 2)
    profit = round(float(df_orders["GrossProfit"].sum()), 2)
    
    margin_pct = round((profit / net * 100), 2) if net > 0 else 0.0
    food_cost_pct = round((cogs / net * 100), 2) if net > 0 else 0.0
    discount_rate = round((discounts / gross * 100), 2) if gross > 0 else 0.0

    pl = {
        "GrossSales": gross,
        "DiscountAmount": discounts,
        "NetSales": net,
        "CostOfGoodsSold": cogs,
        "GrossProfit": profit,
        "GrossMarginPct": margin_pct,
        "FoodCostPct": food_cost_pct,
        "EffectiveDiscountRate": discount_rate,
    }
    logger.info(f"P&L: Net=${net:,.2f} | COGS=${cogs:,.2f} | Profit=${profit:,.2f} ({margin_pct}% margin)")
    return pl


def analyze_product_profitability(df_details: pd.DataFrame) -> pd.DataFrame:
    """Analyze margin percentage and total profit contribution per product."""
    prod_prof = df_details.groupby(["ProductID", "ProductName", "Category"]).agg(
        UnitsSold=("Quantity", "sum"),
        Revenue=("TotalPrice", "sum"),
        COGS=("LineCost", "sum"),
        GrossProfit=("LineProfit", "sum"),
    ).round(2).reset_index()

    total_profit = prod_prof["GrossProfit"].sum()
    prod_prof["MarginPct"] = ((prod_prof["GrossProfit"] / prod_prof["Revenue"]) * 100).round(1)
    prod_prof["ProfitContributionPct"] = ((prod_prof["GrossProfit"] / total_profit) * 100).round(2)
    prod_prof = prod_prof.sort_values("GrossProfit", ascending=False).reset_index(drop=True)
    return prod_prof


def analyze_location_profitability(df_orders: pd.DataFrame, df_locations: pd.DataFrame) -> pd.DataFrame:
    """Compare profitability across restaurant store locations."""
    merged = df_orders.merge(df_locations, on="LocationID", how="left")
    loc_prof = merged.groupby(["LocationID", "LocationName", "StoreType"]).agg(
        OrderCount=("OrderID", "count"),
        NetRevenue=("NetSales", "sum"),
        COGS=("TotalCost", "sum"),
        GrossProfit=("GrossProfit", "sum"),
    ).round(2).reset_index()

    loc_prof["MarginPct"] = ((loc_prof["GrossProfit"] / loc_prof["NetRevenue"]) * 100).round(2)
    loc_prof["ProfitPerOrder"] = (loc_prof["GrossProfit"] / loc_prof["OrderCount"]).round(2)
    loc_prof = loc_prof.sort_values("GrossProfit", ascending=False).reset_index(drop=True)
    return loc_prof


def run_profitability_analysis(
    df_orders: pd.DataFrame,
    df_details: pd.DataFrame,
    df_locations: pd.DataFrame
) -> dict:
    """Execute all profitability analyses."""
    logger.info("Executing profitability & margin optimization analysis...")
    return {
        "pl_summary": calculate_profit_loss_summary(df_orders),
        "products": analyze_product_profitability(df_details),
        "locations": analyze_location_profitability(df_orders, df_locations),
    }
