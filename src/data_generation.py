"""
QSR Sales & Inventory Data Generator
====================================
Generates a realistic Quick-Service Restaurant (QSR) operational dataset
modeled on "Artisan Crust Co.", spanning 12 months (Jan 1, 2024 to Dec 31, 2024).

DATASET TRANSPARENCY NOTICE:
-----------------------------
This dataset is a simulated, synthetic Quick-Service Restaurant benchmark
generated specifically for business intelligence and data analytics modeling.
It does NOT represent confidential customer transactions from a single real-world
restaurant. Transaction distributions, day-part curves, and food cost percentages
(28-32%) are calibrated against published industry benchmarks (e.g. Maven Pizza,
National Restaurant Association operational profiles).

Relational Schema:
1. products.csv: 32 menu items with categories, portion sizes, prices, and food costs.
2. locations.csv: 4 simulated restaurant locations with seating capacity and store types.
3. suppliers.csv: 6 primary QSR suppliers with realistic lead times and reliability ratings.
4. inventory.csv: 24 key food ingredients and packaging items with Beginning Stock (Jan 1, 2024),
   Current Ending Stock (Dec 31, 2024), units, reorder levels, and unit purchase costs.
5. recipes.csv: Bill of Materials (BOM) linking each menu product to its exact ingredient quantities.
6. orders.csv: 33,051 customer orders across 2024 with timestamps, locations, and payment methods.
7. order_details.csv: 65,851 line items with quantities, menu prices, discounts, and line margins.
8. inventory_waste.csv: 1,094 daily kitchen wastage incident logs with root cause reasons and dollar costs.
"""

import os
import sys
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

SEED = 42

# ─────────────────────────────────────────────────────────────────────────────
# 1. Products Definition (32 Menu Items)
# ─────────────────────────────────────────────────────────────────────────────
PRODUCTS_DATA = [
    # Category, Item Name, Size, Unit Price, Unit Cost
    ("Pizza", "Margherita Classic", "Regular", 12.50, 3.50),
    ("Pizza", "Margherita Classic", "Large", 16.50, 4.60),
    ("Pizza", "Pepperoni Feast", "Regular", 14.50, 4.20),
    ("Pizza", "Pepperoni Feast", "Large", 18.50, 5.50),
    ("Pizza", "BBQ Chicken Supreme", "Regular", 15.50, 4.80),
    ("Pizza", "BBQ Chicken Supreme", "Large", 19.50, 6.10),
    ("Pizza", "Veggie Garden Delight", "Regular", 13.00, 3.80),
    ("Pizza", "Veggie Garden Delight", "Large", 17.00, 5.00),
    ("Pizza", "Four Cheese Artisan", "Regular", 14.00, 4.30),
    ("Pizza", "Four Cheese Artisan", "Large", 18.00, 5.70),
    ("Pizza", "Spicy Diablo Sausage", "Regular", 15.00, 4.50),
    ("Pizza", "Spicy Diablo Sausage", "Large", 19.00, 5.90),
    ("Sides", "Garlic Butter Knots (6pc)", "Standard", 5.50, 1.20),
    ("Sides", "Cheesy Stuffed Bread", "Standard", 6.50, 1.80),
    ("Sides", "Buffalo Wings (8pc)", "Standard", 9.50, 3.40),
    ("Sides", "Honey BBQ Wings (8pc)", "Standard", 9.50, 3.40),
    ("Sides", "Mediterranean Caesar Salad", "Regular", 7.00, 2.10),
    ("Sides", "Crispy Seasoned Wedges", "Standard", 4.50, 0.90),
    ("Beverages", "Fountain Soda (Coke/Sprite)", "Regular", 2.75, 0.35),
    ("Beverages", "Fountain Soda (Coke/Sprite)", "Large", 3.50, 0.45),
    ("Beverages", "Artisan Brewed Iced Tea", "Large", 3.75, 0.50),
    ("Beverages", "Fresh Squeezed Lemonade", "Large", 4.00, 0.70),
    ("Beverages", "Sparkling Mineral Water", "Standard", 2.50, 0.60),
    ("Beverages", "Organic Craft Kombucha", "Standard", 4.75, 1.80),
    ("Desserts", "Warm Choco Lava Cake", "Standard", 6.00, 1.60),
    ("Desserts", "Cinnamon Sugar Bites", "Standard", 5.00, 1.10),
    ("Desserts", "New York Cheesecake Slice", "Standard", 5.50, 1.50),
    ("Desserts", "Italian Cannoli Duo", "Standard", 6.50, 1.90),
    ("Combos", "Lunch Rush Solo Combo", "Combo", 14.99, 4.50),
    ("Combos", "Artisan Duo Feast", "Combo", 26.99, 8.20),
    ("Combos", "Family Game Night Box", "Combo", 42.99, 13.50),
    ("Combos", "Party Supreme Bundle", "Combo", 64.99, 21.00),
]

