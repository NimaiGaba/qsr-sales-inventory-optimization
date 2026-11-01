-- ============================================================================
-- 06: PROFITABILITY & MARGIN OPTIMIZATION
-- ============================================================================
-- Database: SQLite / ANSI SQL (qsr_analytics.db)
-- Primary Tables: orders, order_details, products, locations
-- Objective: Detailed COGS analysis, margins by item, category, and location.
-- ============================================================================

-- F1. Enterprise Profit & Loss Bridge
SELECT 
    ROUND(SUM(GrossSales), 2) AS Gross_Revenue,
    ROUND(SUM(DiscountAmount), 2) AS Total_Discounts,
    ROUND(SUM(NetSales), 2) AS Net_Revenue,
    ROUND(SUM(TotalCost), 2) AS Cost_of_Goods_Sold_COGS,
    ROUND(SUM(TotalCost) * 100.0 / SUM(NetSales), 2) AS Food_Cost_PCT,
    ROUND(SUM(GrossProfit), 2) AS Gross_Profit,
    ROUND(SUM(GrossProfit) * 100.0 / SUM(NetSales), 2) AS Gross_Margin_PCT
FROM orders;

-- F2. Top 10 Most Profitable Menu Items (by Total Gross Profit Dollars)
SELECT 
    od.ProductID,
    od.ProductName,
    od.Category,
    SUM(od.Quantity) AS Units_Sold,
    ROUND(AVG(od.UnitPrice), 2) AS Avg_Retail_Price,
    ROUND(SUM(od.TotalPrice), 2) AS Net_Revenue,
    ROUND(SUM(od.LineCost), 2) AS Total_COGS,
    ROUND(SUM(od.LineProfit), 2) AS Total_Gross_Profit,
    ROUND(SUM(od.LineProfit) * 100.0 / SUM(od.TotalPrice), 2) AS Gross_Margin_PCT,
    ROUND(SUM(od.LineProfit) * 100.0 / (SELECT SUM(LineProfit) FROM order_details), 2) AS Profit_Contribution_PCT
FROM order_details od
GROUP BY od.ProductID, od.ProductName, od.Category
ORDER BY Total_Gross_Profit DESC
LIMIT 10;

-- F3. Menu Items by Margin Efficiency (Highest Margin Percentage)
SELECT 
    od.ProductID,
    od.ProductName,
    od.Category,
    ROUND(AVG(od.UnitPrice), 2) AS Price,
    ROUND(AVG(od.LineCost / od.Quantity), 2) AS UnitCost,
    ROUND(SUM(od.LineProfit) * 100.0 / SUM(od.TotalPrice), 2) AS Gross_Margin_PCT,
    SUM(od.Quantity) AS Units_Sold,
    ROUND(SUM(od.LineProfit), 2) AS Total_Gross_Profit
FROM order_details od
GROUP BY od.ProductID, od.ProductName, od.Category
HAVING SUM(od.Quantity) >= 500
ORDER BY Gross_Margin_PCT DESC
LIMIT 10;

-- F4. Category Profitability and Food Cost Comparison
SELECT 
    Category,
    ROUND(SUM(TotalPrice), 2) AS Category_Revenue,
    ROUND(SUM(LineCost), 2) AS Category_COGS,
    ROUND(SUM(LineCost) * 100.0 / SUM(TotalPrice), 2) AS Food_Cost_PCT,
    ROUND(SUM(LineProfit), 2) AS Category_Gross_Profit,
    ROUND(SUM(LineProfit) * 100.0 / SUM(TotalPrice), 2) AS Gross_Margin_PCT,
    ROUND(SUM(LineProfit) * 100.0 / (SELECT SUM(LineProfit) FROM order_details), 2) AS Share_of_Chain_Profit_PCT
FROM order_details
GROUP BY Category
ORDER BY Category_Gross_Profit DESC;

-- F5. Profitability & Margin Performance by Restaurant Location
SELECT 
    l.LocationID,
    l.LocationName,
    l.StoreType,
    COUNT(DISTINCT o.OrderID) AS Order_Count,
    ROUND(SUM(o.NetSales), 2) AS Net_Revenue,
    ROUND(SUM(o.TotalCost), 2) AS Location_COGS,
    ROUND(SUM(o.GrossProfit), 2) AS Gross_Profit,
    ROUND(SUM(o.GrossProfit) * 100.0 / SUM(o.NetSales), 2) AS Gross_Margin_PCT,
    ROUND(AVG(o.GrossProfit), 2) AS Avg_Profit_Per_Order
FROM orders o
JOIN locations l ON o.LocationID = l.LocationID
GROUP BY l.LocationID, l.LocationName, l.StoreType
ORDER BY Gross_Profit DESC;
