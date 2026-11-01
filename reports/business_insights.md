# QSR Sales & Inventory Optimization — Executive Business Insights Report

**Company:** Artisan Crust Co.  
**Analysis Period:** Full Year 2024 (January 1, 2024 – December 31, 2024)  
**Total Orders Analyzed:** 33,051 Orders across 4 Locations  
**Total Line Items:** 65,851 Menu Items Sold  
**Analytics Engine:** SQL, Python (Pandas/NumPy), Power BI Star Schema  

---

## 1. Executive Summary & Macro Financial Performance

| Metric | Measured Value | Operational Benchmark / Context |
|:---|:---:|:---|
| **Gross Merchandise Value (Gross Sales)** | **$1,085,821.50** | Pre-discount transactional volume |
| **Promotional Discounts Awarded** | **$18,533.48** | 1.71% effective discount rate |
| **Net Sales (Net Revenue)** | **$1,067,288.02** | Realized net operating revenue |
| **Cost of Goods Sold (COGS)** | **$318,309.00** | **29.82% food cost** (healthy QSR benchmark: 28–32%) |
| **Gross Profit** | **$748,979.02** | **70.18% gross margin** |
| **Total Orders Fulfilled** | **33,051** | ~90.3 orders/day chain-wide |
| **Average Order Value (AOV)** | **$32.29** | Spikes to $34.50+ on weekends |
| **Total Inventory Valuation on Hand** | **$21,791.50** | Across 24 tracked food & packaging SKUs |
| **Annual Inventory Turnover Ratio** | **14.61x** | Healthy stock turns every ~25.0 days |
| **Annual Food Wastage Dollar Loss** | **$25,202.93** | 2.36% of net sales (Target: < 2.0%) |

---

## 2. Answers to the 12 Core Business Questions

### Question 1: Which products generate the highest revenue?
- **Finding:** **Pepperoni Feast** is the single largest revenue driver, generating **$197,134.07** (18.47% of total restaurant sales).
- **Supporting Metric:** The top 3 menu items are:
  1. *Pepperoni Feast:* $197,134.07 (10,911 units sold)
  2. *BBQ Chicken Supreme:* $112,398.98 (6,014 units sold)
  3. *Margherita Classic:* $108,772.30 (7,219 units sold)
- **Business Impact:** These 3 signature pizzas collectively generate **$418,305.35** (39.19% of total company revenue).
- **Recommended Action:** Ensure zero ingredient stockouts for mozzarella, cured pepperoni, and sous-vide chicken. Secure volume purchase rebates with Supplier `SUP-03` (Prime Meats).

---

### Question 2: Which categories contribute the most to sales?
- **Finding:** **Pizza** and **Combos** account for over **83.9%** of chain revenue.
- **Supporting Metric:**
  - **Pizza:** $634,522.60 (59.45% share)
  - **Combos / Bundles:** $261,357.16 (24.49% share)
  - **Sides:** $100,264.44 (9.39% share)
  - **Beverages:** $38,420.42 (3.60% share)
  - **Desserts:** $32,723.40 (3.07% share)
- **Business Impact:** While Pizza is the brand's core, Combos achieve significantly higher basket sizes ($42.99–$64.99). Conversely, Beverage and Dessert attach rates are underperforming at less than 4% each.
- **Recommended Action:** Implement automated POS prompts for drink/dessert add-ons ($2.50–$4.50) on single-pizza orders to capture incremental high-margin margin revenue.

---

### Question 3: When does the restaurant experience peak demand?
- **Finding:** Operations exhibit a classic bi-modal demand curve with sharp lunch and dinner peaks.
- **Supporting Metric:**
  - **Lunch Rush (12:00 PM – 2:00 PM):** 9,932 orders placed (30.05% of daily volume). Peak hour is **12:00 PM** (5,300 orders).
  - **Dinner Rush (6:00 PM – 8:00 PM):** 8,240 orders placed (24.93% of daily volume). Peak hour is **6:00 PM** (4,982 orders).
  - **Afternoon Lull (2:00 PM – 4:00 PM):** Drops to under 1,900 orders/hr.
