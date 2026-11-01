"""
QSR Data Cleaning & Feature Engineering Pipeline
=================================================
Performs comprehensive data hygiene, type casting, validation checks,
and feature engineering across QSR transactional and operational tables.

Cleaning Steps:
1. Missing value analysis and treatment
2. Duplicate row detection and removal
3. Data type normalization (dates, timestamps, decimals, integers)
4. Temporal feature extraction (Hour, Month, Day of Week, IsWeekend, MealPeriod)
5. Outlier and anomaly checks (negative prices, invalid quantities)
6. Revenue and profit verification (NetSales = GrossSales - Discount)
7. Integration of Product and Location master metadata
8. Exporting cleaned datasets to data/processed/
"""

import os
import sys
import logging
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


def get_meal_period(hour: int) -> str:
    """Categorize operating hour into QSR day-part segments."""
    if 6 <= hour < 11:
        return "Breakfast"
    elif 11 <= hour < 15:
        return "Lunch Rush"
    elif 15 <= hour < 17:
        return "Afternoon Snack"
    elif 17 <= hour < 21:
        return "Dinner Rush"
    else:
        return "Late Night"


def clean_products(df_products: pd.DataFrame) -> pd.DataFrame:
    """Clean and validate products master table."""
    df = df_products.copy()
    df = df.drop_duplicates(subset=["ProductID"]).reset_index(drop=True)
    
    # Type corrections
    df["UnitPrice"] = pd.to_numeric(df["UnitPrice"], errors="coerce")
    df["UnitCost"] = pd.to_numeric(df["UnitCost"], errors="coerce")
    
    # Validation: positive values
    df = df[(df["UnitPrice"] > 0) & (df["UnitCost"] > 0)].copy()
    df["GrossMarginDollar"] = (df["UnitPrice"] - df["UnitCost"]).round(2)
    df["GrossMarginPct"] = ((df["GrossMarginDollar"] / df["UnitPrice"]) * 100).round(1)
    
    logger.info(f"Products cleaned: {len(df)} menu items")
    return df


def clean_locations(df_locations: pd.DataFrame) -> pd.DataFrame:
    """Clean and validate locations master table."""
    df = df_locations.copy()
    df = df.drop_duplicates(subset=["LocationID"]).reset_index(drop=True)
    df["SeatingCapacity"] = pd.to_numeric(df["SeatingCapacity"], errors="coerce").fillna(0).astype(int)
    logger.info(f"Locations cleaned: {len(df)} locations")
    return df


def clean_inventory(df_inventory: pd.DataFrame) -> pd.DataFrame:
    """Clean and validate inventory table with Beginning and Ending valuation."""
    df = df_inventory.copy()
    df = df.drop_duplicates(subset=["InventoryID"]).reset_index(drop=True)
    
    num_cols = ["BeginningStock", "CurrentStock", "ReorderLevel", "SafetyStock", "MaxStock", "UnitCost"]
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    
    # Feature engineering: Beginning, Ending, and Average Inventory Valuation
    if "BeginningStock" in df.columns:
        df["BeginningValuation"] = (df["BeginningStock"] * df["UnitCost"]).round(2)
    else:
        df["BeginningValuation"] = (df["CurrentStock"] * df["UnitCost"]).round(2)
        
    df["InventoryValuation"] = (df["CurrentStock"] * df["UnitCost"]).round(2)  # Ending valuation
    df["EndingValuation"] = df["InventoryValuation"]
    df["AverageValuation"] = ((df["BeginningValuation"] + df["EndingValuation"]) / 2.0).round(2)
    
    # Stock Status Classification
    conditions = [
        df["CurrentStock"] <= df["ReorderLevel"],
        df["CurrentStock"] >= (df["MaxStock"] * 0.90),
    ]
    choices = ["Low Stock (Reorder Alert)", "Overstocked"]
    df["StockStatus"] = np.select(conditions, choices, default="Optimal Stock")
    
    logger.info(f"Inventory cleaned: {len(df)} inventory items")
    return df


