-- ============================================================================
-- 01: EXECUTIVE KPI METRICS
-- ============================================================================
-- Database: SQLite / ANSI SQL (qsr_analytics.db)
-- Primary Tables: orders, order_details, inventory, inventory_waste
-- Objective: Compute primary business KPIs across sales, profitability, and stock.
-- ============================================================================

-- 1. High-Level Executive Sales & Profitability Summary
SELECT 
    COUNT(DISTINCT o.OrderID) AS Total_Orders,
    SUM(od.Quantity) AS Total_Items_Sold,
    ROUND(SUM(o.GrossSales), 2) AS Gross_Revenue,
    ROUND(SUM(o.DiscountAmount), 2) AS Total_Discounts,
    ROUND(SUM(o.NetSales), 2) AS Net_Revenue,
    ROUND(SUM(o.TotalCost), 2) AS Total_COGS,
    ROUND(SUM(o.GrossProfit), 2) AS Gross_Profit,
    ROUND((SUM(o.GrossProfit) * 100.0 / SUM(o.NetSales)), 2) AS Gross_Profit_Margin_PCT,
    ROUND(AVG(o.NetSales), 2) AS Average_Order_Value,
    ROUND(SUM(od.Quantity) * 1.0 / COUNT(DISTINCT o.OrderID), 2) AS Items_Per_Order
FROM orders o
JOIN order_details od ON o.OrderID = od.OrderID;

-- 2. Daily Average Sales Performance
WITH DailySales AS (
    SELECT 
        OrderDate,
        COUNT(DISTINCT OrderID) AS Daily_Orders,
        SUM(NetSales) AS Daily_Revenue
    FROM orders
    GROUP BY OrderDate
)
SELECT 
    COUNT(OrderDate) AS Operating_Days,
    ROUND(AVG(Daily_Orders), 1) AS Avg_Orders_Per_Day,
    ROUND(AVG(Daily_Revenue), 2) AS Avg_Revenue_Per_Day,
    ROUND(MIN(Daily_Revenue), 2) AS Min_Daily_Revenue,
    ROUND(MAX(Daily_Revenue), 2) AS Max_Daily_Revenue
FROM DailySales;

-- 3. Revenue Contribution by Menu Category
WITH CategoryMetrics AS (
    SELECT 
        Category,
        COUNT(OrderDetailID) AS Line_Items_Sold,
        SUM(Quantity) AS Total_Units_Sold,
        ROUND(SUM(TotalPrice), 2) AS Category_Revenue,
        ROUND(SUM(LineProfit), 2) AS Category_Profit
    FROM order_details
    GROUP BY Category
)
SELECT 
    Category,
    Line_Items_Sold,
    Total_Units_Sold,
    Category_Revenue,
    ROUND(Category_Revenue * 100.0 / (SELECT SUM(TotalPrice) FROM order_details), 2) AS Revenue_Contribution_PCT,
    Category_Profit,
    ROUND((Category_Profit * 100.0 / Category_Revenue), 2) AS Category_Margin_PCT
FROM CategoryMetrics
ORDER BY Category_Revenue DESC;

-- 4. Inventory Valuation & Stock Health KPIs
SELECT 
    COUNT(InventoryID) AS Total_Tracked_SKUs,
    ROUND(SUM(CurrentStock * UnitCost), 2) AS Total_Inventory_Valuation_USD,
    SUM(CASE WHEN CurrentStock <= ReorderLevel THEN 1 ELSE 0 END) AS Low_Stock_Alert_Items,
    SUM(CASE WHEN CurrentStock >= (MaxStock * 0.90) THEN 1 ELSE 0 END) AS Overstocked_Items,
    ROUND(AVG(CurrentStock * 1.0 / ReorderLevel), 2) AS Avg_Stock_to_Reorder_Ratio
FROM inventory;

-- 5. Inventory Wastage KPI Summary
SELECT 
    COUNT(WasteID) AS Total_Waste_Incidents,
    ROUND(SUM(QuantityWasted), 1) AS Total_Quantity_Wasted,
    ROUND(SUM(WasteCost), 2) AS Total_Waste_Cost_USD,
    ROUND(SUM(WasteCost) * 100.0 / (SELECT SUM(NetSales) FROM orders), 3) AS Waste_to_Revenue_PCT
FROM inventory_waste;

-- 6. Top 5 Best-Selling Signature Products by Volume
SELECT 
    ProductName,
    Category,
    SUM(Quantity) AS Total_Units_Sold,
    ROUND(SUM(TotalPrice), 2) AS Total_Revenue,
    ROUND(SUM(LineProfit), 2) AS Total_Profit
FROM order_details
GROUP BY ProductName, Category
ORDER BY Total_Units_Sold DESC
LIMIT 5;
