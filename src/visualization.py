"""
QSR Visual Analytics & Exploratory Data Analysis Suite
======================================================
Generates 14 high-resolution, publication-grade analytical visualizations
saved to dashboard/charts/.

Charts Generated:
01_monthly_revenue_trend.png
02_daily_revenue_trend.png
03_hourly_sales_distribution.png
04_weekday_vs_weekend_sales.png
05_revenue_by_product_category.png
06_top_10_products_by_revenue.png
07_top_10_products_by_quantity.png
08_aov_trends.png
09_payment_method_distribution.png
10_product_performance_comparison.png
11_inventory_stock_distribution.png
12_inventory_wastage_analysis.png
13_inventory_turnover_comparison.png
14_gross_margin_by_category.png
"""

import os
import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns

logger = logging.getLogger(__name__)

# Aesthetic styling
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Helvetica"]
plt.rcParams["axes.titlesize"] = 13
plt.rcParams["axes.titleweight"] = "bold"
plt.rcParams["axes.labelsize"] = 11
plt.rcParams["xtick.labelsize"] = 10
plt.rcParams["ytick.labelsize"] = 10

PRIMARY_COLOR = "#C0392B"   # Artisan Pizza Red
SECONDARY_COLOR = "#2980B9" # Deep Blue
ACCENT_COLOR = "#27AE60"    # Fresh Herb Green
DARK_TEXT = "#2C3E50"