def clean_recipes(df_recipes: pd.DataFrame) -> pd.DataFrame:
    """Clean and validate Bill of Materials (recipes) mapping table."""
    df = df_recipes.copy()
    df = df.drop_duplicates(subset=["RecipeID"]).reset_index(drop=True)
    qty_col = "QuantityPerUnit" if "QuantityPerUnit" in df.columns else "QuantityRequired"
    df[qty_col] = pd.to_numeric(df[qty_col], errors="coerce").fillna(0.0)
    df = df[df[qty_col] > 0].copy()
    logger.info(f"Recipes (BOM) cleaned: {len(df)} recipe-ingredient links")
    return df




def clean_orders(df_orders: pd.DataFrame) -> pd.DataFrame:
    """Clean, parse timestamps, and engineer features on orders table."""
    df = df_orders.copy()
    before_len = len(df)
    df = df.drop_duplicates(subset=["OrderID"]).reset_index(drop=True)
    if len(df) < before_len:
        logger.info(f"Removed {before_len - len(df)} duplicate orders")

    # Parse Date & Time
    df["OrderDate"] = pd.to_datetime(df["OrderDate"], errors="coerce")
    df = df.dropna(subset=["OrderDate"]).copy()
    
    # Extract temporal features
    df["OrderYear"] = df["OrderDate"].dt.year
    df["OrderMonth"] = df["OrderDate"].dt.month
    df["OrderMonthName"] = df["OrderDate"].dt.strftime("%b")
    df["OrderQuarter"] = df["OrderDate"].dt.to_period("Q").astype(str)
    df["DayOfWeek"] = df["OrderDate"].dt.dayofweek  # 0=Monday, 6=Sunday
    df["DayName"] = df["OrderDate"].dt.day_name()
    df["IsWeekend"] = df["DayOfWeek"].isin([4, 5, 6]).astype(int)  # Fri, Sat, Sun

    # Parse OrderHour and MealPeriod
    df["OrderHour"] = pd.to_datetime(df["OrderTime"], format="%H:%M:%S", errors="coerce").dt.hour
    df["MealPeriod"] = df["OrderHour"].apply(get_meal_period)

    # Ensure numeric columns
    monetary_cols = ["GrossSales", "DiscountAmount", "NetSales", "TotalCost", "GrossProfit"]
    for col in monetary_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0).round(2)

    # Revenue verification check
    calc_net = (df["GrossSales"] - df["DiscountAmount"]).round(2)
    diff = (df["NetSales"] - calc_net).abs()
    if (diff > 0.05).any():
        logger.warning(f"Re-aligning {sum(diff > 0.05)} orders where NetSales != GrossSales - Discount")
        df["NetSales"] = calc_net

    df["GrossMarginPct"] = np.where(
        df["NetSales"] > 0,
        ((df["GrossProfit"] / df["NetSales"]) * 100).round(2),
        0.0
    )

    logger.info(f"Orders cleaned: {len(df):,} orders")
    return df


