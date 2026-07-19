# ============================================================
# pages.py
# Saare pages ki logic - ek jagah par
# ============================================================

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime

from config import C, F
from auth import logged_user
from database import get_collection
from helpers import get_all_sales, calc_kpis
from ui_components import make_header, white_card, label_entry, styled_btn, kpi_box


# ============================================================
# PAGE 1: DASHBOARD
# ============================================================

def page_dashboard(content):
    """KPI cards + bar chart + pie chart"""
    area    = make_header(content, "📊  Dashboard")
    records = get_all_sales()
    kpis    = calc_kpis(records)

    tk.Label(area, text="Key Performance Indicators",
             font=F["sub"], bg=C["bg"], fg=C["text"]).pack(anchor="w", padx=24, pady=(16, 8))

    kpi_frame = tk.Frame(area, bg=C["bg"])
    kpi_frame.pack(fill="x", padx=16)
    kpi_box(kpi_frame, 0, "💰", "Total Revenue",  f"₹{kpis['revenue']:,.0f}", C["blue"])
    kpi_box(kpi_frame, 1, "📈", "Net Profit",     f"₹{kpis['profit']:,.0f}",  C["green"])
    kpi_box(kpi_frame, 2, "🛒", "Total Orders",   str(kpis["orders"]),          C["purple"])
    kpi_box(kpi_frame, 3, "⭐", "Top Product",    str(kpis["top"])[:14],        C["yellow"])

    if records:
        tk.Label(area, text="Sales Charts", font=F["sub"],
                 bg=C["bg"], fg=C["text"]).pack(anchor="w", padx=24, pady=(20, 8))

        prod_rev = {}; prod_units = {}
        for r in records:
            p = r.get("product", "?")
            prod_rev[p]   = prod_rev.get(p, 0) + r["total"]
            prod_units[p] = prod_units.get(p, 0) + r["units"]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 3.8))
        fig.patch.set_facecolor(C["white"])

        ax1.bar(prod_rev.keys(), prod_rev.values(), color=C["blue"], alpha=0.85, width=0.5)
        ax1.set_title("Product-wise Revenue", fontsize=10, fontweight="bold")
        ax1.set_facecolor(C["bg"])
        ax1.spines["top"].set_visible(False); ax1.spines["right"].set_visible(False)
        ax1.tick_params(axis="x", rotation=25, labelsize=8)
        ax1.set_ylabel("Revenue (₹)", fontsize=8)

        colors_list = [C["blue"], C["green"], C["yellow"], C["red"], C["purple"], "#06B6D4"]
        ax2.pie(prod_units.values(), labels=prod_units.keys(), autopct="%1.1f%%",
                startangle=90, colors=colors_list[:len(prod_units)],
                wedgeprops={"width": 0.6})
        ax2.set_title("Units Distribution", fontsize=10, fontweight="bold")

        plt.tight_layout(pad=1.5)
        canvas = FigureCanvasTkAgg(fig, master=area)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="x", padx=16, pady=8)
        plt.close(fig)
    else:
        tk.Label(area, text="📭  No data available. Please add some sales records first.",
                 font=F["head"], bg=C["bg"], fg="#94A3B8").pack(pady=60)


# ============================================================
# PAGE 2: ADD SALE
# ============================================================

