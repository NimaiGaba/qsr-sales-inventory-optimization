-- ============================================================================
-- 04: TIME-BASED OPERATIONAL SALES ANALYSIS
-- ============================================================================
-- Database: SQLite / ANSI SQL (qsr_analytics.db)
-- Primary Tables: orders, order_details
-- Objective: Hourly rush patterns, meal periods, and weekday/weekend dynamics.
-- ============================================================================

-- D1. Hourly Sales Trend & Rush Hour Identification
SELECT 
    OrderHour,
    COUNT(DISTINCT OrderID) AS Total_Orders,
    ROUND(COUNT(DISTINCT OrderID) * 100.0 / (SELECT COUNT(*) FROM orders), 2) AS Order_Volume_Share_PCT,
    ROUND(SUM(NetSales), 2) AS Total_Hourly_Revenue,
    ROUND(AVG(NetSales), 2) AS Hourly_AOV,
    CASE 
        WHEN OrderHour IN (12, 13) THEN 'Lunch Peak Rush'
        WHEN OrderHour IN (18, 19) THEN 'Dinner Peak Rush'
        WHEN OrderHour BETWEEN 14 AND 16 THEN 'Afternoon Lull'
        ELSE 'Regular Hours'
    END AS Operational_Period
FROM orders
GROUP BY OrderHour
ORDER BY OrderHour;

-- D2. Meal Period (Day-Part) Performance Summary
SELECT 
    MealPeriod,
    COUNT(DISTINCT OrderID) AS Total_Orders,
    ROUND(COUNT(DISTINCT OrderID) * 100.0 / (SELECT COUNT(*) FROM orders), 2) AS Order_Volume_Share_PCT,
    ROUND(SUM(NetSales), 2) AS Total_Revenue,
    ROUND(SUM(NetSales) * 100.0 / (SELECT SUM(NetSales) FROM orders), 2) AS Revenue_Share_PCT,
    ROUND(AVG(NetSales), 2) AS MealPeriod_AOV,
    ROUND(SUM(GrossProfit), 2) AS MealPeriod_Gross_Profit,
    ROUND(SUM(GrossProfit) * 100.0 / SUM(NetSales), 2) AS Margin_PCT
FROM orders
GROUP BY MealPeriod
ORDER BY Total_Revenue DESC;

-- D3. Day of Week Sales Performance Ranking
SELECT 
    DayOfWeek,
    DayName,
    COUNT(DISTINCT OrderID) AS Total_Orders,
    ROUND(SUM(NetSales), 2) AS Day_Revenue,
    ROUND(AVG(NetSales), 2) AS Day_AOV,
    ROUND(SUM(NetSales) * 100.0 / (SELECT SUM(NetSales) FROM orders), 2) AS Revenue_Share_PCT,
    RANK() OVER (ORDER BY SUM(NetSales) DESC) AS Revenue_Rank
FROM orders
GROUP BY DayOfWeek, DayName
ORDER BY DayOfWeek;

-- D4. Weekday vs Weekend Operational Comparison
SELECT 
    CASE WHEN IsWeekend = 1 THEN 'Weekend (Fri-Sun)' ELSE 'Weekday (Mon-Thu)' END AS Day_Type,
    COUNT(DISTINCT OrderDate) AS Number_of_Days,
    COUNT(DISTINCT OrderID) AS Total_Orders,
    ROUND(COUNT(DISTINCT OrderID) * 1.0 / COUNT(DISTINCT OrderDate), 1) AS Avg_Orders_Per_Day,
    ROUND(SUM(NetSales), 2) AS Total_Revenue,
    ROUND(SUM(NetSales) * 1.0 / COUNT(DISTINCT OrderDate), 2) AS Avg_Revenue_Per_Day,
    ROUND(AVG(NetSales), 2) AS Average_Order_Value
FROM orders
GROUP BY IsWeekend;

-- D5. Busiest Operating Days in the Entire Year (Top 10 High-Volume Dates)
SELECT 
    OrderDate,
    DayName,
    COUNT(DISTINCT OrderID) AS Total_Orders,
    ROUND(SUM(NetSales), 2) AS Daily_Net_Revenue,
    ROUND(AVG(NetSales), 2) AS Daily_AOV,
    ROUND(SUM(GrossProfit), 2) AS Daily_Gross_Profit
FROM orders
GROUP BY OrderDate, DayName
ORDER BY Daily_Net_Revenue DESC
LIMIT 10;
