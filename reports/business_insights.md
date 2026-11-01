# QSR Sales & Inventory Optimization — Executive Business Insights Report

> **Dataset Transparency & Simulation Disclosure:**  
> This project is conducted on a high-fidelity **synthetic business analytics dataset** generated via `data_generation.py` for **Artisan Crust Co.**, a simulated 4-unit regional Quick Service Restaurant (QSR) enterprise operating across fiscal year 2024 (January 1, 2024 to December 31, 2024; 366 days). The simulated environment models 33,051 customer transactions, 65,851 line items, 32 standardized menu items, a 125-link Bill of Materials (BOM) recipe architecture, 24 tracked inventory ingredients, 6 regional suppliers, and 1,094 kitchen waste logs. Transaction frequencies, price-elasticities, day-part rushes, and shelf-life decay were synthesized using empirical distributions informed by National Restaurant Association (NRA) industry operating benchmarks. **None of the records represent actual proprietary restaurant customer data.** All analytical findings, turnover rates, and financial opportunity models reflect this controlled business simulation.

---

## 1. Executive Summary & Verified Macro Financial Performance

The following macro KPIs were verified against underlying SQLite transactional tables (`orders`, `order_details`, `inventory`, `inventory_waste`):

| Metric | Measured Value | Standard Formula / Operational Context |
| :--- | :---: | :--- |
| **Gross Revenue (Gross Merchandise Value)** | **$1,079,004.26** | $\sum \text{GrossSales}$ (Pre-discount menu price volume) |
| **Promotional Discounts Awarded** | **$11,716.24** | $\sum \text{DiscountAmount}$ (1.09% effective discount rate) |
| **Net Revenue (Net Sales)** | **$1,067,288.02** | $\text{Gross Revenue} - \text{Promotional Discounts}$ |
| **Cost of Goods Sold (COGS)** | **$318,309.00** | $\sum \text{TotalCost}$ (**29.82% food cost ratio**; benchmark: 28–32%) |
| **Gross Profit** | **$748,979.02** | $\text{Net Revenue} - \text{COGS}$ (**70.18% gross margin**) |
| **Total Orders Fulfilled** | **33,051** | Distinct transaction count (~90.3 orders/day chain-wide) |
| **Total Menu Items Sold** | **65,851** | Distinct line item quantity sold across all tickets |
| **Average Order Value (AOV)** | **$32.29** | $\text{Net Revenue} / \text{Total Orders}$ ($34.50+ on weekend evenings) |
| **Average Basket Depth** | **1.99 items** | $\text{Total Units Sold} / \text{Total Orders}$ |
| **Beginning Inventory Valuation** | **$24,897.00** | $\sum (\text{BeginningStock} \times \text{UnitCost})$ (Jan 1, 2024) |
| **Ending Inventory Valuation** | **$22,882.40** | $\sum (\text{CurrentStock} \times \text{UnitCost})$ (Dec 31, 2024) |
| **Average Inventory Valuation** | **$23,889.70** | $(\text{Beginning Value} + \text{Ending Value}) / 2.0$ |
| **Standard Inventory Turnover Ratio** | **13.32x** | $\text{Annual COGS} / \text{Average Inventory Value}$ |
| **Days Sales of Inventory (DSI / Days to Turn)**| **27.5 days** | $366 / \text{Inventory Turnover Ratio}$ |
| **Annual Kitchen Wastage Cost** | **$25,202.93** | Across 1,094 recorded incidents (2.36% of net sales) |

---

## 2. Structured Analysis of the 12 Core Business Questions

### Question 1: Which products generate the highest revenue?
- **Observation:** Signature pizza items dominate top-line cash generation, with **Pepperoni Feast** serving as the chain's anchor product.
- **Supporting Metric:**
  1. *Pepperoni Feast:* $197,134.07 net revenue (11,821 units sold; 18.47% share of total chain sales).
  2. *BBQ Chicken Supreme:* $112,398.98 net revenue (6,326 units sold; 10.53% share).
  3. *Margherita Classic:* $108,772.30 net revenue (7,401 units sold; 10.19% share).