def page_add(content):
    """Naya sale record add karne ka form"""
    area = make_header(content, "➕  Add New Sale")
    card = white_card(area)

    user_store = logged_user.get("store")  # None = superadmin, "Delhi" etc = admin

    # --- Input fields ---
    f_prod  = label_entry(card, "🏷️  Product Name *")
    f_units = label_entry(card, "📦  Units Sold *")
    f_price = label_entry(card, "💰  Selling Price per Unit (₹) *")
    f_cost  = label_entry(card, "🏭  Cost Price per Unit (₹)")
    f_date  = label_entry(card, "📅  Date (YYYY-MM-DD) *")
    f_date.insert(0, datetime.now().strftime("%Y-%m-%d"))

    # Region - admin ke liye locked (apna store), superadmin manually likhega
    lbl_region = "🌍  Region / City (Auto-set)" if user_store else "🌍  Region / City"
    tk.Label(card, text=lbl_region, font=F["small"],
             bg=C["white"], fg=C["subtext"]).pack(anchor="w", padx=20, pady=(10, 2))
    f_region = tk.Entry(card, font=F["body"], relief="solid", bd=1,
                        bg="#E2E8F0" if user_store else C["bg"], fg=C["text"])
    f_region.pack(fill="x", padx=20, ipady=6, pady=(0, 2))
    if user_store:
        f_region.insert(0, user_store)
        f_region.config(state="disabled")   # Admin change nahi kar sakta

    tk.Label(card, text="📂  Category", font=F["small"],
             bg=C["white"], fg=C["subtext"]).pack(anchor="w", padx=20, pady=(10, 2))
    f_cat = ttk.Combobox(card, font=F["body"], state="readonly",
                          values=["Electronics","Clothing","Food",
                                  "Furniture","Books","Sports","Other"])
    f_cat.set("Electronics")
    f_cat.pack(fill="x", padx=20, ipady=4)

    msg_lbl = tk.Label(card, text="", font=F["sub"], bg=C["white"], fg=C["green"])
    msg_lbl.pack(pady=4)

    def clear_fields():
        for field in [f_prod, f_units, f_price, f_cost]:
            field.delete(0, tk.END)
        f_date.delete(0, tk.END)
        f_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        if not user_store:
            f_region.delete(0, tk.END)

    def save_sale():
        col = get_collection()
        try:
            product = f_prod.get().strip()
            units   = int(f_units.get())
            price   = float(f_price.get())
            cost    = float(f_cost.get()) if f_cost.get().strip() else 0.0
            date    = f_date.get().strip()
            region  = user_store if user_store else f_region.get().strip()
            cat     = f_cat.get()

            if not product or not date:
                messagebox.showwarning("Validation Error", "Product name and Date are required!")
                return
            if units <= 0 or price <= 0:
                messagebox.showwarning("Validation Error", "Units and Price must be positive!")
                return

            datetime.strptime(date, "%Y-%m-%d")

            if col.find_one({"product": product, "date": date, "region": region}):
                messagebox.showwarning("Duplicate",
                    f"A record for '{product}' on {date} in {region} already exists!")
                return

            col.insert_one({
                "product":  product, "units": units, "price": price,
                "cost":     cost,    "date":  date,  "region": region,
                "category": cat,     "added_by": logged_user["username"],
                "saved_at": datetime.now().isoformat()
            })
            msg_lbl.config(text=f"✅  Saved! Revenue: ₹{units*price:,.2f}", fg=C["green"])
            clear_fields()

        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input!\n{e}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save.\n{e}")

    btn_row = tk.Frame(card, bg=C["white"])
    btn_row.pack(fill="x", padx=20, pady=(4, 16))
    tk.Button(btn_row, text="✅  Save Record", font=F["btn"],
              bg=C["green"], fg=C["white"], relief="flat", cursor="hand2",
              padx=12, pady=8, command=save_sale).pack(side="left", padx=(0, 8))
    tk.Button(btn_row, text="🔄  Clear", font=F["btn"],
              bg="#94A3B8", fg=C["white"], relief="flat", cursor="hand2",
              padx=12, pady=8, command=clear_fields).pack(side="left")


# ============================================================
# PAGE 3: VIEW RECORDS
# ============================================================

