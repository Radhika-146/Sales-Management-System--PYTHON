# ============================================================
# helpers.py
# Data fetch karna aur calculations - UI se alag
# Ab role ke hisaab se filter hoga
# ============================================================

from database import get_collection
from auth import get_store_filter


def get_all_sales():
    """
    MongoDB se records fetch karo.
    Admin      → sirf apne store ke records
    Superadmin → sab records
    """
    col = get_collection()
    if col is None:
        return []

    query = get_store_filter()          # {} ya {"region": "Delhi"} etc.
    records = list(col.find(query, {"_id": 0}))

    for r in records:
        r["units"]  = float(r.get("units", 0))
        r["price"]  = float(r.get("price", 0))
        r["cost"]   = float(r.get("cost",  0))
        r["total"]  = r["units"] * r["price"]
        r["profit"] = r["total"] - (r["units"] * r["cost"])
    return records


def calc_kpis(records):
    """KPIs calculate karo - Revenue, Profit, Orders, Top Product"""
    if not records:
        return {"revenue": 0, "profit": 0, "orders": 0, "top": "N/A", "avg": 0}

    revenue = sum(r["total"]  for r in records)
    profit  = sum(r["profit"] for r in records)
    orders  = len(records)
    avg     = revenue / orders if orders > 0 else 0

    prod_rev = {}
    for r in records:
        p = r.get("product", "")
        prod_rev[p] = prod_rev.get(p, 0) + r["total"]

    top = max(prod_rev, key=prod_rev.get) if prod_rev else "N/A"

    return {"revenue": revenue, "profit": profit, "orders": orders, "top": top, "avg": avg}