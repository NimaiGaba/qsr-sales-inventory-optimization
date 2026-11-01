-- ============================================================================
-- 02: SALES PERFORMANCE ANALYSIS
-- ============================================================================
-- Database: SQLite / ANSI SQL (qsr_analytics.db)
-- Primary Tables: orders, order_details, locations, products
-- ============================================================================

-- B1. Monthly Sales Trend with Month-over-Month (MoM) Growth Rate
WITH MonthlySummary AS (
    SELECT 
        OrderYear,
        OrderMonth,
        OrderMonthName,
        COUNT(DISTINCT OrderID) AS Monthly_Orders,
        ROUND(SUM(NetSales), 2) AS Monthly_Revenue,
        ROUND(AVG(NetSales), 2) AS Monthly_AOV
    FROM orders
    GROUP BY OrderYear, OrderMonth, OrderMonthName
)
SELECT 
    OrderYear,
    OrderMonth,
    OrderMonthName,
    Monthly_Orders,
    Monthly_Revenue,
    Monthly_AOV,
    LAG(Monthly_Revenue, 1) OVER (ORDER BY OrderMonth) AS Prior_Month_Revenue,
    ROUND(
        (Monthly_Revenue - LAG(Monthly_Revenue, 1) OVER (ORDER BY OrderMonth)) * 100.0 /
        LAG(Monthly_Revenue, 1) OVER (ORDER BY OrderMonth), 
        2
    ) AS MoM_Growth_PCT
FROM MonthlySummary
ORDER BY OrderMonth;

-- B2. Quarterly Sales Breakdown
SELECT 
    OrderQuarter,
    COUNT(DISTINCT OrderID) AS Total_Orders,
    ROUND(SUM(NetSales), 2) AS Total_Revenue,
    ROUND(AVG(NetSales), 2) AS Quarterly_AOV,
    ROUND(SUM(GrossProfit), 2) AS Quarterly_Gross_Profit,
    ROUND(SUM(GrossProfit) * 100.0 / SUM(NetSales), 2) AS Margin_PCT
FROM orders
GROUP BY OrderQuarter
ORDER BY OrderQuarter;

-- B3. Revenue by Restaurant Location & Seating Format
SELECT 
    l.LocationID,
    l.LocationName,
    l.District,
    l.StoreType,
    l.SeatingCapacity,
    COUNT(DISTINCT o.OrderID) AS Order_Count,
    ROUND(SUM(o.NetSales), 2) AS Location_Revenue,
    ROUND(SUM(o.NetSales) * 100.0 / (SELECT SUM(NetSales) FROM orders), 2) AS Revenue_Share_PCT,
    ROUND(AVG(o.NetSales), 2) AS Location_AOV,
    ROUND(SUM(o.GrossProfit), 2) AS Location_Gross_Profit
FROM orders o
JOIN locations l ON o.LocationID = l.LocationID
GROUP BY l.LocationID, l.LocationName, l.District, l.StoreType, l.SeatingCapacity
ORDER BY Location_Revenue DESC;

-- B4. Sales by Order Type (Dine-In, Takeout, Delivery, Drive-Thru)
SELECT 
    OrderType,
    COUNT(DISTINCT OrderID) AS Total_Orders,
    ROUND(COUNT(DISTINCT OrderID) * 100.0 / (SELECT COUNT(*) FROM orders), 2) AS Order_Volume_Share_PCT,
    ROUND(SUM(NetSales), 2) AS Total_Revenue,
    ROUND(SUM(NetSales) * 100.0 / (SELECT SUM(NetSales) FROM orders), 2) AS Revenue_Share_PCT,
    ROUND(AVG(NetSales), 2) AS Average_Order_Value
FROM orders
GROUP BY OrderType
ORDER BY Total_Revenue DESC;

-- B5. Payment Method Contribution and Preference
SELECT 
    PaymentMethod,
    COUNT(DISTINCT OrderID) AS Transaction_Count,
    ROUND(COUNT(DISTINCT OrderID) * 100.0 / (SELECT COUNT(*) FROM orders), 2) AS Transaction_Share_PCT,
    ROUND(SUM(NetSales), 2) AS Settled_Revenue,
    ROUND(AVG(NetSales), 2) AS AOV_by_Payment_Method
FROM orders
GROUP BY PaymentMethod
ORDER BY Settled_Revenue DESC;

-- B6. Promotional Discount Impact Analysis
SELECT 
    CASE 
        WHEN DiscountAmount > 0 THEN 'Discounted Order'
        ELSE 'Full Price Order'
    END AS Discount_Status,
    COUNT(DISTINCT OrderID) AS Order_Count,
    ROUND(SUM(GrossSales), 2) AS Gross_Sales,
    ROUND(SUM(DiscountAmount), 2) AS Total_Discount_Given,
    ROUND(SUM(NetSales), 2) AS Realized_Net_Sales,
    ROUND(AVG(GrossSales), 2) AS Avg_Gross_Basket,
    ROUND(AVG(NetSales), 2) AS Avg_Net_Basket,
    ROUND(SUM(GrossProfit), 2) AS Realized_Profit,
    ROUND(SUM(GrossProfit) * 100.0 / SUM(NetSales), 2) AS Profit_Margin_PCT
FROM orders
GROUP BY Discount_Status;