def page_view(content):
    """Saare records table mein dikhao"""
    area    = make_header(content, "📋  All Sales Records")
    records = get_all_sales()

    tk.Label(area, text=f"Total Records: {len(records)}",
             font=F["sub"], bg=C["bg"], fg=C["blue"]).pack(anchor="w", padx=24, pady=(12, 4))

    if not records:
        tk.Label(area, text="📭  No records found.",
                 font=F["head"], bg=C["bg"], fg="#94A3B8").pack(pady=60)
        return

    t_frame = tk.Frame(area, bg=C["white"],
                       highlightbackground=C["border"], highlightthickness=1)
    t_frame.pack(fill="both", expand=True, padx=16, pady=8)

    cols = ["product","units","price","cost","total","profit","date","region","category"]
    col_names = {
        "product":"Product","units":"Units","price":"Price(₹)",
        "cost":"Cost(₹)","total":"Revenue(₹)","profit":"Profit(₹)",
        "date":"Date","region":"Region","category":"Category"
    }
    widths = {"product":120,"units":60,"price":90,"cost":90,
              "total":110,"profit":110,"date":100,"region":90,"category":100}

    tree = ttk.Treeview(t_frame, columns=cols, show="headings")
    y_sc = ttk.Scrollbar(t_frame, orient="vertical",   command=tree.yview)
    x_sc = ttk.Scrollbar(t_frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=y_sc.set, xscrollcommand=x_sc.set)
    y_sc.pack(side="right", fill="y"); x_sc.pack(side="bottom", fill="x")
    tree.pack(fill="both", expand=True)

    for col in cols:
        tree.heading(col, text=col_names[col])
        tree.column(col, width=widths[col], anchor="center")

    for i, r in enumerate(records):
        vals = [r.get("product",""), int(r["units"]),
                f"₹{r['price']:,.2f}", f"₹{r['cost']:,.2f}",
                f"₹{r['total']:,.2f}", f"₹{r['profit']:,.2f}",
                r.get("date",""), r.get("region",""), r.get("category","")]
        tree.insert("", "end", values=vals, tags=("even" if i%2==0 else "odd",))

    tree.tag_configure("even", background=C["white"])
    tree.tag_configure("odd",  background=C["hover"])


# ============================================================
# PAGE 4: SEARCH
# ============================================================

def page_search(content):
    """Product search page"""
    area = make_header(content, "🔍  Search Product")
    card = white_card(area)

    row = tk.Frame(card, bg=C["white"])
    row.pack(fill="x", padx=20, pady=14)
    tk.Label(row, text="Product Name:", font=F["sub"],
             bg=C["white"], fg=C["subtext"]).pack(side="left", padx=(0, 8))
    search_entry = tk.Entry(row, font=F["body"], width=28, relief="solid", bd=1, bg=C["bg"])
    search_entry.pack(side="left", ipady=6)

    result_area = tk.Frame(card, bg=C["white"])
    result_area.pack(fill="both", expand=True, padx=20, pady=(0, 16))

    def do_search():
        for w in result_area.winfo_children():
            w.destroy()
        query   = search_entry.get().strip().lower()
        records = get_all_sales()
        results = [r for r in records if query in r.get("product","").lower()] if query else records

        if not results:
            tk.Label(result_area, text=f"❌  No results for '{query}'",
                     font=F["head"], bg=C["white"], fg=C["red"]).pack(pady=20)
            return

        total_rev  = sum(r["total"]  for r in results)
        total_prof = sum(r["profit"] for r in results)
        total_unit = sum(r["units"]  for r in results)

        summary = tk.Frame(result_area, bg=C["white"])
        summary.pack(fill="x", pady=8)
        for txt, col in [
            (f"✅  {len(results)} Records", C["green"]),
            (f"Revenue: ₹{total_rev:,.2f}", C["blue"]),
            (f"Profit: ₹{total_prof:,.2f}", C["purple"]),
            (f"Units: {int(total_unit)}", C["yellow"]),
        ]:
            tk.Label(summary, text=txt, font=F["sub"],
                     bg=C["white"], fg=col).pack(side="left", padx=12)

        s_cols = ["product","units","price","total","profit","date"]
        tree = ttk.Treeview(result_area, columns=s_cols, show="headings", height=8)
        for col in s_cols:
            tree.heading(col, text=col.capitalize())
            tree.column(col, width=110, anchor="center")
        for r in results:
            tree.insert("", "end", values=[
                r.get("product",""), int(r["units"]),
                f"₹{r['price']:,.2f}", f"₹{r['total']:,.2f}",
                f"₹{r['profit']:,.2f}", r.get("date","")
            ])
        tree.pack(fill="x", pady=8)

    def show_all():
        search_entry.delete(0, tk.END)
        do_search()

    tk.Button(row, text=" Search 🔍", font=F["btn"],
              bg=C["blue"], fg=C["white"], relief="flat", cursor="hand2",
              padx=12, pady=6, command=do_search).pack(side="left", padx=8)
    tk.Button(row, text="Show All", font=F["small"],
              bg="#94A3B8", fg=C["white"], relief="flat", cursor="hand2",
              padx=8, pady=6, command=show_all).pack(side="left")


