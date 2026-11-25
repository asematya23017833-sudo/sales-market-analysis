"""Sales & Market Analysis - Streamlit companion app (rebuild, Nov 2026).
Dataset: Sample Superstore (public substitute dataset). SQL in sql/analysis.sql.
"""
import pathlib
import subprocess
import sys

if not (pathlib.Path(__file__).parent / "data" / "superstore.csv").exists():
    subprocess.run([sys.executable, str(pathlib.Path(__file__).parent / "data" / "get_data.py")], check=True)

import duckdb
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Sales & Market Analysis", layout="wide")
st.title("Sales & Market Analysis")
st.caption("Sample Superstore, public dataset - 9,994 order lines, 2015-2018. Rebuild Nov 2026. SQL Server queries in sql/analysis.sql. Amounts shown in units; the data states no currency.")

@st.cache_data
def load():
    con = duckdb.connect()
    con.execute("""CREATE VIEW s AS SELECT "Category", "Sub-Category" sub, Region, Segment,
        Sales, Profit, Discount, CAST("Order Date" AS DATE) d FROM read_csv_auto('data/superstore.csv')""")
    kpi = con.execute("SELECT COUNT(*) n, SUM(Sales) s, SUM(Profit) p FROM s").df()
    cat = con.execute("SELECT \"Category\" c, SUM(Sales) v, SUM(Profit) p FROM s GROUP BY 1 ORDER BY 2 DESC").df()
    reg = con.execute("SELECT Region c, SUM(Sales) v FROM s GROUP BY 1 ORDER BY 2 DESC").df()
    mon = con.execute("SELECT DATE_TRUNC('month', d) m, \"Category\" c, SUM(Sales) v FROM s GROUP BY 1,2 ORDER BY 1").df()
    disc = con.execute("""SELECT CASE WHEN Discount=0 THEN 'none' WHEN Discount<=0.2 THEN 'low'
        WHEN Discount<=0.4 THEN 'mid' ELSE 'high' END b, SUM(Profit) v FROM s GROUP BY 1""").df()
    return kpi, cat, reg, mon, disc

kpi, cat, reg, mon, disc = load()
c1, c2, c3 = st.columns(3)
c1.metric("Order lines", f"{int(kpi['n'][0]):,}")
c2.metric("Sales (units)", f"{kpi['s'][0]:,.0f}")
c3.metric("Profit (units)", f"{kpi['p'][0]:,.0f}")
left, right = st.columns(2)
left.subheader("Sales by category"); left.bar_chart(cat.set_index("c")["v"])
right.subheader("Sales by region"); right.bar_chart(reg.set_index("c"))
st.subheader("Monthly sales by category")
st.line_chart(mon.pivot(index="m", columns="c", values="v"))
st.subheader("Profit by discount band")
st.bar_chart(disc.set_index("b"))
