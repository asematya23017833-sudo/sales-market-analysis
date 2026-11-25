"""Sales & Market Analysis - rebuild (Nov 2026). Sample Superstore (public).
Runs the analysis logic (see sql/analysis.sql for the SQL Server version) and
exports chart-ready aggregates + PNG charts for the companion dashboard.
"""
import json
from pathlib import Path

import duckdb
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
con = duckdb.connect()
con.execute(f"""CREATE VIEW superstore AS
SELECT "Category", "Sub-Category", Region, Segment, "Customer Name",
       Sales, Profit, Discount, Quantity,
       CAST("Order Date" AS DATE) AS order_date
FROM read_csv_auto('{ROOT}/data/superstore.csv')""")

by_cat = con.execute("""SELECT Category, ROUND(SUM(Sales),0) AS sales, ROUND(SUM(Profit),0) AS profit
FROM superstore GROUP BY 1 ORDER BY 2 DESC""").df()
by_region = con.execute("""SELECT Region, ROUND(SUM(Sales),0) AS sales,
ROUND(SUM(Sales) / (SELECT SUM(Sales) FROM superstore), 4) AS share
FROM superstore GROUP BY 1 ORDER BY 2 DESC""").df()
monthly = con.execute("""SELECT DATE_TRUNC('month', order_date) AS month, Category, ROUND(SUM(Sales),0) AS sales
FROM superstore GROUP BY 1, 2 ORDER BY 1""").df()
discount = con.execute("""SELECT CASE WHEN Discount=0 THEN 'none' WHEN Discount<=0.2 THEN 'low'
WHEN Discount<=0.4 THEN 'mid' ELSE 'high' END AS band, ROUND(SUM(Profit),0) AS profit
FROM superstore GROUP BY 1 ORDER BY 1""").df()
kpis = con.execute("""SELECT COUNT(*) AS order_lines, COUNT(DISTINCT "Customer Name") AS customers,
ROUND(SUM(Sales),2) AS total_sales, ROUND(SUM(Profit),2) AS total_profit,
ROUND(SUM(Profit)/SUM(Sales),4) AS margin FROM superstore""").df()

plt.style.use("seaborn-v0_8-whitegrid")
fig, axes = plt.subplots(1, 2, figsize=(11, 4))
axes[0].bar(by_cat["Category"], by_cat["sales"]); axes[0].set_title("Sales by category")
axes[1].bar(by_region["Region"], by_region["sales"]); axes[1].set_title("Sales by region")
fig.tight_layout(); fig.savefig(ROOT / "charts" / "category_region.png", dpi=120); plt.close(fig)

fig, ax = plt.subplots(figsize=(10, 4))
for cat, grp in monthly.groupby("Category"):
    ax.plot(pd.to_datetime(grp["month"]), grp["sales"], label=cat, lw=1.3)
ax.set_title("Monthly sales trend by category"); ax.legend(); ax.set_ylabel("units")
fig.tight_layout(); fig.savefig(ROOT / "charts" / "monthly_trend.png", dpi=120); plt.close(fig)

fig, ax = plt.subplots(figsize=(7, 4))
colors = ["#c0392b" if p < 0 else "#27ae60" for p in discount["profit"]]
ax.bar(discount["band"], discount["profit"], color=colors)
ax.set_title("Profit by discount band"); ax.set_ylabel("units")
fig.tight_layout(); fig.savefig(ROOT / "charts" / "discount_profit.png", dpi=120); plt.close(fig)

summary = {"kpis": kpis.to_dict("records")[0],
           "by_region": by_region.to_dict("records"),
           "by_category": by_cat.to_dict("records"),
           "profit_by_discount_band": discount.to_dict("records")}
(ROOT / "results.json").write_text(json.dumps(summary, indent=2, default=str))
print(json.dumps(summary, indent=2, default=str))