# ============================================================
# PAGE 5: UPDATE PRICE
# ============================================================

def page_update(content):
    """Product ki price update karo"""
    area = make_header(content, "✏️  Update Product Price")
    card = white_card(area)

    u_prod  = label_entry(card, "🏷️  Product Name (exact)")
    u_price = label_entry(card, "💰  New Selling Price (₹)")

    msg_lbl = tk.Label(card, text="", font=F["sub"], bg=C["white"], fg=C["green"])
    msg_lbl.pack(pady=4)

    def do_update():
        col       = get_collection()
        product   = u_prod.get().strip()
        new_price = u_price.get().strip()
        if not product or not new_price:
            messagebox.showwarning("Warning", "Please enter both fields!")
            return
        try:
            new_price = float(new_price)
            result = col.update_many({"product": product}, {"$set": {"price": new_price}})
            if result.modified_count > 0:
                msg_lbl.config(
                    text=f"✅  {result.modified_count} record(s) updated! New Price: ₹{new_price:,.2f}",
                    fg=C["green"])
            else:
                msg_lbl.config(text="⚠️  No matching records found", fg=C["yellow"])
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid number for Price!")

    styled_btn(card, "✏️  Update Price", do_update, C["yellow"])
    tk.Label(card, text="", bg=C["white"]).pack(pady=8)


# ============================================================
# PAGE 6: DELETE
# ============================================================

def page_delete(content):
    """Record delete karo - with warning"""
    area = make_header(content, "🗑️  Delete Record")
    card = tk.Frame(area, bg=C["white"],
                    highlightbackground=C["red"], highlightthickness=2)
    card.pack(fill="x", padx=16, pady=8)

    warn = tk.Frame(card, bg="#FFF5F5")
    warn.pack(fill="x", padx=20, pady=12)
    tk.Label(warn, text="⚠️  Warning: Deleted records cannot be recovered!",
             font=F["small"], bg="#FFF5F5", fg=C["red"]).pack(padx=12, pady=8)

    d_prod = label_entry(card, "🏷️  Product Name")
    d_date = label_entry(card, "📅  Date (optional - blank = delete all for product)")

    msg_lbl = tk.Label(card, text="", font=F["sub"], bg=C["white"], fg=C["red"])
    msg_lbl.pack(pady=4)

    def do_delete():
        col     = get_collection()
        product = d_prod.get().strip()
        date    = d_date.get().strip()
        if not product:
            messagebox.showwarning("Warning", "Product Name is required!")
            return
        confirm = messagebox.askyesno("⚠️  Confirm Delete",
            f"Delete '{product}' {'(' + date + ')' if date else '(ALL records)'}?\n\nThis cannot be undone!")
        if not confirm:
            return
        query = {"product": product}
        if date:
            query["date"] = date
        result = col.delete_many(query)
        if result.deleted_count > 0:
            msg_lbl.config(text=f"🗑️  {result.deleted_count} record(s) deleted!", fg=C["red"])
        else:
            msg_lbl.config(text="⚠️  No matching records found", fg=C["yellow"])

    styled_btn(card, "🗑️  Delete Record", do_delete, C["red"])
    tk.Label(card, text="", bg=C["white"]).pack(pady=8)


# ============================================================
# PAGE 7: ANALYTICS
# ============================================================

