-- ============================================================================
-- 03: PRODUCT PERFORMANCE & PARETO ANALYSIS
-- ============================================================================
-- Database: SQLite / ANSI SQL (qsr_analytics.db)
-- Primary Tables: order_details, products, orders
-- ============================================================================

-- C1. Top 10 Revenue-Generating Menu Items
SELECT 
    od.ProductID,
    od.ProductName,
    od.Category,
    SUM(od.Quantity) AS Units_Sold,
    ROUND(AVG(od.UnitPrice), 2) AS Menu_Price,
    ROUND(SUM(od.TotalPrice), 2) AS Total_Revenue,
    ROUND(SUM(od.TotalPrice) * 100.0 / (SELECT SUM(TotalPrice) FROM order_details), 2) AS Revenue_Share_PCT,
    ROUND(SUM(od.LineProfit), 2) AS Gross_Profit_Contributed
FROM order_details od
GROUP BY od.ProductID, od.ProductName, od.Category
ORDER BY Total_Revenue DESC
LIMIT 10;

-- C2. Bottom 5 Lowest-Selling Products (Underperformers)
SELECT 
    od.ProductID,
    od.ProductName,
    od.Category,
    SUM(od.Quantity) AS Units_Sold,
    ROUND(SUM(od.TotalPrice), 2) AS Total_Revenue,
    ROUND(SUM(od.LineProfit), 2) AS Gross_Profit,
    ROUND(SUM(od.LineProfit) * 100.0 / SUM(od.TotalPrice), 2) AS Margin_PCT
FROM order_details od
GROUP BY od.ProductID, od.ProductName, od.Category
ORDER BY Total_Revenue ASC
LIMIT 5;

-- C3. Pareto 80/20 Cumulative Revenue Contribution by Product
WITH RankedProducts AS (
    SELECT 
        ProductID,
        ProductName,
        Category,
        SUM(TotalPrice) AS Product_Revenue,
        ROW_NUMBER() OVER (ORDER BY SUM(TotalPrice) DESC) AS Sales_Rank
    FROM order_details
    GROUP BY ProductID, ProductName, Category
),
CumulativeStats AS (
    SELECT 
        ProductID,
        ProductName,
        Category,
        Product_Revenue,
        Sales_Rank,
        SUM(Product_Revenue) OVER (ORDER BY Sales_Rank) AS Running_Total_Revenue,
        (SELECT SUM(TotalPrice) FROM order_details) AS Chain_Total_Revenue
    FROM RankedProducts
)
SELECT 
    Sales_Rank,
    ProductID,
    ProductName,
    Category,
    ROUND(Product_Revenue, 2) AS Item_Revenue,
    ROUND(Running_Total_Revenue, 2) AS Cumulative_Revenue,
    ROUND(Running_Total_Revenue * 100.0 / Chain_Total_Revenue, 2) AS Cumulative_Revenue_PCT,
    CASE 
        WHEN (Running_Total_Revenue * 100.0 / Chain_Total_Revenue) <= 80.0 THEN 'Core 80% Driver'
        ELSE 'Long-Tail 20%'
    END AS Pareto_Classification
FROM CumulativeStats
ORDER BY Sales_Rank;

-- C4. Category Mix: Item Counts, Units, Revenue, and Margin Comparison
SELECT 
    Category,
    COUNT(DISTINCT ProductID) AS Active_SKU_Count,
    SUM(Quantity) AS Total_Units_Sold,
    ROUND(SUM(TotalPrice), 2) AS Total_Revenue,
    ROUND(AVG(TotalPrice / Quantity), 2) AS Realized_Avg_Price,
    ROUND(SUM(LineCost), 2) AS Total_COGS,
    ROUND(SUM(LineProfit), 2) AS Total_Gross_Profit,
    ROUND(SUM(LineProfit) * 100.0 / SUM(TotalPrice), 2) AS Category_Gross_Margin_PCT
FROM order_details
GROUP BY Category
ORDER BY Total_Revenue DESC;

-- C5. Product Demand Split: Weekday vs Weekend Preference
SELECT 
    od.ProductName,
    od.Category,
    SUM(CASE WHEN o.IsWeekend = 0 THEN od.Quantity ELSE 0 END) AS Weekday_Units,
    SUM(CASE WHEN o.IsWeekend = 1 THEN od.Quantity ELSE 0 END) AS Weekend_Units,
    ROUND(SUM(CASE WHEN o.IsWeekend = 1 THEN od.Quantity ELSE 0 END) * 100.0 / SUM(od.Quantity), 1) AS Weekend_Demand_Share_PCT
FROM order_details od
JOIN orders o ON od.OrderID = o.OrderID
GROUP BY od.ProductName, od.Category
ORDER BY Weekend_Demand_Share_PCT DESC;

-- C6. H1 vs H2 Product Sales Trend (Identifying Growing vs Declining Items)
WITH HalfYearSales AS (
    SELECT 
        od.ProductID,
        od.ProductName,
        od.Category,
        SUM(CASE WHEN o.OrderMonth <= 6 THEN od.Quantity ELSE 0 END) AS H1_Units,
        SUM(CASE WHEN o.OrderMonth > 6 THEN od.Quantity ELSE 0 END) AS H2_Units,
        SUM(CASE WHEN o.OrderMonth <= 6 THEN od.TotalPrice ELSE 0 END) AS H1_Revenue,
        SUM(CASE WHEN o.OrderMonth > 6 THEN od.TotalPrice ELSE 0 END) AS H2_Revenue
    FROM order_details od
    JOIN orders o ON od.OrderID = o.OrderID
    GROUP BY od.ProductID, od.ProductName, od.Category
)
SELECT 
    ProductID,
    ProductName,
    Category,
    H1_Units,
    H2_Units,
    ROUND(H1_Revenue, 2) AS H1_Revenue,
    ROUND(H2_Revenue, 2) AS H2_Revenue,
    ROUND((H2_Revenue - H1_Revenue) * 100.0 / NULLIF(H1_Revenue, 0), 2) AS H2_vs_H1_Growth_PCT,
    CASE 
        WHEN H2_Revenue > H1_Revenue THEN 'Growing'
        WHEN H2_Revenue < H1_Revenue THEN 'Declining'
        ELSE 'Stable'
    END AS Trajectory
FROM HalfYearSales
ORDER BY H2_vs_H1_Growth_PCT ASC;
