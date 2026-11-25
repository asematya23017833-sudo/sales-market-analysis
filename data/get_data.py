"""Download the Sample Superstore dataset and produce data/superstore.csv.
The public mirror file concatenates two tables (orders + a People lookup);
this script keeps only the 9,994 orders-table rows analyzed in this repo.
Mirror: https://github.com/leonism/sample-superstore (byte-identical to the
file originally analyzed, md5-checked below).
"""
import csv
import hashlib
import urllib.request
from pathlib import Path

URL = "https://raw.githubusercontent.com/leonism/sample-superstore/master/data/superstore.csv"
MD5 = "badd588d3d65617f3201f4b110590cfd"

here = Path(__file__).resolve().parent
full = here / "superstore_full.csv"
out = here / "superstore.csv"
if not full.exists():
    print("downloading mirror file ...")
    urllib.request.urlretrieve(URL, full)
assert hashlib.md5(full.read_bytes()).hexdigest() == MD5, "checksum mismatch"

rows = list(csv.reader(full.read_text().splitlines()))
header, data = rows[0], rows[1:]
orders = [r for r in data if r and r[0].strip().isdigit()]  # drop the appended People table
assert len(orders) == 9994, f"expected 9,994 order lines, got {len(orders)}"
with out.open("w", newline="") as f:
    w = csv.writer(f); w.writerow(header); w.writerows(orders)
print(f"superstore.csv written: {len(orders):,} order lines")