def page_analytics(content):
    """4 charts - bar, donut pie, line trend, area overlap"""
    area    = make_header(content, "📈  Sales Analytics")
    records = get_all_sales()

    if not records:
        tk.Label(area, text="📭  No data available.",
                 font=F["head"], bg=C["bg"], fg="#B8949A").pack(pady=80)
        return

    prod_rev = {}; prod_units = {}; daily_rev = {}; daily_prof = {}
    for r in records:
        p = r.get("product","?")
        prod_rev[p]   = prod_rev.get(p, 0) + r["total"]
        prod_units[p] = prod_units.get(p, 0) + r["units"]
        d = r.get("date","")
        if d:
            daily_rev[d]  = daily_rev.get(d, 0) + r["total"]
            daily_prof[d] = daily_prof.get(d, 0) + r["profit"]

    dates     = sorted(daily_rev.keys())
    rev_vals  = [daily_rev[d]  for d in dates]
    prof_vals = [daily_prof[d] for d in dates]
    palette   = [C["blue"], C["green"], C["yellow"], C["red"], C["purple"], "#06D40D"]

    fig, axes = plt.subplots(2, 2, figsize=(13, 8))
    fig.patch.set_facecolor(C["white"])
    fig.suptitle("Sales Analytics Dashboard", fontsize=12, fontweight="bold", color=C["text"])

    ax1 = axes[0][0]
    ax1.bar(prod_rev.keys(), prod_rev.values(), color=palette[:len(prod_rev)], alpha=0.85, width=0.5)
    ax1.set_title("Product-wise Revenue", fontsize=10, fontweight="bold")
    ax1.set_facecolor(C["bg"]); ax1.spines["top"].set_visible(False); ax1.spines["right"].set_visible(False)
    ax1.tick_params(axis="x", rotation=25, labelsize=8); ax1.set_ylabel("Revenue (₹)", fontsize=8)

    ax2 = axes[0][1]
    ax2.pie(prod_units.values(), labels=prod_units.keys(), autopct="%1.1f%%",
            startangle=90, colors=palette[:len(prod_units)], wedgeprops={"width": 0.55})
    ax2.set_title("Units Distribution", fontsize=10, fontweight="bold")

    ax3 = axes[1][0]
    if len(dates) > 1:
        ax3.plot(dates, rev_vals, color=C["blue"], linewidth=2,
                 marker="o", markersize=4, markerfacecolor=C["green"])
        ax3.fill_between(dates, rev_vals, alpha=0.15, color=C["blue"])
    ax3.set_title("Daily Revenue Trend", fontsize=10, fontweight="bold")
    ax3.set_facecolor(C["bg"]); ax3.spines["top"].set_visible(False); ax3.spines["right"].set_visible(False)
    ax3.tick_params(axis="x", rotation=30, labelsize=7); ax3.set_ylabel("Revenue (₹)", fontsize=8)

    ax4 = axes[1][1]
    if len(dates) > 1:
        ax4.fill_between(dates, rev_vals,  alpha=0.3, color=C["blue"],  label="Revenue")
        ax4.fill_between(dates, prof_vals, alpha=0.5, color=C["green"], label="Profit")
        ax4.plot(dates, rev_vals,  color=C["blue"],  linewidth=1.5)
        ax4.plot(dates, prof_vals, color=C["green"], linewidth=1.5)
        ax4.legend(fontsize=8)
    ax4.set_title("Revenue vs Profit", fontsize=10, fontweight="bold")
    ax4.set_facecolor(C["bg"]); ax4.spines["top"].set_visible(False); ax4.spines["right"].set_visible(False)
    ax4.tick_params(axis="x", rotation=30, labelsize=7)

    plt.tight_layout(pad=2)
    canvas = FigureCanvasTkAgg(fig, master=area)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True, padx=16, pady=8)
    plt.close(fig)


# ============================================================
# PAGE 8: PROFIT & LOSS
# ============================================================