def generate_all_visualizations(
    df_orders: pd.DataFrame,
    df_details: pd.DataFrame,
    df_inventory: pd.DataFrame,
    df_waste: pd.DataFrame,
    output_dir: str = "dashboard/charts"
) -> list:
    """Generate all 14 required exploratory analysis figures."""
    os.makedirs(output_dir, exist_ok=True)
    generated_files = []

    # ─────────────────────────────────────────────────────────────────────────
    # Chart 01: Monthly Revenue Trend
    # ─────────────────────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(10, 5))
    monthly = df_orders.groupby(["OrderMonth", "OrderMonthName"])["NetSales"].sum().reset_index()
    monthly = monthly.sort_values("OrderMonth")
    
    ax.plot(monthly["OrderMonthName"], monthly["NetSales"] / 1000, marker="o", color=PRIMARY_COLOR, linewidth=2.5, markersize=8)
    ax.fill_between(monthly["OrderMonthName"], monthly["NetSales"] / 1000, alpha=0.15, color=PRIMARY_COLOR)
    ax.set_title("Monthly Net Revenue Trend (2024)", pad=15)
    ax.set_ylabel("Revenue ($ in Thousands)")
    ax.set_xlabel("Month")
    ax.yaxis.set_major_formatter(ticker.FormatStrFormatter("$%.0fk"))
    for _, row in monthly.iterrows():
        ax.annotate(f"${row['NetSales']/1000:.1f}k", (row["OrderMonthName"], (row["NetSales"]/1000) + 1.2),
                    ha="center", fontsize=9, fontweight="bold", color=DARK_TEXT)
    ax.set_ylim(0, (monthly["NetSales"].max() / 1000) * 1.2)
    plt.tight_layout()
    p1 = os.path.join(output_dir, "01_monthly_revenue_trend.png")
    fig.savefig(p1, dpi=200)
    plt.close(fig)
    generated_files.append(p1)

    # ─────────────────────────────────────────────────────────────────────────
    # Chart 02: Daily Revenue Trend (with 7-Day Moving Average)
    # ─────────────────────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(12, 5))
    daily = df_orders.groupby("OrderDate")["NetSales"].sum().reset_index()
    daily["OrderDate"] = pd.to_datetime(daily["OrderDate"])
    daily = daily.sort_values("OrderDate")
    daily["7D_MA"] = daily["NetSales"].rolling(7, min_periods=1).mean()

    ax.scatter(daily["OrderDate"], daily["NetSales"], alpha=0.35, color=SECONDARY_COLOR, s=15, label="Daily Net Sales")
    ax.plot(daily["OrderDate"], daily["7D_MA"], color=PRIMARY_COLOR, linewidth=2.2, label="7-Day Moving Average")
    ax.set_title("Daily Sales Trend & 7-Day Moving Average (Full Year 2024)", pad=15)
    ax.set_ylabel("Daily Net Revenue ($)")
    ax.yaxis.set_major_formatter(ticker.StrMethodFormatter("${x:,.0f}"))
    ax.legend(loc="upper left")
    plt.tight_layout()
    p2 = os.path.join(output_dir, "02_daily_revenue_trend.png")
    fig.savefig(p2, dpi=200)
    plt.close(fig)
    generated_files.append(p2)

    # ─────────────────────────────────────────────────────────────────────────
    # Chart 03: Hourly Sales Distribution (Peak Rush Hours)
    # ─────────────────────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(11, 5))
    hourly = df_orders.groupby("OrderHour")["OrderID"].count().reset_index()
    colors = [
        PRIMARY_COLOR if h in [12, 13] else ("#E67E22" if h in [18, 19] else "#7F8C8D")
        for h in hourly["OrderHour"]
    ]
    bars = ax.bar(hourly["OrderHour"], hourly["OrderID"], color=colors, edgecolor="black", linewidth=0.5, alpha=0.85)
    ax.set_title("Hourly Order Volume & Peak Dining Rush Periods", pad=15)
    ax.set_xlabel("Hour of the Day (24-Hour Military Time)")
    ax.set_ylabel("Total Orders Placed")
    ax.set_xticks(hourly["OrderHour"])
    ax.set_xticklabels([f"{h}:00" for h in hourly["OrderHour"]], rotation=45)
    # Legend proxies
    ax.axvspan(11.5, 13.5, color=PRIMARY_COLOR, alpha=0.1, label="Lunch Rush (12pm - 2pm)")
    ax.axvspan(17.5, 19.5, color="#E67E22", alpha=0.1, label="Dinner Rush (6pm - 8pm)")
    ax.legend(loc="upper left")
    plt.tight_layout()
    p3 = os.path.join(output_dir, "03_hourly_sales_distribution.png")
    fig.savefig(p3, dpi=200)
    plt.close(fig)
    generated_files.append(p3)

    # ─────────────────────────────────────────────────────────────────────────
    # Chart 04: Weekday versus Weekend Sales
    # ─────────────────────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(8, 5))
    dow = df_orders.groupby(["DayOfWeek", "DayName", "IsWeekend"]).agg(
        AvgDailyRevenue=("NetSales", lambda s: s.sum() / df_orders.groupby("DayOfWeek")["OrderDate"].nunique().iloc[0])
    ).reset_index().sort_values("DayOfWeek")
    bar_cols = [PRIMARY_COLOR if row["IsWeekend"] == 1 else SECONDARY_COLOR for _, row in dow.iterrows()]
    ax.bar(dow["DayName"], dow["AvgDailyRevenue"], color=bar_cols, width=0.6, edgecolor="black", linewidth=0.5)
    ax.set_title("Average Daily Revenue: Weekday vs Weekend (Fri-Sun)", pad=15)
    ax.set_ylabel("Average Daily Revenue ($)")
    ax.yaxis.set_major_formatter(ticker.StrMethodFormatter("${x:,.0f}"))
    for p in ax.patches:
        val = p.get_height()
        ax.annotate(f"${val:,.0f}", (p.get_x() + p.get_width() / 2., val + 40),
                    ha="center", fontsize=9, fontweight="bold")
    ax.set_ylim(0, dow["AvgDailyRevenue"].max() * 1.15)
    plt.tight_layout()
    p4 = os.path.join(output_dir, "04_weekday_vs_weekend_sales.png")
    fig.savefig(p4, dpi=200)
    plt.close(fig)
    generated_files.append(p4)

    # ─────────────────────────────────────────────────────────────────────────
    # Chart 05: Revenue by Product Category
    # ─────────────────────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(9, 5))
    cat_rev = df_details.groupby("Category")["TotalPrice"].sum().reset_index().sort_values("TotalPrice", ascending=True)
    ax.barh(cat_rev["Category"], cat_rev["TotalPrice"] / 1000, color=SECONDARY_COLOR, edgecolor="black", linewidth=0.5)
    ax.set_title("Total Revenue by Menu Category ($ in Thousands)", pad=15)
    ax.set_xlabel("Revenue ($ in Thousands)")
    ax.xaxis.set_major_formatter(ticker.FormatStrFormatter("$%.0fk"))
    total_r = cat_rev["TotalPrice"].sum()
    for p in ax.patches:
        w = p.get_width()
        pct = (w * 1000 / total_r) * 100
        ax.annotate(f"${w:.1f}k ({pct:.1f}%)", (w + 4, p.get_y() + p.get_height() / 2.),
                    va="center", fontsize=9, fontweight="bold")
    ax.set_xlim(0, (cat_rev["TotalPrice"].max() / 1000) * 1.25)
    plt.tight_layout()
    p5 = os.path.join(output_dir, "05_revenue_by_product_category.png")
    fig.savefig(p5, dpi=200)
    plt.close(fig)
    generated_files.append(p5)

    # ─────────────────────────────────────────────────────────────────────────
    # Chart 06: Top 10 Products by Revenue
    # ─────────────────────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(10, 6))
    top_p_rev = df_details.groupby("ProductName")["TotalPrice"].sum().nlargest(10).sort_values(ascending=True)
    ax.barh(top_p_rev.index, top_p_rev.values / 1000, color=PRIMARY_COLOR, edgecolor="black", linewidth=0.5)
    ax.set_title("Top 10 Highest Revenue-Generating Menu Items", pad=15)
    ax.set_xlabel("Total Sales ($ in Thousands)")
    ax.xaxis.set_major_formatter(ticker.FormatStrFormatter("$%.0fk"))
    for p in ax.patches:
        w = p.get_width()
        ax.annotate(f"${w:.1f}k", (w + 1.5, p.get_y() + p.get_height() / 2.),
                    va="center", fontsize=9, fontweight="bold")
    ax.set_xlim(0, (top_p_rev.max() / 1000) * 1.15)
    plt.tight_layout()
    p6 = os.path.join(output_dir, "06_top_10_products_by_revenue.png")
    fig.savefig(p6, dpi=200)
    plt.close(fig)
    generated_files.append(p6)

    # ─────────────────────────────────────────────────────────────────────────
    # Chart 07: Top 10 Products by Quantity Sold
    # ─────────────────────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(10, 6))
    top_p_qty = df_details.groupby("ProductName")["Quantity"].sum().nlargest(10).sort_values(ascending=True)
    ax.barh(top_p_qty.index, top_p_qty.values, color="#16A085", edgecolor="black", linewidth=0.5)
    ax.set_title("Top 10 Menu Items by Total Quantity Sold (Units)", pad=15)
    ax.set_xlabel("Units Sold")
    for p in ax.patches:
        w = p.get_width()
        ax.annotate(f"{int(w):,}", (w + 100, p.get_y() + p.get_height() / 2.),
                    va="center", fontsize=9, fontweight="bold")
    ax.set_xlim(0, top_p_qty.max() * 1.15)
    plt.tight_layout()
    p7 = os.path.join(output_dir, "07_top_10_products_by_quantity.png")
    fig.savefig(p7, dpi=200)
    plt.close(fig)
    generated_files.append(p7)

    # ─────────────────────────────────────────────────────────────────────────
    # Chart 08: Average Order Value (AOV) Trends
    # ─────────────────────────────────────────────────────────────────────────
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    # By Month
    monthly_aov = df_orders.groupby("OrderMonthName", as_index=False)["NetSales"].mean()
    # Ensure correct calendar order
    month_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    monthly_aov["Sort"] = monthly_aov["OrderMonthName"].map(lambda m: month_order.index(m) if m in month_order else 99)
    monthly_aov = monthly_aov.sort_values("Sort")
    axes[0].plot(monthly_aov["OrderMonthName"], monthly_aov["NetSales"], marker="s", color=SECONDARY_COLOR, linewidth=2)
    axes[0].set_title("Average Order Value by Month ($)")
    axes[0].set_ylabel("AOV ($)")
    axes[0].yaxis.set_major_formatter(ticker.FormatStrFormatter("$%.2f"))

    # By Day of Week
    dow_aov = df_orders.groupby("DayName", as_index=False)["NetSales"].mean()
    dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    dow_aov["Sort"] = dow_aov["DayName"].map(lambda d: dow_order.index(d) if d in dow_order else 99)
    dow_aov = dow_aov.sort_values("Sort")
    axes[1].bar(dow_aov["DayName"], dow_aov["NetSales"], color=[PRIMARY_COLOR if d in ["Friday", "Saturday", "Sunday"] else SECONDARY_COLOR for d in dow_aov["DayName"]], width=0.6)
    axes[1].set_title("AOV by Day of Week (Weekend Premium)")
    axes[1].set_ylabel("AOV ($)")
    axes[1].tick_params(axis="x", rotation=30)
    axes[1].yaxis.set_major_formatter(ticker.FormatStrFormatter("$%.2f"))
    plt.tight_layout()
    p8 = os.path.join(output_dir, "08_aov_trends.png")
    fig.savefig(p8, dpi=200)
    plt.close(fig)
    generated_files.append(p8)

    # ─────────────────────────────────────────────────────────────────────────
    # Chart 09: Payment Method Distribution
    # ─────────────────────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(7, 7))
    pay_dist = df_orders.groupby("PaymentMethod")["NetSales"].sum()
    palette = ["#2980B9", "#27AE60", "#F39C12", "#E74C3C"]
    wedges, texts, autotexts = ax.pie(
        pay_dist.values, labels=pay_dist.index, autopct="%1.1f%%",
        startangle=140, colors=palette, pctdistance=0.75,
        wedgeprops=dict(width=0.4, edgecolor="white", linewidth=2)
    )
    plt.setp(autotexts, size=10, weight="bold")
    ax.set_title("Settled Revenue Share by Payment Method", pad=20)
    plt.tight_layout()
    p9 = os.path.join(output_dir, "09_payment_method_distribution.png")
    fig.savefig(p9, dpi=200)
    plt.close(fig)
    generated_files.append(p9)

    # ─────────────────────────────────────────────────────────────────────────
    # Chart 10: Product Performance Comparison (Revenue vs Quantity vs Profit)
    # ─────────────────────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(10, 6))
    prod_scatter = df_details.groupby(["ProductName", "Category"]).agg(
        Units=("Quantity", "sum"),
        Revenue=("TotalPrice", "sum"),
        Profit=("LineProfit", "sum")
    ).reset_index()

    sns.scatterplot(
        data=prod_scatter, x="Units", y="Revenue", hue="Category",
        size="Profit", sizes=(60, 450), alpha=0.85, ax=ax, palette="tab10"
    )
    ax.set_title("Product Portfolio Matrix: Units Sold vs Revenue Generated", pad=15)
    ax.set_xlabel("Total Units Sold")
    ax.set_ylabel("Total Revenue Generated ($)")
    ax.yaxis.set_major_formatter(ticker.StrMethodFormatter("${x:,.0f}"))
    ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()
    p10 = os.path.join(output_dir, "10_product_performance_comparison.png")
    fig.savefig(p10, dpi=200)
    plt.close(fig)
    generated_files.append(p10)

    # ─────────────────────────────────────────────────────────────────────────
    # Chart 11: Inventory Stock Distribution (Current vs Reorder Level)
    # ─────────────────────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(12, 6))
    inv_sample = df_inventory.head(12)
    x = np.arange(len(inv_sample))
    w = 0.35
    ax.bar(x - w/2, inv_sample["CurrentStock"], width=w, label="Current Stock", color=SECONDARY_COLOR)
    ax.bar(x + w/2, inv_sample["ReorderLevel"], width=w, label="Reorder Level", color=PRIMARY_COLOR)
    ax.set_xticks(x)
    ax.set_xticklabels(inv_sample["ItemName"], rotation=40, ha="right", fontsize=9)
    ax.set_title("Inventory Stock on Hand vs Reorder Threshold (Top SKUs)", pad=15)
    ax.set_ylabel("Stock Units")
    ax.legend()
    plt.tight_layout()
    p11 = os.path.join(output_dir, "11_inventory_stock_distribution.png")
    fig.savefig(p11, dpi=200)
    plt.close(fig)
    generated_files.append(p11)

    # ─────────────────────────────────────────────────────────────────────────
    # Chart 12: Inventory Wastage Analysis (Cost by Category & Reason)
    # ─────────────────────────────────────────────────────────────────────────
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    waste_by_cat = df_waste.groupby("Category")["WasteCost"].sum().reset_index().sort_values("WasteCost", ascending=False)
    axes[0].bar(waste_by_cat["Category"], waste_by_cat["WasteCost"], color=PRIMARY_COLOR, edgecolor="black", linewidth=0.5)
    axes[0].set_title("Kitchen Wastage Dollar Cost by Category ($)")
    axes[0].set_ylabel("Waste Cost ($)")
    axes[0].yaxis.set_major_formatter(ticker.StrMethodFormatter("${x:,.0f}"))
    axes[0].tick_params(axis="x", rotation=30)

    waste_by_reason = df_waste.groupby("Reason")["WasteCost"].sum().reset_index().sort_values("WasteCost", ascending=True)
    axes[1].barh(waste_by_reason["Reason"], waste_by_reason["WasteCost"], color="#E67E22", edgecolor="black", linewidth=0.5)
    axes[1].set_title("Primary Root Causes of Food Wastage")
    axes[1].set_xlabel("Waste Cost ($)")
    axes[1].xaxis.set_major_formatter(ticker.StrMethodFormatter("${x:,.0f}"))
    plt.tight_layout()
    p12 = os.path.join(output_dir, "12_inventory_wastage_analysis.png")
    fig.savefig(p12, dpi=200)
    plt.close(fig)
    generated_files.append(p12)

    # ─────────────────────────────────────────────────────────────────────────
    # Chart 13: Inventory Turnover & Capital Valuation Comparison
    # ─────────────────────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(9, 5))
    df_inv_copy = df_inventory.copy()
    df_inv_copy["Val"] = df_inv_copy["CurrentStock"] * df_inv_copy["UnitCost"]
    inv_cat_val = df_inv_copy.groupby("Category")["Val"].sum().reset_index(name="Valuation").sort_values("Valuation", ascending=False)
    ax.bar(inv_cat_val["Category"], inv_cat_val["Valuation"], color="#8E44AD", width=0.55, edgecolor="black", linewidth=0.5)
    ax.set_title("Current Inventory Capital Valuation by Category ($ USD)", pad=15)
    ax.set_ylabel("Tied-Up Capital Valuation ($)")
    ax.yaxis.set_major_formatter(ticker.StrMethodFormatter("${x:,.0f}"))
    for p in ax.patches:
        v = p.get_height()
        ax.annotate(f"${v:,.0f}", (p.get_x() + p.get_width() / 2., v + 50),
                    ha="center", fontsize=9, fontweight="bold")
    ax.set_ylim(0, inv_cat_val["Valuation"].max() * 1.15)
    plt.tight_layout()
    p13 = os.path.join(output_dir, "13_inventory_turnover_comparison.png")
    fig.savefig(p13, dpi=200)
    plt.close(fig)
    generated_files.append(p13)

    # ─────────────────────────────────────────────────────────────────────────
    # Chart 14: Gross Margin Percentage by Category
    # ─────────────────────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(9, 5))
    cat_margin = df_details.groupby("Category").agg(
        Profit=("LineProfit", "sum"),
        Revenue=("TotalPrice", "sum")
    ).reset_index()
    cat_margin["MarginPct"] = (cat_margin["Profit"] / cat_margin["Revenue"] * 100)
    cat_margin = cat_margin.sort_values("MarginPct", ascending=False)
    ax.bar(cat_margin["Category"], cat_margin["MarginPct"], color=ACCENT_COLOR, width=0.55, edgecolor="black", linewidth=0.5)
    ax.set_title("Gross Profit Margin (%) by Menu Category", pad=15)
    ax.set_ylabel("Gross Margin Percentage (%)")
    ax.yaxis.set_major_formatter(ticker.FormatStrFormatter("%.0f%%"))
    for p in ax.patches:
        v = p.get_height()
        ax.annotate(f"{v:.1f}%", (p.get_x() + p.get_width() / 2., v + 1.2),
                    ha="center", fontsize=9, fontweight="bold")
    ax.set_ylim(0, 100)
    plt.tight_layout()
    p14 = os.path.join(output_dir, "14_gross_margin_by_category.png")
    fig.savefig(p14, dpi=200)
    plt.close(fig)
    generated_files.append(p14)

    logger.info(f"Successfully generated all {len(generated_files)} visualizations in {output_dir}")
    return generated_files