- **Business Interpretation:** The top 3 signature pizzas collectively generate **$418,305.35** (39.19% of total revenue). Customer preference is concentrated heavily around premium traditional toppings.
- **Financial Implications:** Because these 3 items consume the highest volume of mozzarella (`INV-001`), pizza sauce (`INV-006`), pepperoni (`INV-008`), and chicken (`INV-010`), any supply disruption immediately risks up to $1,142/day in top-line sales.
- **Recommended Management Action:** Establish secondary backup vendor agreements for mozzarella and pepperoni with Supplier `SUP-03` (Prime Meats) and maintain a rigid 2-day safety stock buffer on core pizza proteins.
- **Assumptions & Limitations:** Figures reflect simulated consumer choice patterns without accounting for localized competitor delivery pricing or promotional flyers.

---

### Question 2: Which categories contribute the most to sales?
- **Observation:** Core **Pizza** and multi-item **Combos** constitute the vast majority of sales volume.
- **Supporting Metric:**
  - **Pizza:** $634,522.60 (59.45% of net revenue; 38,914 units)
  - **Combos:** $261,357.16 (24.49% of net revenue; 9,599 units)
  - **Sides:** $100,264.44 (9.39% of net revenue; 14,649 units)
  - **Beverages:** $38,420.42 (3.60% of net revenue; 11,434 units)
  - **Desserts:** $32,723.40 (3.07% of net revenue; 5,718 units)
- **Business Interpretation:** While Combos have high AOV ($27.23 average ticket item), standalone beverage and dessert attach rates remain below 4% of sales, indicating significant missed cross-selling potential.
- **Financial Implications:** Beverages deliver an 82.97% gross margin ($31,877 gross profit on $38,420 net revenue). Under-indexing on beverage attach directly suppresses chain gross margin percentages.
- **Recommended Management Action:** Implement automated digital POS and delivery app bundling prompts ("Add a 2-liter soda and cookies for $4.99") on all standalone pizza orders.
- **Assumptions & Limitations:** Assumes simulated basket behavior where cross-sell prompts do not induce checkout cart abandonment.

---

### Question 3: When does the restaurant experience peak demand?
- **Observation:** Store transactions follow a defined bi-modal distribution centered on lunch and dinner rush hours.
- **Supporting Metric:**
  - **Lunch Rush (12:00 PM – 2:00 PM):** 9,932 orders (30.05% of daily volume). Peak hour is **12:00 PM** (5,300 orders; $171,190 annual sales).
  - **Dinner Rush (6:00 PM – 8:00 PM):** 8,240 orders (24.93% of daily volume). Peak hour is **6:00 PM** (4,982 orders; $160,891 annual sales).
  - **Mid-Afternoon Lull (2:00 PM – 4:00 PM):** Combined order volume drops to 2,840 orders (8.59% of volume).
- **Business Interpretation:** Kitchen throughput bottlenecks occur during 12:00–1:30 PM, causing oven queueing, increased customer wait times, and delivery dispatch friction.
- **Financial Implications:** Overloaded ovens during lunch peaks restrict order intake capacity, capping peak revenue generation.
- **Recommended Management Action:** Pre-stretch dough crusts and pre-portion cheese and toppings 30 minutes before the 12:00 PM and 6:00 PM rushes. Dedicate one prep line exclusively to digital delivery/pickup tickets.
- **Assumptions & Limitations:** Analysis assumes uniform oven heating capacity and consistent kitchen station layout across all 4 locations.

---

### Question 4: Which weekdays generate the most revenue?
- **Observation:** Revenue is heavily compressed into weekend trading (Friday, Saturday, Sunday).
- **Supporting Metric:**
  - **Sunday:** $201,000.75 (18.83% of sales; 5,798 orders)
  - **Saturday:** $199,691.52 (18.71% of sales; 5,839 orders)
  - **Friday:** $193,597.33 (18.14% of sales; 5,666 orders)
  - **Monday–Thursday Total:** $472,998.42 (44.32% across 4 days; averaging ~$118,250 per weekday).
- **Business Interpretation:** Over **55.68% of annual sales** ($594,289.60) occurs over the 3-day weekend window. Weekend AOV ($34.42) is significantly higher than weekday AOV ($29.85).
- **Financial Implications:** Fixed kitchen assets and seating are under-utilized Monday through Thursday, while weekend staffing is strained.
- **Recommended Management Action:** Launch targeted midweek promotions (e.g., "Two-for-Tuesday Pizza Deal" or corporate lunch subscription combos) to stimulate Monday–Thursday traffic.
- **Assumptions & Limitations:** Weather anomalies, localized holiday calendars, and sports broadcast schedules are simulated stochastically.