# ─────────────────────────────────────────────────────────────────────────────
# 2. Locations Definition (4 Stores)
# ─────────────────────────────────────────────────────────────────────────────
LOCATIONS_DATA = [
    ("LOC-01", "Downtown Flagship", "Financial District", "Full Dine-in & Delivery", 120),
    ("LOC-02", "Suburb Center", "Westside Suburbs", "Casual Dine-in & Drive-thru", 85),
    ("LOC-03", "Uptown Mall Food Court", "Northway Shopping Mall", "Express Counter", 40),
    ("LOC-04", "Metro Transit Station", "Central Metro Concourse", "Grab & Go Kiosk", 0),
]

# ─────────────────────────────────────────────────────────────────────────────
# 3. Suppliers Definition (6 Vendors)
# ─────────────────────────────────────────────────────────────────────────────
SUPPLIERS_DATA = [
    ("SUP-01", "Valley Dairy & Cheese Co.", "Dairy", 2, 0.96),
    ("SUP-02", "Golden Grain Flour Mills", "Dry Goods & Flour", 4, 0.98),
    ("SUP-03", "Prime Meats & Sausage Wholesale", "Proteins", 2, 0.94),
    ("SUP-04", "FarmFresh Produce Direct", "Fresh Produce", 1, 0.91),
    ("SUP-05", "Apex Beverage Distributors", "Beverages & Syrups", 3, 0.97),
    ("SUP-06", "EcoPack Container Solutions", "Packaging & Disposables", 5, 0.95),
]