def page_profit(content):
    """Overall P&L summary + per-product table"""
    area    = make_header(content, "📉  Profit & Loss")
    records = get_all_sales()

    if not records:
        tk.Label(area, text="📭  No data available.",
                 font=F["head"], bg=C["bg"], fg="#94A3B8").pack(pady=80)
        return

    total_rev  = sum(r["total"]             for r in records)
    total_cost = sum(r["units"] * r["cost"] for r in records)
    total_prof = sum(r["profit"]            for r in records)
    margin     = (total_prof / total_rev * 100) if total_rev > 0 else 0

    tk.Label(area, text="Summary", font=F["sub"],
             bg=C["bg"], fg=C["text"]).pack(anchor="w", padx=24, pady=(16, 8))
    summary = tk.Frame(area, bg=C["bg"])
    summary.pack(fill="x", padx=16)
    for i, (lbl, val, col) in enumerate([
        ("💰  Total Revenue", f"₹{total_rev:,.2f}",  C["blue"]),
        ("🏭  Total Cost",    f"₹{total_cost:,.2f}", C["yellow"]),
        ("📈  Net Profit",    f"₹{total_prof:,.2f}", C["green"] if total_prof >= 0 else C["red"]),
        ("📊  Margin",        f"{margin:.1f}%",       C["purple"]),
    ]):
        kpi_box(summary, i, "", lbl, val, col)

    tk.Label(area, text="Product-wise Profit & Loss", font=F["sub"],
             bg=C["bg"], fg=C["text"]).pack(anchor="w", padx=24, pady=(20, 8))

    prod_data = {}
    for r in records:
        p = r.get("product","?")
        if p not in prod_data:
            prod_data[p] = {"units": 0, "revenue": 0, "profit": 0}
        prod_data[p]["units"]   += r["units"]
        prod_data[p]["revenue"] += r["total"]
        prod_data[p]["profit"]  += r["profit"]

    p_cols = ["Product","Units","Revenue(₹)","Profit(₹)","Margin%"]
    tree = ttk.Treeview(area, columns=p_cols, show="headings", height=12)
    for col, w in zip(p_cols, [140, 80, 130, 130, 90]):
        tree.heading(col, text=col); tree.column(col, width=w, anchor="center")

    for prod, d in sorted(prod_data.items(), key=lambda x: x[1]["profit"], reverse=True):
        mg  = (d["profit"] / d["revenue"] * 100) if d["revenue"] > 0 else 0
        tag = "profit" if d["profit"] >= 0 else "loss"
        tree.insert("", "end", values=[
            prod, int(d["units"]),
            f"₹{d['revenue']:,.2f}", f"₹{d['profit']:,.2f}", f"{mg:.1f}%"
        ], tags=(tag,))

    tree.tag_configure("profit", foreground=C["green"])
    tree.tag_configure("loss",   foreground=C["red"])
    tree.pack(fill="both", expand=True, padx=16, pady=(0, 16))


# ============================================================
# PAGE 9: EXPORT CSV
# ============================================================

def page_export(content):
    """Data ko CSV file mein export karo"""
    area = make_header(content, "📤  Export Data")
    card = white_card(area)

    exp_msg = tk.Label(card, text="", font=F["sub"], bg=C["white"], fg=C["green"])
    exp_msg.pack(pady=(16, 4))

    def export_full():
        records = get_all_sales()
        if not records:
            messagebox.showwarning("Warning", "No data to export!")
            return
        fname   = f"sales_full_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        headers = ["product","units","price","cost","total","profit","date","region","category"]
        with open(fname, "w") as f:
            f.write(",".join(headers) + "\n")
            for r in records:
                f.write(",".join([str(r.get(h,"")) for h in headers]) + "\n")
        exp_msg.config(text=f"✅  Exported: {fname}", fg=C["green"])

    def export_summary():
        records = get_all_sales()
        if not records:
            return
        prod_data = {}
        for r in records:
            p = r.get("product","?")
            if p not in prod_data:
                prod_data[p] = {"units": 0, "revenue": 0, "profit": 0}
            prod_data[p]["units"]   += r["units"]
            prod_data[p]["revenue"] += r["total"]
            prod_data[p]["profit"]  += r["profit"]
        fname = f"sales_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(fname, "w") as f:
            f.write("product,units,revenue,profit\n")
            for p, d in prod_data.items():
                f.write(f"{p},{int(d['units'])},{d['revenue']:.2f},{d['profit']:.2f}\n")
        exp_msg.config(text=f"✅  Summary Exported: {fname}", fg=C["green"])

    styled_btn(card, "📥  Export Full Data (CSV)", export_full, C["blue"])
    styled_btn(card, "📊  Export Summary (CSV)", export_summary, C["purple"])
    tk.Label(card, text="Files current folder mein save hongi.",
             font=F["small"], bg=C["white"], fg="#94A3B8").pack(pady=(0, 16))