---

### Question 5: Which products sell slowly?
- **Observation:** Specialty beverages and single-serve dessert items exhibit low transaction frequency.
- **Supporting Metric:**
  - *Organic Craft Kombucha:* 690 units sold ($3,277.75 revenue; 1.88 units/day across 4 stores).
  - *Sparkling Mineral Water:* 1,347 units sold ($3,366.85 revenue; 3.68 units/day).
  - *Cinnamon Sugar Bites:* 1,351 units sold ($6,754.00 revenue).
  - *New York Cheesecake Slice:* 1,244 units sold ($6,842.79 revenue).
- **Business Interpretation:** Specialty cold-chain beverages tie up valuable front-counter refrigerator display space and incur expiration risks without driving meaningful sales.
- **Financial Implications:** Low velocity items incur dead inventory capital and increase perishable spoilage risk.
- **Recommended Management Action:** Rationalize the menu by delisting Organic Craft Kombucha. Bundle Cinnamon Sugar Bites directly into combo boxes (e.g., Artisan Duo Feast) to deplete existing stock.
- **Assumptions & Limitations:** Consumer brand loyalty to niche beverage offerings was not surveyed in the simulation.

---

### Question 6: Which products need inventory replenishment?
- **Observation:** Fast-moving perishable produce items periodically fall below safety stock levels due to supplier lead times.
- **Supporting Metric:**
  - *Fresh Genovese Basil (`INV-017`):* Current Stock = 8 kg vs Calculated ROP = 86.1 par level (Critical Alert).
  - *Fresh Romaine Hearts (`INV-016`):* Current Stock = 20 cases vs Reorder Level = 25 cases.
  - *Fresh White Button Mushrooms (`INV-013`):* Current Stock = 32 kg vs Reorder Level = 40 kg.
- **Business Interpretation:** Produce items have short shelf lives (3–5 days) and high daily consumption velocity, creating tight replenishment windows.
- **Financial Implications:** Stockout of fresh basil or mushrooms forces 86-ing Margherita Classic and Veggie pizzas, directly threatening up to $900/day in lost sales.
- **Recommended Management Action:** Automate electronic purchase orders (EDI) triggered immediately when stock breaches calculated Dynamic ROP, and arrange daily morning cross-dock deliveries with `SUP-04` (FarmFresh Produce).
- **Assumptions & Limitations:** Lead times are modeled as deterministic based on supplier contracts; transit delays (traffic/weather) are not dynamically modeled.

---

### Question 7: Which products have excessive inventory?
- **Observation:** Non-perishable dry goods and paper packaging materials are held in quantities exceeding 90% warehouse capacity.
- **Supporting Metric:**
  - *High-Gluten Pizza Flour (`INV-004`):* Current Stock = 2,350 kg (94.0% of 2,500 kg Max Capacity; Valuation = $1,997.50; Stock Coverage = 59.1 days).
  - *Kraft Side Carryout Bags (`INV-023`):* Current Stock = 4,600 units (92.0% of 5,000 max capacity; Valuation = $690.00; Stock Coverage = 68.2 days).
- **Business Interpretation:** Purchasing large bulk deliveries of non-perishables reduces per-unit invoice costs but congests limited back-of-house storage space.
- **Financial Implications:** ~$2,680 in working capital is tied up in dry flour and bags, creating opportunity cost and moisture contamination risks.
- **Recommended Management Action:** Place a 3-week procurement hold on flour and bags until stock coverage normalizes to a 20-day buffer (~800 kg flour and 1,500 bags).
- **Assumptions & Limitations:** Bulk freight delivery discounts were not penalized by warehouse holding cost calculations in raw ledger records.

---

### Question 8: How much inventory is wasted?
- **Observation:** Total recorded food and packaging waste amounted to **$25,202.93** across 1,094 incidents (2.36% of net sales).
- **Supporting Metric:**
  - **Expired Shelf-Life:** $11,861.39 (47.06% of total waste; 1,712 units discarded).
  - **Preparation Trim / Spillage:** $6,321.50 (25.08%; 908 units discarded).
  - **Drop / Damaged Handling:** $3,538.55 (14.04%; 507 units discarded).
  - **Overcooked / Burnt:** $3,481.49 (13.81%; 538 units discarded).
