# Sales & Market Analysis (SQL Server + Power BI)

Sales and product analysis with advanced SQL (joins, aggregations, subqueries) feeding Power BI dashboards with drill-through views.

> **Provenance:** Rebuilt in November 2026 after the original project files were lost. All numbers below were measured on this rebuild against the public dataset named here.

> **Power BI note:** this repo ships the real dataset, the DAX measures, the Power Query steps, and a runnable verified companion analysis (charts in `charts/`). A native `.pbix` file cannot be authored on Linux; open the dataset in Power BI Desktop and apply `dax/measures.dax` + `powerquery/steps.pq` to reproduce the dashboard in minutes.

## Dataset
Sample Superstore (public), `data/superstore.csv`: 9,994 order lines, 793 customers, 2015-2018. The source mirror bundles three tables; this repo uses the orders table (documented cleaning in `src/`). Amounts are shown as USD: the sample dataset is US-based but states no currency explicitly. Substitute dataset; the original data was lost.

## SQL
`sql/analysis.sql` - five T-SQL queries (SQL Server): category/sub-category drill-through, regional share via subquery, top-5 customers per segment via window function, monthly trend by category, loss-making discount bands.

## Measured results (this rebuild, logic validated with DuckDB)
- Total sales **USD 2,297,201**, profit **USD 286,397** (12.5% margin)
- West leads with 31.6% of sales; Technology is the top category ($836K)
- High discounts destroy profit: -$99.6K in the high-discount band vs +$321K at no discount
- Charts (verified): `charts/category_region.png`, `charts/monthly_trend.png`, `charts/discount_profit.png`

## Run
```bash
pip install -r requirements.txt
python src/build_dashboard_data.py
```
