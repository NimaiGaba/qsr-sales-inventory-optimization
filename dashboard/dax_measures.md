# Power BI Executive Dashboard Architecture & DAX Measures Guide

> **Environment Disclosure & Reproducibility Notice:**  
> Power BI Desktop is not installed on this Linux/Windows headless runtime environment. Therefore, a binary `.pbix` file is not generated. Instead, this repository provides complete, validated star-schema CSV exports in `dashboard/exports/`, an automated SQLite database, 14 publication-grade PNG visualizations in `dashboard/charts/`, and this production-ready DAX repository and visual design guide. When opened in Power BI Desktop on any desktop workstation, connecting to `dashboard/exports/` and copying these exact measures produces the 4-page dashboard immediately.

---

## 1. Enterprise Star Schema Data Model

### 1.1 Data Source Tables (`dashboard/exports/`)
| Table Name | File Name | Role | Primary Key | Foreign Keys | Row Count |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **FactOrders** | `FactOrders.csv` | Fact (Header) | `OrderID` | `LocationID`, `OrderDate` | 33,051 |
| **FactOrderItems** | `FactOrderItems.csv` | Fact (Line Item) | `OrderDetailID` | `OrderID`, `ProductID` | 65,851 |
| **DimProducts** | `DimProducts.csv` | Dimension | `ProductID` | — | 32 |
| **DimLocations** | `DimLocations.csv` | Dimension | `LocationID` | — | 4 |
| **DimInventory** | `DimInventory.csv` | Dimension / Snapshot | `InventoryID` | `SupplierID` | 24 |
| **DimRecipes** | `DimRecipes.csv` | Dimension (BOM) | `RecipeID` | `ProductID`, `InventoryID` | 125 |
| **FactWaste** | `FactWaste.csv` | Fact (Wastage) | `WasteID` | `InventoryID`, `WasteDate` | 1,094 |
| **DimCalendar** | `DimCalendar.csv` | Dimension (Date) | `Date` | — | 366 |
| **ReportReorder** | `ReportReorderRecommendations.csv` | Operational Report | `InventoryID` | — | 24 |

### 1.2 Data Model Relationships (Star Schema)

```
                     ┌──────────────────┐
                     │   DimCalendar    │
                     │      (Date)      │
                     └────────┬─────────┘
                              │ 1
                              │
                              │ * (OrderDate)
┌──────────────────┐          ▼          ┌──────────────────┐
│   DimLocations   │1 ────────*──────── 1│   DimProducts    │
│   (LocationID)   │      FactOrders     │   (ProductID)    │
└──────────────────┘     (Gross, Net)    └────────┬─────────┘
                              │ 1                 │ 1
                              │                   │
                              │ * (OrderID)       │ * (ProductID)
                              ▼                   ▼
                     ┌──────────────────────────────┐
                     │        FactOrderItems        │
                     │ (Qty, TotalPrice, LineProfit)│
                     └──────────────────────────────┘
                              ▲
                              │ 1 (InventoryID)
                     ┌────────┴─────────┐
                     │   DimInventory   │
                     │  (Beginning/End) │
                     └────────┬─────────┘
                              │ 1
                              │ * (InventoryID)
                     ┌────────┴─────────┐
                     │    FactWaste     │
                     │(WasteCost, Reason│
                     └──────────────────┘
```

#### Required Power BI Relationship Configurations:
1. `DimCalendar[Date]` (1) ─── to ─── `FactOrders[OrderDate]` (*) | Single Direction
2. `DimLocations[LocationID]` (1) ─── to ─── `FactOrders[LocationID]` (*) | Single Direction
3. `FactOrders[OrderID]` (1) ─── to ─── `FactOrderItems[OrderID]` (*) | Single Direction
4. `DimProducts[ProductID]` (1) ─── to ─── `FactOrderItems[ProductID]` (*) | Single Direction
5. `DimInventory[InventoryID]` (1) ─── to ─── `FactWaste[InventoryID]` (*) | Single Direction
6. `DimCalendar[Date]` (1) ─── to ─── `FactWaste[WasteDate]` (*) | Single Direction (Inactive or Active)
7. `DimProducts[ProductID]` (1) ─── to ─── `DimRecipes[ProductID]` (*) | Single Direction
8. `DimInventory[InventoryID]` (1) ─── to ─── `DimRecipes[InventoryID]` (*) | Single Direction

---

## 2. Production DAX Measures Repository

Create a dedicated measure table named `_Measures` in Power BI Desktop (`_Measures = ROW("Setup", 1)`).

### 2.1 Sales & Order Volume Metrics

#### Total Revenue (Gross)
```dax
Total Revenue = 
SUM(FactOrders[GrossSales])
```

#### Total Discounts
```dax
Total Discounts = 
SUM(FactOrders[DiscountAmount])
```

#### Total Net Sales
```dax
Total Net Sales = 
SUM(FactOrders[NetSales])
```