# ─────────────────────────────────────────────────────────────────────────────
# 4. Inventory Definition (Beginning Stock + Ending Current Stock)
# ─────────────────────────────────────────────────────────────────────────────
INVENTORY_DATA = [
    # ItemID, Name, Category, BegStock, EndStock, Unit, ReorderLevel, SafetyStock, MaxStock, UnitCost, SupplierID
    ("INV-001", "Whole Milk Mozzarella (Blocks)", "Dairy", 350, 320, "kg", 150, 50, 600, 6.20, "SUP-01"),
    ("INV-002", "Shredded Provolone", "Dairy", 160, 140, "kg", 80, 25, 300, 7.10, "SUP-01"),
    ("INV-003", "Grated Parmesan Reggiano", "Dairy", 105, 95, "kg", 50, 20, 200, 11.50, "SUP-01"),
    ("INV-004", "High-Gluten Pizza Flour", "Dry Goods", 1850, 2350, "kg", 500, 150, 2500, 0.85, "SUP-02"), # Overstocked
    ("INV-005", "Active Dry Yeast", "Dry Goods", 50, 45, "kg", 20, 10, 80, 4.50, "SUP-02"),
    ("INV-006", "San Marzano Style Crushed Tomatoes", "Dry Goods", 650, 620, "cans", 250, 80, 1200, 2.40, "SUP-02"),
    ("INV-007", "Extra Virgin Olive Oil", "Dry Goods", 195, 180, "liters", 75, 25, 350, 8.50, "SUP-02"),
    ("INV-008", "Cured Sliced Pepperoni", "Proteins", 240, 210, "kg", 110, 40, 450, 8.90, "SUP-03"),
    ("INV-009", "Italian Pork Sausage Crumbles", "Proteins", 180, 165, "kg", 90, 30, 350, 7.80, "SUP-03"),
    ("INV-010", "Sous-Vide Diced Chicken Breast", "Proteins", 190, 175, "kg", 95, 35, 400, 7.50, "SUP-03"),
    ("INV-011", "Smoked Bacon Bits", "Proteins", 95, 85, "kg", 50, 15, 200, 9.20, "SUP-03"),
    ("INV-012", "Jumbo Chicken Wings (Raw)", "Proteins", 460, 420, "kg", 200, 75, 800, 4.80, "SUP-03"),
    ("INV-013", "Fresh White Button Mushrooms", "Produce", 55, 32, "kg", 40, 15, 120, 3.20, "SUP-04"), # Low Stock Alert
    ("INV-014", "Fresh Green Bell Peppers", "Produce", 60, 55, "kg", 35, 15, 100, 2.40, "SUP-04"),
    ("INV-015", "Red Onions", "Produce", 75, 70, "kg", 40, 15, 150, 1.80, "SUP-04"),
    ("INV-016", "Fresh Romaine Hearts", "Produce", 40, 20, "cases", 25, 10, 80, 14.50, "SUP-04"), # Low Stock Alert
    ("INV-017", "Fresh Genovese Basil", "Produce", 22, 8, "kg", 12, 5, 35, 12.00, "SUP-04"),     # Low Stock Alert
    ("INV-018", "Post-Mix Soda Syrup (Cola 5gal)", "Beverages", 32, 28, "boxes", 15, 5, 50, 65.00, "SUP-05"),
    ("INV-019", "Lemonade Concentrate (3gal)", "Beverages", 18, 16, "boxes", 10, 4, 35, 42.00, "SUP-05"),
    ("INV-020", "Craft Black Tea Leaves", "Beverages", 35, 30, "kg", 15, 5, 60, 9.50, "SUP-05"),
    ("INV-021", "Corrugated Pizza Boxes 12in", "Packaging", 2100, 1800, "units", 800, 250, 4000, 0.42, "SUP-06"),
    ("INV-022", "Corrugated Pizza Boxes 16in", "Packaging", 1600, 1400, "units", 600, 200, 3000, 0.58, "SUP-06"),
    ("INV-023", "Kraft Side Carryout Bags", "Packaging", 3200, 4600, "units", 1000, 300, 5000, 0.18, "SUP-06"), # Overstocked
    ("INV-024", "Biodegradable Beverage Cups & Lids", "Packaging", 3900, 3400, "units", 1500, 500, 7000, 0.12, "SUP-06"),
]