- **Business Impact:** Kitchen throughput bottlenecks during the 12:00–1:30 PM window lead to order delays and delivery wait-time friction.
- **Recommended Action:** Stagger prep shifts so that dough rolling and cheese pre-portioning are 100% completed by 11:30 AM and 5:00 PM.

---

### Question 4: Which weekdays generate the most revenue?
- **Finding:** Weekend demand (Friday, Saturday, Sunday) heavily outpaces weekday demand.
- **Supporting Metric:**
  - **Sunday:** $201,000.75 (18.83% of annual sales)
  - **Saturday:** $199,691.52 (18.71% of annual sales)
  - **Friday:** $193,597.33 (18.14% of annual sales)
  - **Monday–Thursday Average:** ~$118,200 per day over the year (~$2,270/day per location vs ~$3,850/day on weekends).
- **Business Impact:** Over **55.68% of total annual revenue** is compressed into 3 days (Friday–Sunday).
- **Recommended Action:** Allocate 65% of variable part-time kitchen and front-of-house labor to Friday–Sunday shifts. Implement a "Midweek Lunch Club" loyalty discount on Tuesdays and Wednesdays to lift weekday kitchen utilization.

---

### Question 5: Which products sell slowly?
- **Finding:** Niche beverages and standalone single desserts demonstrate sluggish turnover.
- **Supporting Metric:**
  - *Organic Craft Kombucha:* $3,277.75 (690 units sold)
  - *Sparkling Mineral Water:* $3,366.85 (1,347 units sold)
  - *Cinnamon Sugar Bites:* $6,754.00 (1,351 units sold)
  - *New York Cheesecake Slice:* $6,842.79 (1,244 units sold)
- **Business Impact:** Low-velocity specialty beverages tie up refrigerated display space and risk expiration before depletion.
- **Recommended Action:** Delist Organic Craft Kombucha or replace it with a higher-velocity iced tea variant. Bundle Cinnamon Bites directly into the Family Game Night combo.

---

### Question 6: Which products need inventory replenishment?
- **Finding:** Three fresh produce SKUs have fallen below their safety reorder thresholds:
- **Supporting Metric:**
  1. **Fresh Genovese Basil (`INV-017`):** Stock = 8 kg | Reorder Level = 12 kg (CRITICAL)
  2. **Fresh Romaine Hearts (`INV-016`):** Stock = 20 cases | Reorder Level = 25 cases (LOW)
  3. **Fresh White Button Mushrooms (`INV-013`):** Stock = 32 kg | Reorder Level = 40 kg (LOW)
- **Business Impact:** Runout of basil or mushrooms halts production of Margherita Classic and Veggie Garden pizzas, impacting nearly $1,500/day in potential sales.
- **Recommended Action:** Issue automated electronic purchase orders (PO) to `SUP-04` (FarmFresh Produce) for immediate next-day morning delivery.

---

### Question 7: Which products have excessive inventory?
- **Finding:** Non-perishable packaging and dry flour items are currently overstocked above 90% warehouse capacity.
- **Supporting Metric:**
  1. **Kraft Side Carryout Bags (`INV-023`):** Stock = 4,600 units (92.0% of 5,000 max capacity)
  2. **High-Gluten Pizza Flour (`INV-004`):** Stock = 2,350 kg (94.0% of 2,500 max capacity, valuation: $1,997.50)
- **Business Impact:** Overstocked bags and flour consume dry storage space and tie up ~$2,800 in unneeded working capital.
- **Recommended Action:** Pause routine bi-weekly deliveries from `SUP-02` and `SUP-06` until flour drops to 1,200 kg and bags drop to 2,000 units.

---