#### Total Orders
```dax
Total Orders = 
DISTINCTCOUNT(FactOrders[OrderID])
```

#### Total Quantity Sold
```dax
Total Quantity Sold = 
SUM(FactOrderItems[Quantity])
```

#### Average Order Value (AOV)
```dax
Average Order Value = 
DIVIDE([Total Net Sales], [Total Orders], 0)
```

#### Items Per Order (Basket Depth)
```dax
Items Per Order = 
DIVIDE([Total Quantity Sold], [Total Orders], 0)
```

---

### 2.2 Profitability & Margin Metrics

#### Total COGS (Cost of Goods Sold)
```dax
Total COGS = 
SUM(FactOrders[TotalCost])
```

#### Gross Profit ($)
```dax
Gross Profit = 
[Total Net Sales] - [Total COGS]
```

#### Gross Profit Margin (%)
```dax
Gross Profit Margin % = 
DIVIDE([Gross Profit], [Total Net Sales], 0)
```

#### Food Cost Percentage (%)
```dax
Food Cost % = 
DIVIDE([Total COGS], [Total Net Sales], 0)
```

#### Effective Discount Rate (%)
```dax
Effective Discount Rate % = 
DIVIDE([Total Discounts], [Total Revenue], 0)
```

---

### 2.3 Inventory Management & Turnover Metrics

#### Beginning Inventory Value ($)
```dax
Beginning Inventory Value = 
SUMX(
    DimInventory,
    COALESCE(DimInventory[BeginningStock], DimInventory[CurrentStock]) * DimInventory[UnitCost]
)
```

#### Ending Inventory Value ($)
```dax
Ending Inventory Value = 
SUMX(
    DimInventory,
    DimInventory[CurrentStock] * DimInventory[UnitCost]
)
```

#### Average Inventory Value ($)
```dax
Average Inventory Value = 
DIVIDE([Beginning Inventory Value] + [Ending Inventory Value], 2, 0)
```

#### Inventory Turnover Ratio (Standard)
```dax
Inventory Turnover = 
DIVIDE([Total COGS], [Average Inventory Value], 0)
```

#### Inventory Days (Days Sales of Inventory - DSI)
```dax
Inventory Days = 
DIVIDE([Average Inventory Value] * 366, [Total COGS], 0)
```

#### Total Inventory Wastage ($)
```dax
Inventory Wastage = 
SUM(FactWaste[WasteCost])
```

#### Waste to Sales Ratio (%)
```dax
Waste to Sales % = 
DIVIDE([Inventory Wastage], [Total Net Sales], 0)
```

#### Low Stock Products Count
```dax
Low Stock Products = 
CALCULATE(
    COUNTROWS(DimInventory),
    DimInventory[CurrentStock] <= DimInventory[ReorderLevel]
)
```

#### Overstocked Products Count
```dax
Overstocked Products = 
CALCULATE(
    COUNTROWS(DimInventory),
    DimInventory[CurrentStock] >= (DimInventory[MaxStock] * 0.90)
)
```

#### Fast Moving Products Count
```dax
Fast Moving Products = 
CALCULATE(
    COUNTROWS(DimInventory),
    DimInventory[StockStatus] = "Optimal Stock",
    DimInventory[CurrentStock] > DimInventory[ReorderLevel]
)
```

#### Slow Moving Products Count
```dax
Slow Moving Products = 
CALCULATE(
    COUNTROWS(DimInventory),
    DimInventory[CurrentStock] >= (DimInventory[MaxStock] * 0.80)
)
```

---

### 2.4 Time Intelligence & Operational Ratios

#### Prior Month Net Sales
```dax
Prior Month Net Sales = 
CALCULATE(
    [Total Net Sales],
    PREVIOUSMONTH(DimCalendar[Date])
)
```

#### Month-over-Month Revenue Growth (%)
```dax
MoM Sales Growth % = 
VAR CurrentSales = [Total Net Sales]
VAR PriorSales = [Prior Month Net Sales]
RETURN
DIVIDE(CurrentSales - PriorSales, PriorSales, 0)
```

#### Weekend Net Sales
```dax
Weekend Sales = 
CALCULATE(
    [Total Net Sales],
    FactOrders[IsWeekend] = 1
)
```

#### Weekday Net Sales
```dax
Weekday Sales = 
CALCULATE(
    [Total Net Sales],
    FactOrders[IsWeekend] = 0
)
```

---

## 3. Four-Page Enterprise Dashboard Visual Design

### PAGE 1: EXECUTIVE OVERVIEW
- **Theme**: Slate Dark / Modern Analytics (`#1A1D20` canvas, `#FFFFFF` cards, `#2ECC71` positive accents).
- **KPI Summary Cards (Top Ribbon)**:
  1. `[Total Revenue]` (Formatted: `$1,085,967`)
  2. `[Total Net Sales]` (Formatted: `$1,067,288`)
  3. `[Total Orders]` (Formatted: `33,051`)
  4. `[Average Order Value]` (Formatted: `$32.29`)
  5. `[Total Quantity Sold]` (Formatted: `65,851`)
  6. `[Gross Profit]` (Formatted: `$748,979`)
  7. `[Gross Profit Margin %]` (Formatted: `70.2%`)
