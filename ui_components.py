# ============================================================
# ui_components.py
# Reusable UI components - header, card, entry, button, KPI box
# ============================================================

import tkinter as tk
from datetime import datetime
from config import C, F
from auth import logged_user


def make_header(content_frame, title):
    """Har page ka top header - title + date + username + store dikhata hai"""
    h = tk.Frame(content_frame, bg=C["white"])
    h.pack(fill="x")
    tk.Label(h, text=title, font=F["head"],
             bg=C["white"], fg=C["text"]).pack(side="left", padx=20, pady=14)

    # Store info - admin ko store name dikhao, superadmin ko "All Stores"
    store = logged_user.get("store")
    store_txt = f"🏪 {store}" if store else "🏪 All Stores"

    info_txt = (f"📅 {datetime.now().strftime('%d %b %Y')}  |  "
                f"👤 {logged_user['name']}  |  {store_txt}")
    tk.Label(h, text=info_txt, font=F["small"], bg=C["white"],
             fg=C["subtext"]).pack(side="right", padx=20)

    tk.Frame(content_frame, bg=C["border"], height=1).pack(fill="x")
    container = tk.Frame(content_frame, bg=C["bg"])
    container.pack(fill="both", expand=True)
    return container


def white_card(parent, pady=8, padx=16):
    """Bordered white card frame"""
    card = tk.Frame(parent, bg=C["white"],
                    highlightbackground=C["border"], highlightthickness=1)
    card.pack(fill="x", padx=padx, pady=pady)
    return card


def label_entry(parent, label_text):
    """Label + Entry field pair"""
    tk.Label(parent, text=label_text, font=F["small"],
             bg=C["white"], fg=C["subtext"]).pack(anchor="w", padx=20, pady=(10, 2))
    entry = tk.Entry(parent, font=F["body"], relief="solid",
                     bd=1, bg=C["bg"], fg=C["text"])
    entry.pack(fill="x", padx=20, ipady=6, pady=(0, 2))
    return entry


def styled_btn(parent, text, command, color=None):
    """Styled button - color deo ya default blue"""
    color = color or C["blue"]
    b = tk.Button(parent, text=text, font=F["btn"],
                  bg=color, fg=C["white"], relief="flat",
                  cursor="hand2", padx=14, pady=8, command=command)
    b.pack(padx=20, pady=8, fill="x")
    return b


def kpi_box(parent, col, icon, title, value, color):
    """Bada KPI card - top color strip + number"""
    card = tk.Frame(parent, bg=C["white"],
                    highlightbackground=color, highlightthickness=2)
    card.grid(row=0, column=col, padx=8, pady=4, sticky="nsew")
    parent.columnconfigure(col, weight=1)
    tk.Frame(card, bg=color, height=4).pack(fill="x")
    tk.Label(card, text=f"{icon}  {title}", font=F["small"],
             bg=C["white"], fg=C["subtext"]).pack(anchor="w", padx=14, pady=(10, 0))
    tk.Label(card, text=value, font=F["big_num"],
             bg=C["white"], fg=color).pack(anchor="w", padx=14, pady=(4, 12))