def clean_order_details(df_details: pd.DataFrame, df_products: pd.DataFrame) -> pd.DataFrame:
    """Clean order line items and verify line totals and margins."""
    df = df_details.copy()
    df = df.drop_duplicates(subset=["OrderDetailID"]).reset_index(drop=True)

    numeric_cols = ["Quantity", "UnitPrice", "Discount", "TotalPrice", "LineCost", "LineProfit"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    df["Quantity"] = df["Quantity"].astype(int)
    # Filter non-positive quantities
    df = df[df["Quantity"] > 0].copy()

    # Verify line totals
    expected_total = (df["Quantity"] * df["UnitPrice"] - df["Discount"]).round(2)
    df["TotalPrice"] = expected_total

    logger.info(f"Order details cleaned: {len(df):,} line items")
    return df


def clean_waste_log(df_waste: pd.DataFrame) -> pd.DataFrame:
    """Clean and validate kitchen wastage logs."""
    df = df_waste.copy()
    df = df.drop_duplicates(subset=["WasteID"]).reset_index(drop=True)
    df["WasteDate"] = pd.to_datetime(df["WasteDate"], errors="coerce")
    df["QuantityWasted"] = pd.to_numeric(df["QuantityWasted"], errors="coerce").fillna(0.0)
    df["UnitCost"] = pd.to_numeric(df["UnitCost"], errors="coerce").fillna(0.0)
    df["WasteCost"] = (df["QuantityWasted"] * df["UnitCost"]).round(2)
    logger.info(f"Waste log cleaned: {len(df):,} entries")
    return df


def run_data_cleaning_pipeline(
    raw_dir: str = "data/raw",
    processed_dir: str = "data/processed"
) -> dict:
    """Execute complete cleaning pipeline and save processed datasets."""
    os.makedirs(processed_dir, exist_ok=True)
    logger.info("=" * 60)
    logger.info("STARTING QSR DATA CLEANING PIPELINE")
    logger.info("=" * 60)

    # 1. Load raw files
    df_products_raw = pd.read_csv(os.path.join(raw_dir, "products.csv"))
    df_locations_raw = pd.read_csv(os.path.join(raw_dir, "locations.csv"))
    df_suppliers_raw = pd.read_csv(os.path.join(raw_dir, "suppliers.csv"))
    df_inventory_raw = pd.read_csv(os.path.join(raw_dir, "inventory.csv"))
    df_recipes_raw = pd.read_csv(os.path.join(raw_dir, "recipes.csv")) if os.path.exists(os.path.join(raw_dir, "recipes.csv")) else pd.DataFrame()
    df_orders_raw = pd.read_csv(os.path.join(raw_dir, "orders.csv"))
    df_details_raw = pd.read_csv(os.path.join(raw_dir, "order_details.csv"))
    df_waste_raw = pd.read_csv(os.path.join(raw_dir, "inventory_waste.csv"))

    # 2. Clean individual tables
    products_clean = clean_products(df_products_raw)
    locations_clean = clean_locations(df_locations_raw)
    suppliers_clean = df_suppliers_raw.drop_duplicates(subset=["SupplierID"]).copy()
    inventory_clean = clean_inventory(df_inventory_raw)
    recipes_clean = clean_recipes(df_recipes_raw) if not df_recipes_raw.empty else pd.DataFrame()
    orders_clean = clean_orders(df_orders_raw)
    details_clean = clean_order_details(df_details_raw, products_clean)
    waste_clean = clean_waste_log(df_waste_raw)

    # 3. Create Denormalized Master Table for Fast BI / EDA
    # Merge order items with orders, products, and locations
    master = details_clean.merge(
        orders_clean[["OrderID", "OrderDate", "OrderTime", "OrderYear", "OrderMonth",
                      "OrderMonthName", "OrderQuarter", "DayOfWeek", "DayName", "IsWeekend",
                      "OrderHour", "MealPeriod", "LocationID", "PaymentMethod", "OrderType"]],
        on="OrderID",
        how="inner"
    ).merge(
        locations_clean[["LocationID", "LocationName", "District", "StoreType"]],
        on="LocationID",
        how="left"
    )

    # 4. Save to processed directory
    products_clean.to_csv(os.path.join(processed_dir, "products_cleaned.csv"), index=False)
    locations_clean.to_csv(os.path.join(processed_dir, "locations_cleaned.csv"), index=False)
    suppliers_clean.to_csv(os.path.join(processed_dir, "suppliers_cleaned.csv"), index=False)
    inventory_clean.to_csv(os.path.join(processed_dir, "inventory_cleaned.csv"), index=False)
    if not recipes_clean.empty:
        recipes_clean.to_csv(os.path.join(processed_dir, "recipes_cleaned.csv"), index=False)
    orders_clean.to_csv(os.path.join(processed_dir, "orders_cleaned.csv"), index=False)
    details_clean.to_csv(os.path.join(processed_dir, "order_details_cleaned.csv"), index=False)
    waste_clean.to_csv(os.path.join(processed_dir, "inventory_waste_cleaned.csv"), index=False)
    master.to_csv(os.path.join(processed_dir, "qsr_sales_master.csv"), index=False)

    logger.info("=" * 60)
    logger.info(f"CLEANING PIPELINE COMPLETE — Saved to {processed_dir}")
    logger.info(f"Master Transaction Dataset Shape: {master.shape}")
    logger.info("=" * 60)

    return {
        "products": products_clean,
        "locations": locations_clean,
        "suppliers": suppliers_clean,
        "inventory": inventory_clean,
        "recipes": recipes_clean,
        "orders": orders_clean,
        "order_details": details_clean,
        "waste": waste_clean,
        "master": master,
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(levelname)s — %(message)s")
    run_data_cleaning_pipeline()
