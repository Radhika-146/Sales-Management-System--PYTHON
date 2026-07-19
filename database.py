# ============================================================
# database.py
# MongoDB se connection aur collection handle karna
# ============================================================

from pymongo import MongoClient
from tkinter import messagebox

collection = None   # Global variable - baaki files import karke use karengi


def connect_db():
    """MongoDB se connect karo aur collection return karo"""
    global collection
    try:
        client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=3000)
        client.server_info()
        db = client["sales_db"]
        collection = db["sales"]
        return collection
    except Exception as e:
        messagebox.showerror("Database Error",
            f"Could not connect to MongoDB!\nPlease start MongoDB service and try again.\n\nError: {e}")
        return None


def get_collection():
    """Collection ka reference do"""
    return collection