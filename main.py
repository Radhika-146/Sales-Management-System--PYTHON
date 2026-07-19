# ============================================================
# main.py  ← SIRF YAHI FILE RUN KARO
# Sab files ko import karke poora app chalata hai
#
# File Structure:
#   main.py          ← Yahan se run karo
#   config.py        ← Colors & Fonts
#   database.py      ← MongoDB connection
#   auth.py          ← Users & Login logic
#   helpers.py       ← Data fetch & KPI calculations
#   ui_components.py ← Reusable UI widgets
#   pages.py         ← Saare pages (Dashboard, Add, View, etc.)
# ============================================================

import tkinter as tk
from tkinter import messagebox

# --- Apni files import karo ---
from config import C, F
from database import connect_db
from auth import logged_user, check_login, logout_user
from pages import (
    page_dashboard, page_add, page_view, page_search,
    page_update, page_delete, page_analytics,
    page_profit, page_export, page_import_csv
)


# ============================================================
# LOGIN WINDOW
# ============================================================

class LoginWindow:
    """Pehle login screen dikhao"""

    def __init__(self, on_success):
        self.on_success = on_success        # Login ke baad callback

        self.win = tk.Tk()
        self.win.title("Sales Pro - Login")
        self.win.geometry("420x500")
        self.win.resizable(False, False)
        self.win.configure(bg=C["sidebar"])
        self.win.eval('tk::PlaceWindow . center')

        tk.Label(self.win, text="📊 Sales Pro",
                 font=F["title"], bg=C["sidebar"], fg=C["white"]).pack(pady=(50, 4))
        tk.Label(self.win, text="Sales Management System",
                 font=F["small"], bg=C["sidebar"], fg="#94A3B8").pack()

        # --- White login card ---
        card = tk.Frame(self.win, bg=C["white"], padx=30, pady=30)
        card.pack(fill="x", padx=40, pady=30)

        tk.Label(card, text="Username", font=F["small"],
                 bg=C["white"], fg=C["subtext"]).pack(anchor="w")
        self.e_user = tk.Entry(card, font=F["body"], relief="solid", bd=1)
        self.e_user.pack(fill="x", ipady=6, pady=(2, 12))

        tk.Label(card, text="Password", font=F["small"],
                 bg=C["white"], fg=C["subtext"]).pack(anchor="w")
        self.e_pass = tk.Entry(card, font=F["body"], relief="solid", bd=1, show="*")
        self.e_pass.pack(fill="x", ipady=6, pady=(2, 16))

        tk.Button(card, text="Login →", font=F["btn"],
                  bg=C["blue"], fg=C["white"], relief="flat",
                  cursor="hand2", padx=10, pady=8,
                  command=self.do_login).pack(fill="x")

        self.win.bind("<Return>", lambda e: self.do_login())

        tk.Label(self.win,
                 text="admin/admin123 (Delhi)  |  admin2/admin456 (Mumbai)  |  superadmin/super123 (All)",
                 font=F["small"], bg=C["sidebar"], fg="#64748B").pack()

        self.win.mainloop()

    def do_login(self):
        username = self.e_user.get().strip()
        password = self.e_pass.get().strip()

        if check_login(username, password):
            self.win.destroy()
            self.on_success()               # Main window kholo
        else:
            messagebox.showerror("Login Failed",
                "Invalid username or password!\n\nDefault credentials:\n  admin / admin123\n  superadmin / super123",
                parent=self.win)


# ============================================================
# MAIN APPLICATION WINDOW
# ============================================================

class MainApp:
    """Login ke baad main window"""

    # Page name → function mapping
    PAGE_MAP = {
        "dashboard":  page_dashboard,
        "add":        page_add,
        "view":       page_view,
        "search":     page_search,
        "update":     page_update,
        "delete":     page_delete,
        "analytics":  page_analytics,
        "profit":     page_profit,
        "export":     page_export,
        "import_csv": page_import_csv,
    }

    # Sidebar buttons
    NAV_ITEMS = [
        ("🏠  Dashboard",    "dashboard"),
        ("➕  Add Sale",     "add"),
        ("📋  View Records", "view"),
        ("🔍  Search",       "search"),
        ("✏️  Update Price", "update"),
        ("🗑️  Delete",       "delete"),
        ("📈  Analytics",    "analytics"),
        ("📉  Profit/Loss",  "profit"),
        ("📤  Export CSV",   "export"),
        ("📥  Import CSV",   "import_csv"),
    ]

    def __init__(self):
        self.current_page = "dashboard"
        self.nav_btns     = {}
        self._build_window()

    def _build_window(self):
        self.root = tk.Tk()
        self.root.title(f"Sales Pro  |  {logged_user['name']}  |  {logged_user['role']}")
        self.root.geometry("1100x680")
        self.root.configure(bg=C["bg"])
        self.root.state("zoomed")

        # --- Sidebar ---
        sidebar = tk.Frame(self.root, bg=C["sidebar"], width=200)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # --- Content area ---
        self.content = tk.Frame(self.root, bg=C["bg"])
        self.content.pack(side="right", fill="both", expand=True)

        tk.Label(sidebar, text="📊 Sales Pro", font=F["sub"],
                 bg=C["sidebar"], fg=C["white"]).pack(pady=(20, 4))
        tk.Label(sidebar, text=logged_user["role"], font=F["small"],
                 bg=C["sidebar"], fg="#94A3B8").pack(pady=(0, 16))
        tk.Frame(sidebar, bg="#2D4270", height=1).pack(fill="x")

        for label, page in self.NAV_ITEMS:
            btn = tk.Button(sidebar, text=label, font=F["btn"],
                            bg=C["sidebar"], fg=C["white"],
                            relief="flat", anchor="w", padx=16, pady=8,
                            cursor="hand2",
                            command=lambda p=page: self.navigate(p))
            btn.pack(fill="x")
            btn.bind("<Enter>",  lambda e, b=btn: b.config(bg="#2D4270"))
            btn.bind("<Leave>",  lambda e, b=btn, pg=page:
                     b.config(bg=C["blue"] if self.current_page == pg else C["sidebar"]))
            self.nav_btns[page] = btn

        tk.Frame(sidebar, bg="#2D4270", height=1).pack(fill="x", side="bottom", pady=4)
        tk.Button(sidebar, text="🚪  Logout", font=F["small"],
                  bg=C["sidebar"], fg="#94A3B8", relief="flat",
                  cursor="hand2", pady=8,
                  command=self.logout).pack(side="bottom", fill="x")

        self.navigate("dashboard")
        self.root.mainloop()

    def navigate(self, page):
        """Page switch karo - content clear karo, naya page load karo"""
        self.current_page = page
        for p, btn in self.nav_btns.items():
            btn.config(bg=C["blue"] if p == page else C["sidebar"])
        for widget in self.content.winfo_children():
            widget.destroy()
        if page in self.PAGE_MAP:
            self.PAGE_MAP[page](self.content)   # Page function ko content frame do

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            logout_user()
            self.root.destroy()
            start_app()                         # Login screen pe wapas jao


# ============================================================
# APP START FUNCTION
# ============================================================

def start_app():
    """Login window dikhao, success pe main app kholo"""
    LoginWindow(on_success=lambda: MainApp())


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    connect_db()    # Pehle MongoDB se connect karo
    start_app()     # Phir app shuru karo