# ─────────────────────────────────────────────────────────────────────────────
# 5. Recipe / Bill of Materials (BOM) Definition
# ─────────────────────────────────────────────────────────────────────────────
# Maps ProductID to required ingredient quantities per finished menu item
RECIPES_DATA = [
    # Margherita Classic Reg
    ("PRD-001", "INV-004", 0.20, "kg"),    # Flour
    ("PRD-001", "INV-005", 0.005, "kg"),   # Yeast
    ("PRD-001", "INV-006", 0.35, "cans"),  # Tomato Sauce
    ("PRD-001", "INV-007", 0.03, "liters"),# Olive Oil
    ("PRD-001", "INV-001", 0.18, "kg"),    # Mozzarella
    ("PRD-001", "INV-017", 0.015, "kg"),   # Basil
    ("PRD-001", "INV-021", 1.0, "units"),  # 12in Box
    # Margherita Classic Large
    ("PRD-002", "INV-004", 0.30, "kg"),
    ("PRD-002", "INV-005", 0.008, "kg"),
    ("PRD-002", "INV-006", 0.50, "cans"),
    ("PRD-002", "INV-007", 0.04, "liters"),
    ("PRD-002", "INV-001", 0.26, "kg"),
    ("PRD-002", "INV-017", 0.020, "kg"),
    ("PRD-002", "INV-022", 1.0, "units"),  # 16in Box
    # Pepperoni Feast Reg
    ("PRD-003", "INV-004", 0.20, "kg"),
    ("PRD-003", "INV-005", 0.005, "kg"),
    ("PRD-003", "INV-006", 0.35, "cans"),
    ("PRD-003", "INV-007", 0.03, "liters"),
    ("PRD-003", "INV-001", 0.18, "kg"),
    ("PRD-003", "INV-008", 0.10, "kg"),    # Pepperoni
    ("PRD-003", "INV-021", 1.0, "units"),
    # Pepperoni Feast Large
    ("PRD-004", "INV-004", 0.30, "kg"),
    ("PRD-004", "INV-005", 0.008, "kg"),
    ("PRD-004", "INV-006", 0.50, "cans"),
    ("PRD-004", "INV-007", 0.04, "liters"),
    ("PRD-004", "INV-001", 0.26, "kg"),
    ("PRD-004", "INV-008", 0.15, "kg"),
    ("PRD-004", "INV-022", 1.0, "units"),
    # BBQ Chicken Reg
    ("PRD-005", "INV-004", 0.20, "kg"),
    ("PRD-005", "INV-001", 0.18, "kg"),
    ("PRD-005", "INV-010", 0.12, "kg"),    # Diced Chicken
    ("PRD-005", "INV-011", 0.04, "kg"),    # Smoked Bacon Bits
    ("PRD-005", "INV-015", 0.04, "kg"),    # Red Onions
    ("PRD-005", "INV-021", 1.0, "units"),
    # BBQ Chicken Large
    ("PRD-006", "INV-004", 0.30, "kg"),
    ("PRD-006", "INV-001", 0.26, "kg"),
    ("PRD-006", "INV-010", 0.18, "kg"),
    ("PRD-006", "INV-011", 0.06, "kg"),    # Smoked Bacon Bits
    ("PRD-006", "INV-015", 0.06, "kg"),
    ("PRD-006", "INV-022", 1.0, "units"),

    # Veggie Delight Reg & Large
    ("PRD-007", "INV-004", 0.20, "kg"),
    ("PRD-007", "INV-001", 0.18, "kg"),
    ("PRD-007", "INV-013", 0.05, "kg"),    # Mushrooms
    ("PRD-007", "INV-014", 0.05, "kg"),    # Bell Peppers
    ("PRD-007", "INV-015", 0.03, "kg"),
    ("PRD-007", "INV-021", 1.0, "units"),
    ("PRD-008", "INV-004", 0.30, "kg"),
    ("PRD-008", "INV-001", 0.26, "kg"),
    ("PRD-008", "INV-013", 0.08, "kg"),
    ("PRD-008", "INV-014", 0.08, "kg"),
    ("PRD-008", "INV-015", 0.05, "kg"),
    ("PRD-008", "INV-022", 1.0, "units"),
    # 4 Cheese Reg & Large
    ("PRD-009", "INV-004", 0.20, "kg"),
    ("PRD-009", "INV-001", 0.14, "kg"),    # Mozzarella
    ("PRD-009", "INV-002", 0.08, "kg"),    # Provolone
    ("PRD-009", "INV-003", 0.04, "kg"),    # Parmesan
    ("PRD-009", "INV-021", 1.0, "units"),
    ("PRD-010", "INV-004", 0.30, "kg"),
    ("PRD-010", "INV-001", 0.20, "kg"),
    ("PRD-010", "INV-002", 0.12, "kg"),
    ("PRD-010", "INV-003", 0.06, "kg"),
    ("PRD-010", "INV-022", 1.0, "units"),
    # Diablo Sausage Reg & Large
    ("PRD-011", "INV-004", 0.20, "kg"),
    ("PRD-011", "INV-001", 0.18, "kg"),
    ("PRD-011", "INV-009", 0.12, "kg"),    # Sausage
    ("PRD-011", "INV-014", 0.04, "kg"),
    ("PRD-011", "INV-021", 1.0, "units"),
    ("PRD-012", "INV-004", 0.30, "kg"),
    ("PRD-012", "INV-001", 0.26, "kg"),
    ("PRD-012", "INV-009", 0.18, "kg"),
    ("PRD-012", "INV-014", 0.06, "kg"),
    ("PRD-012", "INV-022", 1.0, "units"),
    # Sides
    ("PRD-013", "INV-004", 0.15, "kg"),    # Knots flour
    ("PRD-013", "INV-003", 0.02, "kg"),    # Parmesan
    ("PRD-013", "INV-023", 1.0, "units"),  # Bag
    ("PRD-014", "INV-004", 0.20, "kg"),    # Cheesy bread
    ("PRD-014", "INV-001", 0.10, "kg"),
    ("PRD-014", "INV-023", 1.0, "units"),
    ("PRD-015", "INV-012", 0.35, "kg"),    # Buffalo Wings
    ("PRD-015", "INV-023", 1.0, "units"),
    ("PRD-016", "INV-012", 0.35, "kg"),    # BBQ Wings
    ("PRD-016", "INV-023", 1.0, "units"),
    ("PRD-017", "INV-016", 0.05, "cases"), # Caesar Salad (Romaine)
    ("PRD-017", "INV-003", 0.03, "kg"),    # Parmesan
    ("PRD-017", "INV-023", 1.0, "units"),
    ("PRD-018", "INV-007", 0.05, "liters"),# Wedges
    ("PRD-018", "INV-023", 1.0, "units"),
    # Beverages
    ("PRD-019", "INV-018", 0.04, "boxes"), # Soda Reg
    ("PRD-019", "INV-024", 1.0, "units"),  # Cup
    ("PRD-020", "INV-018", 0.06, "boxes"), # Soda Large
    ("PRD-020", "INV-024", 1.0, "units"),
    ("PRD-021", "INV-020", 0.03, "kg"),    # Tea
    ("PRD-021", "INV-024", 1.0, "units"),
    ("PRD-022", "INV-019", 0.05, "boxes"), # Lemonade
    ("PRD-022", "INV-024", 1.0, "units"),
    ("PRD-023", "INV-024", 1.0, "units"),  # Mineral water cup
    ("PRD-024", "INV-024", 1.0, "units"),  # Kombucha cup
    # Desserts
    ("PRD-025", "INV-023", 1.0, "units"),  # Lava cake
    ("PRD-026", "INV-004", 0.08, "kg"),    # Cinnamon bites flour
    ("PRD-026", "INV-023", 1.0, "units"),
    ("PRD-027", "INV-023", 1.0, "units"),  # Cheesecake
    ("PRD-028", "INV-002", 0.06, "kg"),    # Cannoli
    ("PRD-028", "INV-023", 1.0, "units"),
    # Combos
    ("PRD-029", "INV-004", 0.15, "kg"),    # Solo combo (Small pizza + drink)
    ("PRD-029", "INV-001", 0.12, "kg"),
    ("PRD-029", "INV-018", 0.04, "boxes"),
    ("PRD-029", "INV-021", 1.0, "units"),
    ("PRD-029", "INV-024", 1.0, "units"),
    ("PRD-030", "INV-004", 0.35, "kg"),    # Duo feast (2 pizzas + 2 drinks)
    ("PRD-030", "INV-001", 0.28, "kg"),
    ("PRD-030", "INV-018", 0.08, "boxes"),
    ("PRD-030", "INV-021", 2.0, "units"),
    ("PRD-030", "INV-024", 2.0, "units"),
    ("PRD-031", "INV-004", 0.60, "kg"),    # Family box (2 Large + wings + drinks)
    ("PRD-031", "INV-001", 0.50, "kg"),
    ("PRD-031", "INV-008", 0.20, "kg"),
    ("PRD-031", "INV-012", 0.35, "kg"),
    ("PRD-031", "INV-018", 0.15, "boxes"),
    ("PRD-031", "INV-022", 2.0, "units"),
    ("PRD-031", "INV-024", 4.0, "units"),
    ("PRD-032", "INV-004", 0.90, "kg"),    # Party bundle (3 Large + 2 wings + knots + drinks)
    ("PRD-032", "INV-001", 0.75, "kg"),
    ("PRD-032", "INV-008", 0.30, "kg"),
    ("PRD-032", "INV-012", 0.70, "kg"),
    ("PRD-032", "INV-018", 0.25, "boxes"),
    ("PRD-032", "INV-022", 3.0, "units"),
    ("PRD-032", "INV-024", 6.0, "units"),
]