# ============================================================
# PAGE 10: IMPORT CSV
# ============================================================

def page_import_csv(content):
    """CSV file se bulk data import karo"""
    area = make_header(content, "📥  Import CSV Data")

    # --- Instructions card ---
    info = tk.Frame(area, bg="#EFF6FF", highlightbackground=C["blue"], highlightthickness=1)
    info.pack(fill="x", padx=16, pady=(12, 4))
    tk.Label(info, text="📋  How to Import:",
             font=F["sub"], bg="#EFF6FF", fg=C["blue"]).pack(anchor="w", padx=16, pady=(10, 2))
    for s in [
        "1.  Fill data in Excel (product, units, price, date are required)",
        "2.  Save as CSV  (File → Save As → CSV)",
        "3.  Click 'Browse & Import CSV' and select your file",
        "4.  Done! Data will appear in Dashboard instantly.",
    ]:
        tk.Label(info, text=s, font=F["body"],
                 bg="#EFF6FF", fg=C["text"]).pack(anchor="w", padx=24, pady=1)
    tk.Label(info, text="", bg="#EFF6FF").pack(pady=4)

    # --- Required columns card ---
    req_card = white_card(area)
    tk.Label(req_card, text="Required CSV Columns:",
             font=F["sub"], bg=C["white"], fg=C["text"]).pack(anchor="w", padx=20, pady=(12, 4))
    col_info = tk.Frame(req_card, bg=C["white"])
    col_info.pack(fill="x", padx=20, pady=(0, 12))
    for i, (col, color, note) in enumerate([
        ("product",  C["blue"],  "Required"),
        ("units",    C["blue"],  "Required"),
        ("price",    C["blue"],  "Required"),
        ("date",     C["blue"],  "Required (YYYY-MM-DD)"),
        ("cost",     C["green"], "Optional"),
        ("region",   C["green"], "Optional"),
        ("category", C["green"], "Optional"),
    ]):
        tk.Label(col_info, text=f"  {col}", font=F["btn"], bg=C["white"],
                 fg=color).grid(row=i//4, column=(i%4)*2, padx=(0,2), pady=2, sticky="w")
        tk.Label(col_info, text=f"({note})", font=F["small"], bg=C["white"],
                 fg=C["subtext"]).grid(row=i//4, column=(i%4)*2+1, padx=(0,16), pady=2, sticky="w")

    imp_msg = tk.Label(area, text="", font=F["sub"], bg=C["bg"], fg=C["green"])
    imp_msg.pack(pady=8)

    # --- Import log table ---
    tk.Label(area, text="Import Log", font=F["sub"],
             bg=C["bg"], fg=C["text"]).pack(anchor="w", padx=24, pady=(12, 4))
    log_frame = tk.Frame(area, bg=C["white"],
                         highlightbackground=C["border"], highlightthickness=1)
    log_frame.pack(fill="both", expand=True, padx=16, pady=(0, 4))

    log_cols = ["#","Product","Units","Price","Date","Status"]
    imp_tree = ttk.Treeview(log_frame, columns=log_cols, show="headings", height=8)
    log_sc   = ttk.Scrollbar(log_frame, orient="vertical", command=imp_tree.yview)
    imp_tree.configure(yscrollcommand=log_sc.set)
    log_sc.pack(side="right", fill="y"); imp_tree.pack(fill="both", expand=True)
    for col, w in zip(log_cols, [40, 140, 70, 100, 100, 140]):
        imp_tree.heading(col, text=col); imp_tree.column(col, width=w, anchor="center")
    imp_tree.tag_configure("ok",   foreground=C["green"])
    imp_tree.tag_configure("skip", foreground=C["yellow"])
    imp_tree.tag_configure("err",  foreground=C["red"])

    def do_import_csv():
        col = get_collection()
        filepath = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if not filepath:
            return
        for row in imp_tree.get_children():
            imp_tree.delete(row)

        imported = 0; skipped = 0; errors = 0
        try:
            with open(filepath, "r", encoding="utf-8-sig") as f:
                headers = [h.strip().lower() for h in f.readline().split(",")]
                for line_num, line in enumerate(f, start=2):
                    line = line.strip()
                    if not line:
                        continue
                    values  = [v.strip().strip('"') for v in line.split(",")]
                    row_map = dict(zip(headers, values))
                    product = row_map.get("product","").strip()
                    date    = row_map.get("date","").strip()

                    if not product or not date:
                        errors += 1
                        imp_tree.insert("","end",values=[line_num,product or "?","-","-",date or "?","❌ Missing field"],tags=("err",))
                        continue
                    try:
                        datetime.strptime(date, "%Y-%m-%d")
                    except ValueError:
                        errors += 1
                        imp_tree.insert("","end",values=[line_num,product,"-","-",date,"❌ Wrong date format"],tags=("err",))
                        continue
                    try:
                        units = float(row_map.get("units",0) or 0)
                        price = float(row_map.get("price",0) or 0)
                        cost  = float(row_map.get("cost", 0) or 0)
                    except ValueError:
                        errors += 1
                        imp_tree.insert("","end",values=[line_num,product,"?","?",date,"❌ Invalid number"],tags=("err",))
                        continue
                    if col is not None and col.find_one({"product": product, "date": date}):
                        skipped += 1
                        imp_tree.insert("","end",values=[line_num,product,int(units),f"₹{price:,.0f}",date,"⚠️ Duplicate"],tags=("skip",))
                        continue
                    if col is not None:
                        col.insert_one({
                            "product":  product, "units": units, "price": price, "cost": cost,
                            "date":     date,    "region": row_map.get("region","").strip(),
                            "category": row_map.get("category","Other").strip() or "Other",
                            "added_by": logged_user["username"],
                            "saved_at": datetime.now().isoformat(),
                        })
                        imported += 1
                        imp_tree.insert("","end",values=[line_num,product,int(units),f"₹{price:,.0f}",date,"✅ Imported"],tags=("ok",))

            imp_msg.config(
                text=f"✅  Done!  Imported: {imported}  |  Skipped: {skipped}  |  Errors: {errors}",
                fg=C["green"] if errors == 0 else C["yellow"])
            if imported > 0:
                messagebox.showinfo("Import Done",
                    f"✅ Imported: {imported}\n⚠️ Skipped: {skipped}\n❌ Errors: {errors}\n\nGo to Dashboard!")
        except Exception as e:
            messagebox.showerror("Import Error", f"Could not read CSV.\n\n{e}")

    def clear_all_data():
        col = get_collection()
        if not messagebox.askyesno("⚠️  Clear All", "Delete ALL sales records permanently?"):
            return
        if not messagebox.askyesno("⚠️  Final Confirm", "Last warning! ALL data will be erased. Continue?"):
            return
        if col is not None:
            result = col.delete_many({})
            messagebox.showinfo("Done", f"✅  {result.deleted_count} records deleted.")
            imp_msg.config(text=f"🗑️  {result.deleted_count} records cleared.", fg=C["red"])

    btn_card = white_card(area)
    btn_row  = tk.Frame(btn_card, bg=C["white"])
    btn_row.pack(padx=20, pady=16)
    tk.Button(btn_row, text="📥  Browse & Import CSV",
              font=F["btn"], bg=C["blue"], fg=C["white"], relief="flat", cursor="hand2",
              padx=16, pady=10, command=do_import_csv).pack(side="left", padx=(0,12))
    tk.Button(btn_row, text="🔄  Clear All Data (Reset DB)",
              font=F["btn"], bg=C["red"], fg=C["white"], relief="flat", cursor="hand2",
              padx=16, pady=10, command=clear_all_data).pack(side="left")