# Power BI Executive Dashboard Architecture & DAX Measures Guide

## 1. Executive Overview & Data Modeling

This document provides complete instructions, data modeling schemas, and enterprise DAX measure formulas for the **QSR Sales & Inventory Optimization Executive Dashboard** built for **Artisan Crust Co.**

### 1.1 Data Source Tables (`dashboard/exports/`)
- `FactOrders.csv`: Granular order header transactions (~33,000 records).
- `FactOrderItems.csv`: Order line items with quantity, unit prices, discounts, and margins (~66,000 records).
- `DimProducts.csv`: 32 menu items with categories, portion sizes, prices, and food costs.
- `DimLocations.csv`: 4 restaurant stores with district, seating capacity, and operating models.
- `DimInventory.csv`: 24 inventory SKUs with stock levels, reorder points, safety stock, and suppliers.
- `FactWaste.csv`: Daily kitchen waste logs with quantities, dollar cost impact, and reasons.
- `DimCalendar.csv`: Master date table with year, month, day-of-week, and weekend flags.

### 1.2 Enterprise Star Schema Data Model

```
                     ┌──────────────────┐
                     │   DimCalendar    │
                     │  (Date, DayName) │
                     └────────┬─────────┘
                              │ 1
                              │
                              │ * (OrderDate)
┌──────────────────┐          ▼          ┌──────────────────┐
│   DimLocations   │1 ────────*──────── 1│   DimProducts    │
│(LocationID, Type)│      FactOrders     │  (ProductID, Cat)│
└──────────────────┘     (NetSales, AOV) └────────┬─────────┘
                              │ 1                 │ 1
                              │                   │
                              │ * (OrderID)       │ * (ProductID)
                              ▼                   ▼
                     ┌──────────────────────────────┐
                     │        FactOrderItems        │
                     │ (Qty, TotalPrice, LineProfit)│
                     └──────────────────────────────┘
                              ▲
                              │ * (Date)
                     ┌────────┴─────────┐
                     │    FactWaste     │
                     │(WasteCost, Reason│
                     └──────────────────┘
```

---

## 2. Production DAX Measures Repository

Create a dedicated measure table named `_Measures` in Power BI Desktop.

### 2.1 Sales & Revenue Metrics

#### Total Gross Revenue
```dax
Total Gross Sales = 
SUM(FactOrders[GrossSales])
```

#### Total Promotional Discounts
```dax
Total Discounts = 
SUM(FactOrders[DiscountAmount])
```

#### Total Net Revenue
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
Total Units Sold = 
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
DIVIDE([Total Units Sold], [Total Orders], 0)
```

---

### 2.2 Profitability & Margin Metrics

#### Cost of Goods Sold (COGS)
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
DIVIDE([GrossProfit], [Total Net Sales], 0)
```

#### Food Cost Ratio (%)
```dax
Food Cost % = 
DIVIDE([Total COGS], [Total Net Sales], 0)
```

---

### 2.3 Time Intelligence & Growth Metrics

#### Prior Month Revenue (MoM)
```dax
Prior Month Revenue = 
CALCULATE(
    [Total Net Sales],
    PREVIOUSMONTH(DimCalendar[Date])
)
```

#### Month-over-Month Revenue Growth (%)
```dax
MoM Revenue Growth % = 
VAR CurrentRev = [Total Net Sales]
VAR PrevRev = [Prior Month Revenue]
RETURN
DIVIDE(CurrentRev - PrevRev, PrevRev, 0)
```

#### Weekend vs Weekday Revenue Ratio
```dax
Weekend Revenue = 
CALCULATE(
    [Total Net Sales],
    FactOrders[IsWeekend] = 1
)
```

```dax
Weekday Revenue = 
CALCULATE(
    [Total Net Sales],
    FactOrders[IsWeekend] = 0
)
```

---

### 2.4 Inventory Optimization & Wastage Metrics

#### Total Inventory Capital Valuation
```dax
Total Inventory Valuation = 
SUMX(
    DimInventory,
    DimInventory[CurrentStock] * DimInventory[UnitCost]
)
```

#### Inventory Turnover Ratio
```dax
Inventory Turnover = 
DIVIDE([Total COGS], [Total Inventory Valuation], 0)
```

#### Days of Inventory on Hand (Days of Supply)
```dax
Days of Supply = 
DIVIDE([Total Inventory Valuation] * 365, [Total COGS], 0)
```