### Question 8: How much inventory is wasted?
- **Finding:** Annual kitchen wastage totaled **$25,202.93** across **1,094 incidents** (2.36% of net sales).
- **Supporting Metric:**
  - **Expired Shelf-Life:** $11,861.39 (47.06% of all waste)
  - **Preparation Trim / Spillage:** $6,321.50 (25.08%)
  - **Drop / Damaged Handling:** $3,538.55 (14.04%)
  - **Overcooked / Burnt:** $3,481.49 (13.81%)
- **Business Impact:** Expired perishable greens and dairy represent direct unrecovered cash drain from gross profit.
- **Recommended Action:** Transition perishable produce ordering from 1x/week to 2x/week (smaller, fresher drops) and enforce strict First-In, First-Out (FIFO) kitchen inventory staging.

---

### Question 9: Which products have the highest profitability?
- **Finding:** **Pepperoni Feast** delivers the highest total dollar gross profit, while **Fountain Soda** delivers the highest percentage gross margin.
- **Supporting Metric:**
  - *Top Dollar Profit:* Pepperoni Feast generates **$138,704.37** in gross profit (70.36% margin).
  - *Top Percentage Margin:* Fountain Beverages achieve **87.27% gross margin** ($2.75 price vs $0.35 COGS).
  - *Category Profitability:* Pizza contributes $445,431.50 in gross profit (70.20% margin); Combos contribute $179,848.16 in gross profit (68.81% margin).
- **Business Impact:** High-margin sides and beverages significantly improve store-level operating margins when bundled.
- **Recommended Action:** Anchor high-margin fountain drinks into all lunch combos to maximize cash flow per transaction.

---

### Question 10: How can inventory management be improved?
1. **Dynamic Reorder Points (ROP):** Shift from static gut-feel ordering to the calculated formula:
   $$\text{ROP} = (\text{Average Daily Consumption} \times \text{Lead Time Days}) + \text{Safety Stock}$$
2. **Perishable Safety Buffer:** Set safety stock for produce to a 2-day buffer rather than 5 days, curtailing the $11.8k expiration waste.
3. **Weekly Cycle Counts:** Conduct high-value protein audits (chicken wings, cured pepperoni, cheeses) weekly to eliminate prep trim slippage.

---

### Question 11: How can restaurant operations be made more efficient?
1. **Kitchen Station Balancing:** At the Downtown Flagship and Suburb Center, dedicate one makeline exclusively to Delivery/Takeout orders during 12:00–1:30 PM to prevent in-store diner delays.
2. **Drive-thru & Kiosk Throughput:** Metro Station Kiosk averages $28.50 AOV. Introducing a 3-tap touch-screen combo menu will reduce ordering time from 75 seconds to under 30 seconds.
3. **Cross-Trained Evening Crew:** Cross-train dishwashers and cashiers on box prep to eliminate packaging bottlenecks during the 6:00–8:00 PM dinner rush.

---

### Question 12: What actions can management take to improve revenue?
1. **Midweek Lunch Promotion:** Introduce a $12.99 "Lunch Express Slice & Soda" Mon–Thu from 11:30 AM to 1:30 PM to raise weekday AOV and capture corporate office traffic.
2. **Weekend Party Upsell:** Upsell the Party Supreme Bundle ($64.99) on digital delivery platforms (DoorDash, UberEats) during football game hours.
3. **Beverage & Dessert Add-on Protocol:** Incentivize cashiers with monthly bonuses for achieving a >15% beverage and dessert attach rate on single-item orders.

---

## 3. Financial Summary & ROI Projection

Implementing the top three strategic recommendations (perishable waste reduction, midweek combo upselling, and beverage attach optimization) will yield:
- **+$12,600 / year** from a 50% reduction in expired food wastage.
- **+$42,000 / year** from a 5% increase in Mon–Thu lunch revenue.
- **+$24,500 / year** from lifting beverage attach rates by 4 percentage points.
- **Total Projected EBITDA Lift:** **+$79,100 / year** across the 4-location chain.