- **Business Interpretation:** Expiration of perishable produce and dairy is the single largest root cause of dollar leakage, followed by prep knife errors and over-portioning.
- **Financial Implications:** Food waste directly inflates COGS by 2.36 percentage points, reducing gross profit dollar-for-dollar.
- **Recommended Management Action:** Implement First-In, First-Out (FIFO) colored container date-dots, shift produce deliveries from weekly to twice-weekly batches, and introduce digital portion scales at pizza prep stations.
- **Assumptions & Limitations:** Waste logs rely on kitchen staff self-reporting; unrecorded theft or untracked over-portioning is not captured.

---

### Question 9: Which products have the highest profitability?
- **Observation:** High-volume pizzas generate the largest total gross profit dollars, while fountain drinks yield the highest gross margin percentages.
- **Supporting Metric:**
  - *Highest Dollar Profit:* **Pepperoni Feast** generated **$138,704.37** in gross profit (70.36% gross margin; $197,134.07 net sales vs $58,429.70 COGS).
  - *Highest Percentage Margin:* **Fountain Beverages** delivered **82.97% gross margin** ($31,877.32 gross profit on $38,420.42 revenue; syrup and cup cost is ~$0.47 per unit).
  - *Top Margin Pizza:* Margherita Classic achieved a **71.90% margin** ($78,212.50 profit on $108,772.30 sales) due to simple, lower-cost cheese and basil toppings.
- **Business Interpretation:** Premium meat toppings carry higher dollar margins despite slightly lower percentage margins, while beverages provide pure margin expansion.
- **Financial Implications:** Maximizing fountain drink attach on pizza orders accelerates cash conversion and overall margin expansion.
- **Recommended Management Action:** Protect recipe specifications on Pepperoni Feast against ingredient degradation, and train staff to suggest drinks on all phone and counter orders.
- **Assumptions & Limitations:** COGS figures reflect standardized recipe ingredient weights and unit purchase prices, excluding kitchen labor and utility baking costs.

---

### Question 10: How can inventory management be improved?
- **Observation:** Transitioning from static periodic par ordering to dynamic consumption-driven reorder parameters stabilizes stock.
- **Supporting Metric:**
  - Implemented Dynamic Reorder Point Formula:
    $$\text{ROP} = (\mu_{\text{daily}} \times \text{LeadTimeDays}) + \left(1.65 \times \sigma_{\text{daily}} \times \sqrt{\text{LeadTimeDays}}\right)$$
  - Across 24 SKUs, empirical consumption was tracked across all 366 days (including zero-sales dates).
- **Business Interpretation:** Incorporating demand variance ($\sigma_{\text{daily}}$) prevents stockouts during weekend surges while curtailing mid-week overstocking.
- **Financial Implications:** Mitigates the risk of perishable produce expiration ($11.8k baseline waste) while guaranteeing 95% cycle-service levels.
- **Recommended Management Action:** Synchronize POS nightly transaction rollups with inventory depletion tables using recipe Bill of Materials (BOM) explosion.
- **Assumptions & Limitations:** Assumes normal distribution of daily demand and consistent supplier lead times.

---

### Question 11: How can restaurant operations be made more efficient?
- **Observation:** Store-level sales vary significantly by location type and operational footprint.
- **Supporting Metric:**
  - *Downtown Flagship (Dine-in/Delivery):* $348,210.45 net sales (9,842 orders; AOV $35.38).
  - *Suburb Center (Family Dining):* $312,450.80 net sales (8,914 orders; AOV $35.05).
  - *West End Mall (Food Court):* $248,110.12 net sales (8,421 orders; AOV $29.46).
  - *Metro Station Kiosk (Grab & Go):* $158,516.65 net sales (5,874 orders; AOV $26.99).
- **Business Interpretation:** Kiosk and Food Court locations have high order velocity but lower ticket sizes, whereas Flagship and Suburb units handle large dinner groups.
- **Financial Implications:** Kiosks require high-speed transaction processing to remain profitable, while full-service stores require seating turn optimization.
- **Recommended Management Action:** Deploy 3-tap self-service touchscreen kiosks at the Metro Station and West End Mall to reduce order taking time from 70 seconds to under 25 seconds.
- **Assumptions & Limitations:** Customer foot traffic counts outside store entrances were not captured in the point-of-sale dataset.

---

