"""
QSR Inventory Optimization & Supply Chain Analysis Module
=========================================================
Rule-based inventory management, Bill of Materials (BOM) consumption tracking,
and stock optimization using Python.

Methodology & Standards:
1. Historical Ingredient Consumption (BOM):
   - Merges customer order item quantities with standardized recipe ingredient weights/units.
   - Computes daily ingredient demand across the full 366-day observation window (2024-01-01 to 2024-12-31).
   - Accurately captures zero-demand days (fill zero) to prevent upward skew of average consumption.
   - Distinguishes observed recipe-derived consumption from synthetic fallback estimates.

2. Standard Inventory Turnover Ratio:
   - Beginning Inventory Valuation = Sum(BeginningStock * UnitCost)
   - Ending Inventory Valuation = Sum(CurrentStock * UnitCost)
   - Average Inventory Value = (Beginning Inventory Valuation + Ending Inventory Valuation) / 2
   - Inventory Turnover Ratio = Annual Cost of Goods Sold (COGS) / Average Inventory Value
   - Days Sales of Inventory (DSI / Inventory Days) = 366 / Inventory Turnover Ratio

3. Dynamic Reorder Point (ROP) & Safety Stock:
   - ROP = (Average Daily Consumption * LeadTimeDays) + SafetyStock
   - Safety Stock = Z (1.65 for 95% service level) * StdDev(DailyDemand) * sqrt(LeadTimeDays)
   - Stock Coverage (Days of Supply) = CurrentStock / Average Daily Consumption
   - Categorization: Fast-Moving, Moderate-Moving, Slow-Moving SKUs.
"""

import logging
from typing import Optional, Dict, Any
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

SERVICE_LEVEL_Z_95 = 1.65  # 95% cycle-service level (one-tailed z-score)
OBSERVATION_DAYS_2024 = 366  # 2024 is a leap year (366 calendar days)


def calculate_recipe_ingredient_consumption(
    df_details: pd.DataFrame,
    df_recipes: pd.DataFrame,
    df_orders: pd.DataFrame,
    df_inventory: pd.DataFrame,
    annual_days: int = OBSERVATION_DAYS_2024
) -> pd.DataFrame:
    """
    Calculate empirical ingredient consumption from historical sales transactions
    multiplied by recipe Bill of Materials (BOM) quantities.
    
    Explicitly accounts for zero-demand days by reindexing each SKU across
    the complete 366-day calendar.
    """
    if df_recipes.empty or df_details.empty:
        logger.warning("Recipe BOM or Order Details empty. Falling back to synthetic estimates.")
        return pd.DataFrame()

    # Determine recipe quantity column name
    qty_col = "QuantityPerUnit" if "QuantityPerUnit" in df_recipes.columns else "QuantityRequired"

    # Merge line items with recipe definitions
    merged_items = df_details[["OrderID", "ProductID", "Quantity"]].merge(
        df_recipes[["ProductID", "InventoryID", qty_col, "Unit"]],
        on="ProductID",
        how="inner"
    )
    merged_items["IngredientUsage"] = merged_items["Quantity"] * merged_items[qty_col]

    # Merge with orders to extract date
    df_orders_dates = df_orders[["OrderID", "OrderDate"]].copy()
    df_orders_dates["OrderDate"] = pd.to_datetime(df_orders_dates["OrderDate"]).dt.date
    merged_items = merged_items.merge(df_orders_dates, on="OrderID", how="inner")

    # Full date range for calendar normalization
    min_date = merged_items["OrderDate"].min()
    max_date = merged_items["OrderDate"].max()
    all_dates = pd.date_range(start=min_date, end=max_date, freq="D").date
    total_calendar_days = len(all_dates)

    # Group daily consumption per inventory item
    daily_usage = merged_items.groupby(["InventoryID", "OrderDate"])["IngredientUsage"].sum().reset_index()

    consumption_records = []
    for inv_id in df_inventory["InventoryID"].unique():
        item_daily = daily_usage[daily_usage["InventoryID"] == inv_id].set_index("OrderDate")
        # Reindex across all calendar days, filling 0 for days without orders
        full_series = item_daily["IngredientUsage"].reindex(all_dates, fill_value=0.0)

        total_consumed = float(full_series.sum())
        mean_daily = float(full_series.mean())
        std_daily = float(full_series.std(ddof=1)) if len(full_series) > 1 else 0.0
        peak_daily = float(full_series.max())
        zero_days = int((full_series == 0).sum())

        consumption_records.append({
            "InventoryID": inv_id,
            "TotalObservedConsumption": round(total_consumed, 2),
            "ObservedDailyConsumption": round(mean_daily, 3),
            "DailyDemandStdDev": round(std_daily, 3),
            "PeakDailyDemand": round(peak_daily, 2),
            "ObservationDays": total_calendar_days,
            "ZeroDemandDays": zero_days,
            "ConsumptionSource": "Observed (Recipe BOM Historical Sales)"
        })

    df_consumption = pd.DataFrame(consumption_records)
    logger.info(f"Calculated recipe-level consumption for {len(df_consumption)} inventory items across {total_calendar_days} days")
    return df_consumption


