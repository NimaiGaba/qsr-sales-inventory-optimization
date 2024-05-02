# QSR Sales & Inventory Optimization

## 📌 Executive Summary
This analytics project dives into the daily transactional data of "Artisan Crust Co.", a high-volume Quick-Service Restaurant (QSR). The primary objective was to extract key sales KPIs, validate data integrity, and visualize performance trends to help restaurant management optimize staffing and inventory levels during peak hours.

## 🛠 Tech Stack & Architecture
- **Data Engineering:** SQL (Aggregations, Date/Time Parsing, Joins)
- **Data Visualization:** Power BI (DAX, Interactive Dashboards)
- **Business Logic:** Sales Forecasting, Inventory Depletion Rates

## 📊 Key Business Findings
- **Gross Merchandise Value (GMV):** Generated $817,860 over a 12-month period across 48,000+ orders.
- **Average Order Value (AOV):** Maintained an AOV of $16.75, which spiked to $19.20 on weekends due to family bundle purchases.
- **Peak Hour Utilization:** Peak order volume consistently occurred between 12:00 PM – 1:30 PM (Lunch Rush) and 5:30 PM - 7:30 PM (Dinner Rush), accounting for 62% of total daily revenue.
- **Pareto Principle (80/20 Rule):** The top 3 signature items (out of 32 total menu items) drove 24% of the total GMV.

## 💡 Strategic Recommendations
1. Adjust mid-day kitchen staffing and prep schedules to ensure the top 3 best-selling items are prepped by 11:30 AM to reduce fulfillment bottlenecks.
2. Introduce a targeted up-sell on weekday lunch orders to push the AOV closer to the weekend benchmark of $19.20.

## 📁 Repository Structure
- `/sql/`: Queries for aggregating sales metrics and calculating AOV/GMV
- `/dashboard/`: Power BI .pbix file and screenshots
