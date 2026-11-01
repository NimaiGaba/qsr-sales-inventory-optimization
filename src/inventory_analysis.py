"""
QSR Inventory Optimization & Supply Chain Analysis Module
=========================================================
Rule-based inventory management and stock optimization using Python.
Calculates stock velocity, turnover ratios, consumption rates,
dynamic reorder points (ROP), safety stock, and kitchen wastage impact.

Methodology:
- Average Daily Consumption (ADC) = Total Annual Usage / 365 Days
- Safety Stock = Z * std_dev(daily_demand) * sqrt(LeadTimeDays)
- Reorder Point (ROP) = (ADC * LeadTimeDays) + SafetyStock
- Inventory Turnover = Annual COGS / Average Inventory Valuation
- Days of Supply (DOS) = CurrentStock / ADC
"""

import logging
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

SERVICE_LEVEL_Z_95 = 1.65  # 95% service level z-score


def analyze_inventory_health(df_inventory: pd.DataFrame, df_suppliers: pd.DataFrame) -> pd.DataFrame:
    """Analyze current stock against reorder thresholds and safety stock."""
    df = df_inventory.merge(df_suppliers, on="SupplierID", how="left")
    
    # Calculate stock ratios and replenishment urgency
    df["StockToReorderRatio"] = (df["CurrentStock"] / df["ReorderLevel"]).round(2)
    df["ValuationUSD"] = (df["CurrentStock"] * df["UnitCost"]).round(2)
    
    # Classification: Low Stock, Optimal, Overstocked
    conditions = [
        df["CurrentStock"] <= df["ReorderLevel"],
        df["CurrentStock"] >= (df["MaxStock"] * 0.90),
    ]
    labels = ["Low Stock (Reorder Needed)", "Overstocked (Excess Capital)"]
    df["StockClassification"] = np.select(conditions, labels, default="Healthy / Optimal")
    
    # Recommended Reorder Quantity to bring back to MaxStock
    df["SuggestedReorderQty"] = np.where(
        df["CurrentStock"] <= df["ReorderLevel"],
        df["MaxStock"] - df["CurrentStock"],
        0
    )
    df["SuggestedReorderCostUSD"] = (df["SuggestedReorderQty"] * df["UnitCost"]).round(2)

    logger.info(f"Inventory health assessed for {len(df)} SKUs")
    return df


def calculate_stock_velocity_and_turnover(
    df_inventory: pd.DataFrame,
    df_waste: pd.DataFrame,
    df_orders: pd.DataFrame,
    annual_days: int = 366
) -> dict:
    """
    Calculate inventory velocity, annual turnover ratio,
    and days of supply.
    """
    total_cogs = float(df_orders["TotalCost"].sum())
    total_inv_val = float((df_inventory["CurrentStock"] * df_inventory["UnitCost"]).sum())
    
    # Chain-level inventory turnover = Annual COGS / Current Inventory Value
    turnover_ratio = round(total_cogs / total_inv_val, 2) if total_inv_val > 0 else 0.0
    days_to_turn = round(annual_days / turnover_ratio, 1) if turnover_ratio > 0 else 0.0

    # Category turnover estimates
    category_summary = df_inventory.groupby("Category").agg(
        SKUCount=("InventoryID", "count"),
        TotalStockValue=("CurrentStock", lambda x: (x * df_inventory.loc[x.index, "UnitCost"]).sum()),
    ).round(2).reset_index()

    category_summary["ValuationSharePct"] = (
        category_summary["TotalStockValue"] / category_summary["TotalStockValue"].sum() * 100
    ).round(2)

    metrics = {
        "AnnualCOGS": round(total_cogs, 2),
        "TotalInventoryValuation": round(total_inv_val, 2),
        "InventoryTurnoverRatio": turnover_ratio,
        "DaysToTurnInventory": days_to_turn,
        "CategorySummary": category_summary,
    }
    logger.info(f"Inventory Turnover: {turnover_ratio}x per year (Days to turn: {days_to_turn} days)")
    return metrics