def analyze_inventory_health(df_inventory: pd.DataFrame, df_suppliers: pd.DataFrame) -> pd.DataFrame:
    """Analyze current stock against reorder thresholds, safety stock, and par levels."""
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
    annual_days: int = OBSERVATION_DAYS_2024
) -> dict:
    """
    Calculate standard inventory turnover ratio and days sales of inventory.
    
    Standard Formula:
    Inventory Turnover Ratio = Cost of Goods Sold (COGS) / Average Inventory Value
    Average Inventory Value = (Beginning Inventory Value + Ending Inventory Value) / 2
    Days to Turn Inventory = Annual Days / Inventory Turnover Ratio
    """
    total_cogs = float(df_orders["TotalCost"].sum())
    
    # Calculate beginning and ending inventory valuation
    if "BeginningStock" in df_inventory.columns:
        beg_val = float((df_inventory["BeginningStock"] * df_inventory["UnitCost"]).sum())
    else:
        beg_val = float((df_inventory["CurrentStock"] * df_inventory["UnitCost"]).sum())
        
    end_val = float((df_inventory["CurrentStock"] * df_inventory["UnitCost"]).sum())
    avg_inv_val = (beg_val + end_val) / 2.0
    
    turnover_ratio = round(total_cogs / avg_inv_val, 2) if avg_inv_val > 0 else 0.0
    days_to_turn = round(annual_days / turnover_ratio, 1) if turnover_ratio > 0 else 0.0

    # Category turnover estimates
    category_summary = df_inventory.groupby("Category").agg(
        SKUCount=("InventoryID", "count"),
        BeginningStockValue=("BeginningStock", lambda x: (x * df_inventory.loc[x.index, "UnitCost"]).sum()) if "BeginningStock" in df_inventory.columns else ("CurrentStock", lambda x: (x * df_inventory.loc[x.index, "UnitCost"]).sum()),
        EndingStockValue=("CurrentStock", lambda x: (x * df_inventory.loc[x.index, "UnitCost"]).sum()),
    ).round(2).reset_index()

    category_summary["AverageStockValue"] = (
        (category_summary["BeginningStockValue"] + category_summary["EndingStockValue"]) / 2.0
    ).round(2)
    category_summary["ValuationSharePct"] = (
        category_summary["EndingStockValue"] / category_summary["EndingStockValue"].sum() * 100
    ).round(2)

    metrics = {
        "AnnualCOGS": round(total_cogs, 2),
        "BeginningInventoryValuation": round(beg_val, 2),
        "EndingInventoryValuation": round(end_val, 2),
        "TotalInventoryValuation": round(end_val, 2),  # Kept for backward compatibility
        "AverageInventoryValuation": round(avg_inv_val, 2),
        "InventoryTurnoverRatio": turnover_ratio,
        "DaysToTurnInventory": days_to_turn,
        "AnnualDays": annual_days,
        "CategorySummary": category_summary,
    }
    logger.info(
        f"Standard Inventory Turnover: {turnover_ratio}x (COGS: ${total_cogs:,.2f}, "
        f"Avg Inv: ${avg_inv_val:,.2f}, Days to Turn: {days_to_turn} days)"
    )
    return metrics