#### Low Stock Alert SKUs Count
```dax
Low Stock SKU Count = 
CALCULATE(
    COUNTROWS(DimInventory),
    DimInventory[CurrentStock] <= DimInventory[ReorderLevel]
)
```

#### Total Wastage Cost
```dax
Total Waste Cost = 
SUM(FactWaste[WasteCost])
```

#### Wastage as % of Sales
```dax
Waste to Sales % = 
DIVIDE([Total Waste Cost], [Total Net Sales], 0)
```

---

## 3. 4-Page Dashboard Layout & Visual Specifications

### Page 1: Executive Sales Overview
- **Header KPI Cards**:
  1. `[Total Net Sales]` ($ Net Revenue)
  2. `[Total Orders]` (Order Volume)
  3. `[Average Order Value]` ($ AOV)
  4. `[Gross Profit Margin %]` (% Profitability)
  5. `[Total Units Sold]` (Menu Items)
- **Visual 1 (Area / Line Chart)**: Monthly Revenue Trend with 7-day rolling moving average.
- **Visual 2 (Donut Chart)**: Revenue Contribution by Menu Category (Pizza, Combos, Sides, Beverages, Desserts).
- **Visual 3 (Clustered Column Chart)**: Net Sales vs Gross Profit across the 4 Restaurant Locations.
- **Visual 4 (Table / Matrix)**: Location summary with Order Count, Revenue, AOV, and Margin %.

### Page 2: Product Performance & Pareto Insights
- **Visual 1 (Horizontal Bar Chart)**: Top 10 Revenue-Generating Menu Items.
- **Visual 2 (Horizontal Bar Chart)**: Top 10 Menu Items by Volume (Quantity Sold).
- **Visual 3 (Scatter / Bubble Plot)**: Product Portfolio Matrix — X: Units Sold, Y: Total Revenue, Bubble Size: Gross Margin %.
- **Visual 4 (Table with Data Bars)**: Bottom 5 Underperforming SKUs with Revenue, Units, and Trajectory.
- **Callout Card**: Pareto Insight — "Top 9 Menu Items generate 80% of total restaurant sales."

### Page 3: Inventory Management & Supply Chain Health
- **Header KPI Cards**:
  1. `[Total Inventory Valuation]` ($ Tied-Up Capital)
  2. `[Inventory Turnover]` (Annual Turnover Ratio)
  3. `[Low Stock SKU Count]` (Urgent Reorder Alerts)
  4. `[Total Waste Cost]` ($ Food Lost)
  5. `[Waste to Sales %]` (Shrinkage Rate)
- **Visual 1 (Clustered Bar Chart)**: Current Stock on Hand vs Dynamic Reorder Level (ROP).
- **Visual 2 (Treemap)**: Inventory Capital Allocation by Category (Dairy, Proteins, Dry Goods, Packaging).
- **Visual 3 (Stacked Bar Chart)**: Kitchen Food Wastage Dollar Impact by Root Cause Reason.
- **Visual 4 (Grid Table)**: Reorder Action Table with Recommended Order Quantities and Lead Times.

### Page 4: Operational & Time Performance
- **Visual 1 (Heatmap Matrix)**: Day of Week (Rows) vs Operating Hour 10am–10pm (Columns), Values: Order Volume.
- **Visual 2 (Grouped Column Chart)**: Meal Period Performance (Lunch Rush vs Dinner Rush vs Lull).
- **Visual 3 (Clustered Bar Chart)**: Average Order Value: Weekday ($16–$17) vs Weekend ($20–$22).
- **Visual 4 (Donut Chart)**: Settled Revenue Share by Payment Method (Credit Card, Mobile Wallet, Debit, Cash).

---

## 4. Implementation Steps in Power BI Desktop

1. Open Power BI Desktop.
2. Under **Home** > **Get Data**, choose **Folder** or **Text/CSV** and point to `dashboard/exports/`.
3. Set Relationships in the **Model View** matching the Star Schema above (1-to-many single direction).
4. Create calculated table `_Measures = ROW("Setup", 1)` and paste the DAX formulas.
5. Apply standard number formatting (`$#,##0` for currency, `0.0%` for percentages).
6. Build pages 1 to 4 using the specifications and publish/export `.pbix`.