def generate_qsr_dataset(raw_dir: str = "data/raw") -> dict:
    """Generate all raw CSV files for the QSR analytics project."""
    os.makedirs(raw_dir, exist_ok=True)
    rng = np.random.default_rng(SEED)

    # 1. Products DataFrame
    products_list = []
    for idx, (cat, name, size, price, cost) in enumerate(PRODUCTS_DATA, start=1):
        pid = f"PRD-{str(idx).zfill(3)}"
        margin = round((price - cost) / price * 100, 1)
        products_list.append({
            "ProductID": pid,
            "ProductName": name,
            "Category": cat,
            "Size": size,
            "UnitPrice": price,
            "UnitCost": cost,
            "TargetMarginPct": margin,
        })
    df_products = pd.DataFrame(products_list)
    df_products.to_csv(os.path.join(raw_dir, "products.csv"), index=False)

    # 2. Locations DataFrame
    locations_list = []
    for loc_id, name, district, stype, seats in LOCATIONS_DATA:
        locations_list.append({
            "LocationID": loc_id,
            "LocationName": name,
            "District": district,
            "StoreType": stype,
            "SeatingCapacity": seats,
        })
    df_locations = pd.DataFrame(locations_list)
    df_locations.to_csv(os.path.join(raw_dir, "locations.csv"), index=False)

    # 3. Suppliers DataFrame
    suppliers_list = []
    for sid, name, cat, lead, rel in SUPPLIERS_DATA:
        suppliers_list.append({
            "SupplierID": sid,
            "SupplierName": name,
            "CategorySupplied": cat,
            "LeadTimeDays": lead,
            "ReliabilityScore": rel,
        })
    df_suppliers = pd.DataFrame(suppliers_list)
    df_suppliers.to_csv(os.path.join(raw_dir, "suppliers.csv"), index=False)

    # 4. Inventory Master DataFrame (with Beginning & Ending Stock)
    inventory_list = []
    for iid, name, cat, beg_stock, end_stock, unit, reorder, safety, max_stk, cost, sid in INVENTORY_DATA:
        inventory_list.append({
            "InventoryID": iid,
            "ItemName": name,
            "Category": cat,
            "BeginningStock": beg_stock,
            "CurrentStock": end_stock,
            "Unit": unit,
            "ReorderLevel": reorder,
            "SafetyStock": safety,
            "MaxStock": max_stk,
            "UnitCost": cost,
            "SupplierID": sid,
        })
    df_inventory = pd.DataFrame(inventory_list)
    df_inventory.to_csv(os.path.join(raw_dir, "inventory.csv"), index=False)

    # 5. Recipes / BOM DataFrame
    recipes_list = []
    for r_idx, (pid, iid, qty, unit) in enumerate(RECIPES_DATA, start=1):
        recipes_list.append({
            "RecipeID": f"RCP-{str(r_idx).zfill(4)}",
            "ProductID": pid,
            "InventoryID": iid,
            "QuantityPerUnit": qty,
            "Unit": unit,
        })
    df_recipes = pd.DataFrame(recipes_list)
    df_recipes.to_csv(os.path.join(raw_dir, "recipes.csv"), index=False)

    # 6. Orders & Order Details Generation
    start_date = datetime(2024, 1, 1)
    n_days = 366  # 2024 leap year

    p_weights = np.array([
        0.05, 0.07,  # Margherita
        0.08, 0.11,  # Pepperoni (Top)
        0.04, 0.06,  # BBQ Chicken
        0.03, 0.04,  # Veggie
        0.03, 0.04,  # 4 Cheese
        0.03, 0.04,  # Diablo
        0.05, 0.04, 0.04, 0.03, 0.03, 0.04, # Sides
        0.05, 0.04, 0.03, 0.03, 0.02, 0.01, # Beverages
        0.03, 0.02, 0.02, 0.02,             # Desserts
        0.06, 0.05, 0.03, 0.01              # Combos
    ])
    p_weights = p_weights / p_weights.sum()

    location_weights = [0.38, 0.28, 0.22, 0.12]
    payment_methods = ["Credit Card", "Debit Card", "Mobile Payment", "Cash"]
    payment_weights = [0.45, 0.25, 0.20, 0.10]
    order_types = ["Dine-In", "Takeout", "Delivery", "Drive-Thru"]
    order_type_weights = [0.32, 0.38, 0.22, 0.08]

    orders_records = []
    order_details_records = []

    order_id_counter = 1
    detail_id_counter = 1

    hours = list(range(10, 23))
    hourly_probs = np.array([
        0.02, 0.06, 0.16, 0.14, 0.06, 0.04, 0.06, 0.12, 0.15, 0.10, 0.05, 0.03, 0.01
    ])
    hourly_probs = hourly_probs / hourly_probs.sum()

    for day_offset in range(n_days):
        current_date = start_date + timedelta(days=day_offset)
        weekday = current_date.weekday()
        is_weekend = weekday >= 4

        if is_weekend:
            daily_orders_count = rng.integers(90, 125)
        else:
            daily_orders_count = rng.integers(60, 85)

        month = current_date.month
        if month in [6, 7, 8, 12]:
            daily_orders_count = int(daily_orders_count * 1.12)

        for _ in range(daily_orders_count):
            order_id = f"ORD-2024-{str(order_id_counter).zfill(6)}"
            order_id_counter += 1

            h = rng.choice(hours, p=hourly_probs)
            m = rng.integers(0, 60)
            s = rng.integers(0, 60)
            order_time = f"{str(h).zfill(2)}:{str(m).zfill(2)}:{str(s).zfill(2)}"

            loc = rng.choice(["LOC-01", "LOC-02", "LOC-03", "LOC-04"], p=location_weights)
            pay = rng.choice(payment_methods, p=payment_weights)
            otype = rng.choice(order_types, p=order_type_weights)
            
            if loc == "LOC-04" and otype == "Dine-In":
                otype = "Takeout"

            num_items = rng.choice([1, 2, 3, 4], p=[0.42, 0.35, 0.18, 0.05])
            if is_weekend and otype in ["Delivery", "Dine-In"]:
                num_items = rng.choice([1, 2, 3, 4, 5], p=[0.25, 0.35, 0.25, 0.10, 0.05])

            chosen_indices = rng.choice(len(PRODUCTS_DATA), size=num_items, replace=False, p=p_weights)

            order_subtotal = 0.0
            order_discount = 0.0
            order_cost_total = 0.0
            order_qty_total = 0

            for p_idx in chosen_indices:
                prod = df_products.iloc[p_idx]
                qty = int(rng.choice([1, 2, 3], p=[0.82, 0.14, 0.04]))
                unit_p = float(prod["UnitPrice"])
                unit_c = float(prod["UnitCost"])

                discount_rate = 0.0
                if prod["Category"] == "Combos" and rng.random() < 0.20:
                    discount_rate = 0.10
                elif h in [14, 15, 16] and rng.random() < 0.25:
                    discount_rate = 0.15

                line_subtotal = round(qty * unit_p, 2)
                line_discount = round(line_subtotal * discount_rate, 2)
                line_total = round(line_subtotal - line_discount, 2)
                line_cost = round(qty * unit_c, 2)
                line_profit = round(line_total - line_cost, 2)

                order_details_records.append({
                    "OrderDetailID": f"DET-{str(detail_id_counter).zfill(7)}",
                    "OrderID": order_id,
                    "ProductID": prod["ProductID"],
                    "ProductName": prod["ProductName"],
                    "Category": prod["Category"],
                    "Quantity": qty,
                    "UnitPrice": unit_p,
                    "Discount": line_discount,
                    "TotalPrice": line_total,
                    "LineCost": line_cost,
                    "LineProfit": line_profit,
                })
                detail_id_counter += 1

                order_subtotal += line_subtotal
                order_discount += line_discount
                order_cost_total += line_cost
                order_qty_total += qty

            order_net_total = round(order_subtotal - order_discount, 2)
            orders_records.append({
                "OrderID": order_id,
                "OrderDate": current_date.strftime("%Y-%m-%d"),
                "OrderTime": order_time,
                "LocationID": loc,
                "PaymentMethod": pay,
                "OrderType": otype,
                "ItemCount": order_qty_total,
                "GrossSales": round(order_subtotal, 2),
                "DiscountAmount": round(order_discount, 2),
                "NetSales": order_net_total,
                "TotalCost": round(order_cost_total, 2),
                "GrossProfit": round(order_net_total - order_cost_total, 2),
            })

    df_orders = pd.DataFrame(orders_records)
    df_order_details = pd.DataFrame(order_details_records)

    df_orders.to_csv(os.path.join(raw_dir, "orders.csv"), index=False)
    df_order_details.to_csv(os.path.join(raw_dir, "order_details.csv"), index=False)

    # 7. Inventory Waste Log Generation (366 days across 4 locations)
    waste_records = []
    waste_reasons = ["Expired Shelf-Life", "Preparation Trim/Spillage", "Overcooked/Burnt", "Drop/Damaged Handling"]
    waste_reasons_probs = [0.45, 0.25, 0.15, 0.15]
    waste_id_counter = 1

    perishable_inv_ids = [
        "INV-001", "INV-002", "INV-004", "INV-008", "INV-010",
        "INV-012", "INV-013", "INV-014", "INV-016", "INV-017"
    ]

    for day_offset in range(n_days):
        current_date = start_date + timedelta(days=day_offset)
        n_incidents = rng.integers(2, 5)
        for _ in range(n_incidents):
            inv_id = rng.choice(perishable_inv_ids)
            inv_row = df_inventory[df_inventory["InventoryID"] == inv_id].iloc[0]
            loc_id = rng.choice(["LOC-01", "LOC-02", "LOC-03", "LOC-04"])
            reason = rng.choice(waste_reasons, p=waste_reasons_probs)

            w_qty = round(float(rng.uniform(1.2, 5.5)), 2)
            cost_impact = round(w_qty * float(inv_row["UnitCost"]), 2)

            waste_records.append({
                "WasteID": f"WST-{str(waste_id_counter).zfill(6)}",
                "WasteDate": current_date.strftime("%Y-%m-%d"),
                "LocationID": loc_id,
                "InventoryID": inv_id,
                "ItemName": inv_row["ItemName"],
                "Category": inv_row["Category"],
                "QuantityWasted": w_qty,
                "Unit": inv_row["Unit"],
                "UnitCost": inv_row["UnitCost"],
                "WasteCost": cost_impact,
                "Reason": reason,
            })
            waste_id_counter += 1

    df_waste = pd.DataFrame(waste_records)
    df_waste.to_csv(os.path.join(raw_dir, "inventory_waste.csv"), index=False)

    logger.info(f"Generated QSR Raw Datasets in {raw_dir}:")
    logger.info(f"  Products:      {len(df_products)} rows")
    logger.info(f"  Locations:     {len(df_locations)} rows")
    logger.info(f"  Suppliers:     {len(df_suppliers)} rows")
    logger.info(f"  Inventory:     {len(df_inventory)} rows (with Beginning & Ending Stock)")
    logger.info(f"  Recipes (BOM): {len(df_recipes)} recipe-ingredient links")
    logger.info(f"  Orders:        {len(df_orders):,} rows")
    logger.info(f"  Order Details: {len(df_order_details):,} rows")
    logger.info(f"  Waste Logs:    {len(df_waste):,} rows")

    return {
        "products": df_products,
        "locations": df_locations,
        "suppliers": df_suppliers,
        "inventory": df_inventory,
        "recipes": df_recipes,
        "orders": df_orders,
        "order_details": df_order_details,
        "waste": df_waste,
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(levelname)s — %(message)s")
    generate_qsr_dataset()
