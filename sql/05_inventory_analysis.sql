-- ============================================================================
-- 05: INVENTORY & SUPPLY CHAIN OPTIMIZATION
-- ============================================================================
-- Database: SQLite / ANSI SQL (qsr_analytics.db)
-- Primary Tables: inventory, suppliers, inventory_waste, orders
-- ============================================================================

-- E1. Inventory Stock Levels, Reorder Status, and Current Valuation
SELECT 
    i.InventoryID,
    i.ItemName,
    i.Category,
    i.CurrentStock,
    i.Unit,
    i.ReorderLevel,
    i.SafetyStock,
    i.MaxStock,
    ROUND(i.UnitCost, 2) AS UnitCost,
    ROUND(i.CurrentStock * i.UnitCost, 2) AS Inventory_Valuation_USD,
    CASE 
        WHEN i.CurrentStock <= i.ReorderLevel THEN 'CRITICAL: Reorder Immediately'
        WHEN i.CurrentStock >= (i.MaxStock * 0.90) THEN 'WARNING: Overstocked'
        ELSE 'Healthy Stock'
    END AS Replenishment_Action,
    s.SupplierName,
    s.LeadTimeDays
FROM inventory i
LEFT JOIN suppliers s ON i.SupplierID = s.SupplierID
ORDER BY (i.CurrentStock * 1.0 / NULLIF(i.ReorderLevel, 0)) ASC;

-- E2. Category-Wise Inventory Capital Allocation
SELECT 
    Category,
    COUNT(InventoryID) AS SKU_Count,
    ROUND(SUM(CurrentStock * UnitCost), 2) AS Category_Inventory_Valuation,
    ROUND(SUM(CurrentStock * UnitCost) * 100.0 / (SELECT SUM(CurrentStock * UnitCost) FROM inventory), 2) AS Capital_Share_PCT,
    SUM(CASE WHEN CurrentStock <= ReorderLevel THEN 1 ELSE 0 END) AS Low_Stock_SKUs,
    SUM(CASE WHEN CurrentStock >= (MaxStock * 0.90) THEN 1 ELSE 0 END) AS Overstocked_SKUs
FROM inventory
GROUP BY Category
ORDER BY Category_Inventory_Valuation DESC;

-- E3. Kitchen Wastage Breakdown by Reason
SELECT 
    Reason,
    COUNT(WasteID) AS Incident_Count,
    ROUND(SUM(QuantityWasted), 1) AS Total_Units_Lost,
    ROUND(SUM(WasteCost), 2) AS Total_Waste_Cost_USD,
    ROUND(SUM(WasteCost) * 100.0 / (SELECT SUM(WasteCost) FROM inventory_waste), 2) AS Waste_Cost_Share_PCT,
    ROUND(AVG(WasteCost), 2) AS Avg_Cost_Per_Incident
FROM inventory_waste
GROUP BY Reason
ORDER BY Total_Waste_Cost_USD DESC;

-- E4. Wastage Cost by Inventory Category & Item
SELECT 
    w.Category,
    w.ItemName,
    COUNT(w.WasteID) AS Waste_Incidents,
    ROUND(SUM(w.QuantityWasted), 1) AS Total_Quantity_Lost,
    w.Unit,
    ROUND(SUM(w.WasteCost), 2) AS Total_Cost_Lost_USD,
    ROUND(SUM(w.WasteCost) * 100.0 / (SELECT SUM(WasteCost) FROM inventory_waste), 2) AS Share_of_Total_Waste_PCT
FROM inventory_waste w
GROUP BY w.Category, w.ItemName, w.Unit
ORDER BY Total_Cost_Lost_USD DESC
LIMIT 10;

-- E5. Supplier Performance & Reliability Ranking
SELECT 
    s.SupplierID,
    s.SupplierName,
    s.CategorySupplied,
    s.LeadTimeDays,
    ROUND(s.ReliabilityScore * 100, 1) AS Reliability_Score_PCT,
    COUNT(i.InventoryID) AS Managed_SKU_Count,
    ROUND(SUM(i.CurrentStock * i.UnitCost), 2) AS Value_Under_Management_USD
FROM suppliers s
LEFT JOIN inventory i ON s.SupplierID = i.SupplierID
GROUP BY s.SupplierID, s.SupplierName, s.CategorySupplied, s.LeadTimeDays, s.ReliabilityScore
ORDER BY Value_Under_Management_USD DESC;

-- E6. Recommended Reorder Purchase Quantities
-- Reorder Quantity = (MaxStock - CurrentStock)
SELECT 
    InventoryID,
    ItemName,
    Category,
    CurrentStock,
    ReorderLevel,
    MaxStock,
    Unit,
    (MaxStock - CurrentStock) AS Recommended_Reorder_Qty,
    ROUND((MaxStock - CurrentStock) * UnitCost, 2) AS Estimated_Purchase_Cost_USD
FROM inventory
WHERE CurrentStock <= ReorderLevel
ORDER BY Estimated_Purchase_Cost_USD DESC;
