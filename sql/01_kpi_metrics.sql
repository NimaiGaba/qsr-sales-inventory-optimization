/*
  QSR Sales KPI Metrics & Forecasting
  Objective: Extract critical sales and operational metrics
*/

-- 1. Total Gross Merchandise Value (GMV)
SELECT 
    SUM(total_price) AS GMV 
FROM order_details;

-- 2. Average Order Value (AOV)
SELECT 
    (SUM(total_price) / COUNT(DISTINCT order_id)) AS Average_Order_Value
FROM order_details;

-- 3. Total Items Sold
SELECT 
    SUM(quantity) AS Total_Items_Sold 
FROM order_details;

-- 4. Hourly Trend for Order Volume (Peak Hour Identification)
SELECT 
    DATEPART(HOUR, order_time) AS Order_Hour, 
    COUNT(DISTINCT order_id) AS Total_Orders
FROM orders
GROUP BY DATEPART(HOUR, order_time)
ORDER BY Order_Hour;

-- 5. Pareto Analysis: Revenue contribution by Category
WITH CategorySales AS (
    SELECT 
        menu_category, 
        SUM(total_price) AS Total_Sales
    FROM order_details
    GROUP BY menu_category
)
SELECT 
    menu_category, 
    Total_Sales,
    Total_Sales * 100.0 / (SELECT SUM(total_price) FROM order_details) AS PCT_Contribution
FROM CategorySales
ORDER BY Total_Sales DESC;

-- 6. Top 5 Best Sellers by Quantity
SELECT TOP 5
    item_name, 
    SUM(quantity) AS Total_Quantity
FROM order_details
GROUP BY item_name
ORDER BY Total_Quantity DESC;
