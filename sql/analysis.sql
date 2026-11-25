-- Sales & Market Analysis - SQL Server (T-SQL) analysis queries
-- Rebuild (Nov 2026). Dataset: Sample Superstore (public), ~10K order lines.
-- Joins, aggregations and subqueries over sales and product data, feeding
-- Power BI drill-through views. Validated logically against DuckDB (see src/).

-- 1) Revenue and profit by category / sub-category (drill-through target)
SELECT Category, [Sub-Category],
       SUM(Sales) AS total_sales, SUM(Profit) AS total_profit,
       CAST(SUM(Profit) / NULLIF(SUM(Sales), 0) AS DECIMAL(10,4)) AS profit_margin
FROM superstore
GROUP BY Category, [Sub-Category]
ORDER BY total_sales DESC;

-- 2) Regional performance with running share (aggregation + subquery)
SELECT Region,
       SUM(Sales) AS total_sales,
       CAST(SUM(Sales) / (SELECT SUM(Sales) FROM superstore) AS DECIMAL(10,4)) AS sales_share
FROM superstore
GROUP BY Region
ORDER BY total_sales DESC;

-- 3) Top customers per segment (join + window subquery)
SELECT segment, customer_name, total_spend FROM (
  SELECT Segment AS segment, [Customer Name] AS customer_name, SUM(Sales) AS total_spend,
         ROW_NUMBER() OVER (PARTITION BY Segment ORDER BY SUM(Sales) DESC) AS rn
  FROM superstore
  GROUP BY Segment, [Customer Name]
) t
WHERE rn <= 5
ORDER BY segment, total_spend DESC;

-- 4) Monthly trend by category (aggregation for drill-through time view)
SELECT YEAR([Order Date]) AS order_year, MONTH([Order Date]) AS order_month,
       Category, SUM(Sales) AS monthly_sales
FROM superstore
GROUP BY YEAR([Order Date]), MONTH([Order Date]), Category
ORDER BY order_year, order_month, Category;

-- 5) Loss-making sub-categories by discount band (subquery filter)
SELECT discount_band, [Sub-Category], SUM(Profit) AS profit FROM (
  SELECT [Sub-Category], Profit,
         CASE WHEN Discount = 0 THEN 'none' WHEN Discount <= 0.2 THEN 'low'
              WHEN Discount <= 0.4 THEN 'mid' ELSE 'high' END AS discount_band
  FROM superstore
) d
GROUP BY discount_band, [Sub-Category]
HAVING SUM(Profit) < 0
ORDER BY profit;