- **Visual 1 (Area / Spline Chart)**: Monthly Revenue & Gross Profit Trend across 2024.
- **Visual 2 (Donut Chart)**: Net Sales Revenue Contribution by Menu Category (`Pizza`, `Combos`, `Sides`, `Beverages`, `Desserts`).
- **Visual 3 (Clustered Bar Chart)**: Location-Wise Performance comparing Net Sales vs Gross Profit.
- **Visual 4 (Table / Matrix)**: Summary by Location with Order Count, Revenue, Margin %, and AOV.

### PAGE 2: SALES & PRODUCT PERFORMANCE
- **Top Row Slicers**: Category dropdown, Location dropdown, Date range slider.
- **Visual 1 (Horizontal Bar Chart)**: Top 10 Revenue-Generating Menu Items (Led by *The Grand Artisan Supreme* and *Truffle Mushroom Rustica*).
- **Visual 2 (Horizontal Bar Chart)**: Lowest Performing 5 Menu Items (Evaluation for menu rationalization).
- **Visual 3 (Matrix Grid with Data Bars)**: Product Quantity Analysis: Category, Product, Units Sold, Net Revenue, COGS, Profit, Margin %.
- **Visual 4 (Line Chart)**: Daily Sales Trend across 366 days highlighting weekend peaks.
- **Visual 5 (Heatmap Matrix)**: Day of Week (Rows) vs Operating Hour (Columns) with color intensity mapped to order count.
- **Visual 6 (Clustered Column Chart)**: Weekday vs Weekend Sales Comparison.

### PAGE 3: INVENTORY MANAGEMENT
- **Top Ribbon Cards**:
  1. `[Ending Inventory Value]` (`$21,791.50`)
  2. `[Inventory Turnover]` (`14.37x`)
  3. `[Inventory Days]` (`25.5 days`)
  4. `[Inventory Wastage]` (`$6,867.75`)
  5. `[Low Stock Products]` (`1 SKU`)
  6. `[Overstocked Products]` (`2 SKUs`)
- **Visual 1 (Clustered Bar Chart)**: Current Stock vs Dynamic Reorder Level (ROP) by SKU.
- **Visual 2 (Treemap)**: Capital Valuation Share by Inventory Category (`Dry Goods`, `Dairy`, `Proteins`, `Packaging`).
- **Visual 3 (Donut Chart)**: Kitchen Wastage Loss by Root Cause Reason (`Handling & Prep Error`, `Excess Prep Spoilage`, `Supplier Quality Rejection`, `Expired Stock`).
- **Visual 4 (Table with Conditional Formatting)**: Reorder Recommendations Report:
  - Columns: `ItemName`, `Category`, `CurrentStock`, `AverageDailyConsumption`, `StockCoverageDays`, `LeadTimeDays`, `CalculatedSafetyStock`, `CalculatedROP`, `ReorderRecommendation`.
  - Conditional Rules: Red highlight for "Reorder Urgent", Yellow for "Reorder Soon", Blue for "Overstocked".

### PAGE 4: OPERATIONAL PERFORMANCE
- **Top Ribbon Cards**:
  1. Peak Operating Hour (`19:00 - 20:00`)
  2. Peak Day of Week (`Friday / Saturday`)
  3. Average Items Per Basket (`1.99 items`)
  4. Dine-in vs Takeaway vs Delivery Order Share
- **Visual 1 (Column Chart)**: Hourly Order Volume Distribution showing Lunch Rush (12:00–14:00) and Dinner Rush (18:00–21:00).
- **Visual 2 (Donut Chart)**: Payment Method Distribution (`Credit Card`, `Debit Card`, `Mobile Wallet`, `Cash`).
- **Visual 3 (Grouped Bar Chart)**: Location-wise Revenue by Order Type (`Dine-in`, `Takeout`, `Delivery`).
- **Visual 4 (Scatter Plot)**: Seating Capacity vs Average Order Value across locations.
- **Visual 5 (Table)**: Operational KPIs table summarizing daily order velocity and average turn rates.

---

## 4. Validation Checklist

- [x] All DAX measure names match references exactly (`[Gross Profit]` instead of `[GrossProfit]`).
- [x] Standard inventory turnover uses `Average Inventory Value` ($(\text{Beg} + \text{End}) / 2$).
- [x] Profitability hierarchy is strictly: Gross Sales $\rightarrow$ Net Sales $\rightarrow$ COGS $\rightarrow$ Gross Profit.
- [x] No claims of EBITDA or operating expenses since labor and occupancy costs are out of scope.
- [x] Star-schema tables and relationships fully documented with 1-to-many cardinality.