def calculate_reorder_points(df_inventory: pd.DataFrame, df_suppliers: pd.DataFrame) -> pd.DataFrame:
    """
    Compute dynamic Reorder Points (ROP) and Safety Stock.
    ROP = (Average Daily Consumption * Lead Time) + Safety Stock
    """
    df = df_inventory.merge(df_suppliers, on="SupplierID", how="left")
    
    # Daily consumption benchmark based on turnover
    # Fast-moving ingredients (flour, cheese, dough, sauce) turn every 7-14 days
    df["DailyConsumptionEst"] = (df["MaxStock"] / 20.0).round(2)
    # Demand standard deviation (~18% demand variability)
    df["DailyDemandStdDev"] = (df["DailyConsumptionEst"] * 0.18).round(2)

    # Safety Stock = Z * std_dev * sqrt(LeadTime)
    df["CalculatedSafetyStock"] = (
        SERVICE_LEVEL_Z_95 * df["DailyDemandStdDev"] * np.sqrt(df["LeadTimeDays"])
    ).round(1)

    # Dynamic ROP = (Daily Consumption * Lead Time) + Safety Stock
    df["CalculatedROP"] = (
        (df["DailyConsumptionEst"] * df["LeadTimeDays"]) + df["CalculatedSafetyStock"]
    ).round(1)

    df["DaysOfSupply"] = (df["CurrentStock"] / df["DailyConsumptionEst"]).round(1)

    # Classify velocity
    conditions = [
        df["DaysOfSupply"] <= 7.0,
        df["DaysOfSupply"] <= 21.0,
    ]
    labels = ["Fast Moving (High Velocity)", "Moderate Moving"]
    df["VelocityClassification"] = np.select(conditions, labels, default="Slow Moving (Long Cycle)")

    return df


def analyze_kitchen_wastage(df_waste: pd.DataFrame) -> dict:
    """Analyze kitchen wastage volume, cost, and root causes."""
    total_waste_cost = round(float(df_waste["WasteCost"].sum()), 2)
    total_waste_qty = round(float(df_waste["QuantityWasted"].sum()), 1)
    total_incidents = len(df_waste)

    by_reason = df_waste.groupby("Reason").agg(
        IncidentCount=("WasteID", "count"),
        QuantityLost=("QuantityWasted", "sum"),
        CostLostUSD=("WasteCost", "sum"),
    ).round(2).reset_index()
    by_reason["CostSharePct"] = (by_reason["CostLostUSD"] / total_waste_cost * 100).round(2)
    by_reason = by_reason.sort_values("CostLostUSD", ascending=False).reset_index(drop=True)

    by_category = df_waste.groupby("Category").agg(
        IncidentCount=("WasteID", "count"),
        QuantityLost=("QuantityWasted", "sum"),
        CostLostUSD=("WasteCost", "sum"),
    ).round(2).reset_index()
    by_category["CostSharePct"] = (by_category["CostLostUSD"] / total_waste_cost * 100).round(2)
    by_category = by_category.sort_values("CostLostUSD", ascending=False).reset_index(drop=True)

    top_wasted_items = df_waste.groupby(["InventoryID", "ItemName", "Category", "Unit"]).agg(
        Incidents=("WasteID", "count"),
        QuantityLost=("QuantityWasted", "sum"),
        CostLostUSD=("WasteCost", "sum"),
    ).round(2).reset_index().sort_values("CostLostUSD", ascending=False).head(8).reset_index(drop=True)

    return {
        "TotalWasteCostUSD": total_waste_cost,
        "TotalWasteQty": total_waste_qty,
        "TotalIncidents": total_incidents,
        "ByReason": by_reason,
        "ByCategory": by_category,
        "TopWastedItems": top_wasted_items,
    }


def run_inventory_analysis(
    df_inventory: pd.DataFrame,
    df_suppliers: pd.DataFrame,
    df_waste: pd.DataFrame,
    df_orders: pd.DataFrame
) -> dict:
    """Execute all inventory and supply chain optimization analyses."""
    logger.info("Executing inventory optimization analysis...")
    return {
        "health": analyze_inventory_health(df_inventory, df_suppliers),
        "turnover": calculate_stock_velocity_and_turnover(df_inventory, df_waste, df_orders),
        "reorder_points": calculate_reorder_points(df_inventory, df_suppliers),
        "wastage": analyze_kitchen_wastage(df_waste),
    }