### Question 12: What actions can management take to improve revenue?
- **Observation:** Strategic interventions targeting weekday traffic, combo upsells, and beverage attachments present viable growth levers.
- **Supporting Metric:**
  - Monday–Thursday represents 44.3% of sales with an average basket size of $29.85.
  - Weekend orders average $34.42 with higher bundle penetration.
- **Business Interpretation:** Closing the $4.57 ticket gap on weekdays and lifting drink attach represents substantial top-line opportunity.
- **Recommended Management Action:** Launch a $14.99 "Midweek Express Lunch" combo (personal pizza, fountain drink, dipping sauce) Mon–Thu from 11:30 AM to 2:00 PM.
- **Assumptions & Limitations:** Assumes kitchen capacity can accommodate incremental lunch volume without slowing delivery fulfillment.

---

## 3. Financial Modeling & Opportunity Scenarios

### 3.1 Investigation of the Preliminary "$79,100 EBITDA Lift" Claim
In the initial draft of this project, a potential annual improvement of **$79,100** was reported and labeled as an "EBITDA improvement." An exhaustive analytical review of the financial logic reveals:

1. **Analytical Methodology Issue:** The QSR transaction dataset records sales revenues, discounts, and direct food ingredient costs (COGS). It **does not record operating expenses (OPEX)** such as kitchen labor wages, commercial rent, utilities, delivery fleet fees, or equipment depreciation. Therefore, **calculating EBITDA (Earnings Before Interest, Taxes, Depreciation, and Amortization) is analytically invalid**. Any financial opportunity must be strictly identified as an **Estimated Gross Profit Opportunity**.
2. **Deconstruction of the Original Calculation:**
   - *Component 1 (Wastage Reduction):* Assumed a 50% reduction in total annual food wastage ($25,202.93 $\times$ 50% $\approx$ $12,600/year COGS savings).
   - *Component 2 (Weekday Revenue Lift):* Assumed a ~5% increase on weekday sales ($472,998 $\times$ 5% $\approx$ $23,650 gross revenue, or $42,000 if overall lunch revenue was targeted).
   - *Component 3 (Beverage Cross-Sell):* Assumed a 4 percentage point expansion in beverage attach rates ($\approx$ $24,500 incremental revenue).
   - *Sum:* $12,600 + $42,000 + $24,500 = $79,100.
3. **Correction & Transparency:** Revenue, gross margin, and operating income must not be conflated. Below, we present modeled opportunity scenarios with fully disclosed assumptions, separating empirical metrics from hypothetical projections.

---

### 3.2 Modeled Annual Gross Profit Opportunity Scenarios

| Scenario Dimension | Baseline Metric (2024 Actual) | Conservative Opportunity (+20%) | Moderate Opportunity (+35%) | Aggressive Target (+50%) | Methodology & Assumptions |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **A. Expired Food Wastage Reduction** | $11,861.39 (Expired Waste Cost) | **+$2,372 / yr** (20% reduction) | **+$4,151 / yr** (35% reduction) | **+$5,931 / yr** (50% reduction) | COGS savings realized through twice-weekly produce drops and FIFO date-labeling. |
| **B. Midweek Lunch Express Volume Lift** | $472,998.42 (Mon–Thu Net Sales) | **+$6,640 / yr** (2% sales lift @ 70.2% margin) | **+$11,620 / yr** (3.5% sales lift @ 70.2% margin) | **+$16,600 / yr** (5% sales lift @ 70.2% margin) | Net gross profit contribution from incremental Mon–Thu lunch orders. |
| **C. Beverage Attach Optimization** | $38,420.42 (Beverage Sales) | **+$3,188 / yr** (10% attach lift @ 83.0% margin) | **+$6,375 / yr** (20% attach lift @ 83.0% margin) | **+$9,563 / yr** (30% attach lift @ 83.0% margin) | Gross profit from add-on fountain drinks ($0.47 COGS vs $2.75 price). |
| **Total Estimated Gross Profit Opportunity** | — | **+$12,200 / yr** | **+$22,146 / yr** | **+$32,094 / yr** | **Non-guaranteed exploratory projection across 4 stores.** |

> [!IMPORTANT]
> **Executive Note on Projections:** These opportunity ranges represent hypothetical scenario models designed for executive evaluation. They do not constitute guaranteed earnings forecasts. Realization depends upon kitchen operational discipline, employee compliance with portion controls, and local competitive conditions.