def calculate_reorder_points(
    df_inventory: pd.DataFrame,
    df_suppliers: pd.DataFrame,
    df_consumption: Optional[pd.DataFrame] = None
) -> pd.DataFrame:
    """
    Compute dynamic Reorder Points (ROP), Safety Stock, and Stock Coverage.
    Formula:
    ROP = (Average Daily Consumption * LeadTimeDays) + Safety Stock
    Safety Stock = Z (1.65) * StdDev(Daily Demand) * sqrt(LeadTimeDays)
    Stock Coverage (Days of Supply) = CurrentStock / Average Daily Consumption
    """
    df = df_inventory.merge(df_suppliers, on="SupplierID", how="left")
    
    if df_consumption is not None and not df_consumption.empty:
        # Use empirically derived recipe consumption metrics
        df = df.merge(
            df_consumption[[
                "InventoryID", "TotalObservedConsumption", "ObservedDailyConsumption",
                "DailyDemandStdDev", "PeakDailyDemand", "ObservationDays", "ZeroDemandDays",
                "ConsumptionSource"
            ]],
            on="InventoryID",
            how="left"
        )
        df["AverageDailyConsumption"] = df["ObservedDailyConsumption"].fillna(df["MaxStock"] / 20.0).round(2)
        df["DemandStdDev"] = df["DailyDemandStdDev"].fillna(df["AverageDailyConsumption"] * 0.18).round(2)
    else:
        # Documented synthetic fallback when historical recipe consumption is not provided
        df["ConsumptionSource"] = "Assumed Approximation (MaxStock / 20)"
        df["AverageDailyConsumption"] = (df["MaxStock"] / 20.0).round(2)
        df["DemandStdDev"] = (df["AverageDailyConsumption"] * 0.18).round(2)
        df["ObservationDays"] = OBSERVATION_DAYS_2024
        df["ZeroDemandDays"] = 0

    # Safety Stock = Z * std_dev * sqrt(LeadTime)
    df["CalculatedSafetyStock"] = (
        SERVICE_LEVEL_Z_95 * df["DemandStdDev"] * np.sqrt(df["LeadTimeDays"])
    ).round(1)

    # Dynamic ROP = (Average Daily Consumption * Lead Time) + Safety Stock
    df["CalculatedROP"] = (
        (df["AverageDailyConsumption"] * df["LeadTimeDays"]) + df["CalculatedSafetyStock"]
    ).round(1)

    # Stock coverage in days (handling division by zero)
    df["StockCoverageDays"] = np.where(
        df["AverageDailyConsumption"] > 0,
        (df["CurrentStock"] / df["AverageDailyConsumption"]).round(1),
        999.0
    )
    # Kept for backward compatibility with existing tests
    df["DaysOfSupply"] = df["StockCoverageDays"]

    # Classify velocity based on stock coverage
    conditions = [
        df["StockCoverageDays"] <= 10.0,
        df["StockCoverageDays"] <= 25.0,
    ]
    labels = ["Fast Moving (High Velocity)", "Moderate Moving"]
    df["VelocityClassification"] = np.select(conditions, labels, default="Slow Moving (Long Cycle)")

    # Reorder Action Recommendation
    reorder_conditions = [
        df["CurrentStock"] <= df["CalculatedROP"],
        df["CurrentStock"] <= df["ReorderLevel"],
        df["CurrentStock"] >= (df["MaxStock"] * 0.90),
    ]
    reorder_labels = [
        "Reorder Urgent (Stock Below Dynamic ROP)",
        "Reorder Soon (Below Par Level)",
        "Overstocked (Pause Replenishment)"
    ]
    df["ReorderRecommendation"] = np.select(reorder_conditions, reorder_labels, default="Adequate Stock")

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
    df_orders: pd.DataFrame,
    df_details: Optional[pd.DataFrame] = None,
    df_recipes: Optional[pd.DataFrame] = None
) -> dict:
    """Execute all inventory and supply chain optimization analyses."""
    logger.info("Executing comprehensive inventory optimization analysis...")
    
    # Calculate empirical consumption if details and recipes are provided
    df_consumption = None
    if df_details is not None and df_recipes is not None and not df_recipes.empty:
        df_consumption = calculate_recipe_ingredient_consumption(
            df_details=df_details,
            df_recipes=df_recipes,
            df_orders=df_orders,
            df_inventory=df_inventory
        )

    health_df = analyze_inventory_health(df_inventory, df_suppliers)
    turnover_dict = calculate_stock_velocity_and_turnover(df_inventory, df_waste, df_orders)
    rop_df = calculate_reorder_points(df_inventory, df_suppliers, df_consumption=df_consumption)
    wastage_dict = analyze_kitchen_wastage(df_waste)

    return {
        "health": health_df,
        "turnover": turnover_dict,
        "reorder_points": rop_df,
        "wastage": wastage_dict,
        "consumption": df_consumption,
    }
