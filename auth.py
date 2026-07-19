# ============================================================
# auth.py
# Users, passwords aur logged-in user ka data
# store = None  → superadmin/analyst (sab stores ka data)
# store = "Delhi" → sirf Delhi store ka data dikhega
# ============================================================

USERS = {
    "admin":      {"password": "admin123",   "role": "Admin",       "name": "Admin User",   "store": "Delhi"},
    "admin2":     {"password": "admin456",   "role": "Admin",       "name": "Admin Mumbai", "store": "Mumbai"},
    "admin3":     {"password": "admin789",   "role": "Admin",       "name": "Admin Pune",   "store": "Pune"},
    "superadmin": {"password": "super123",   "role": "Super Admin", "name": "Super Admin",  "store": None},
    "analyst":    {"password": "analyst123", "role": "Analyst",     "name": "Sales Analyst","store": None},
}

# --- Currently logged-in user ka data ---
logged_user = {"name": "", "role": "", "username": "", "store": None}


def check_login(username: str, password: str) -> bool:
    """Username aur password match karo. True = login successful"""
    if username in USERS and USERS[username]["password"] == password:
        logged_user["name"]     = USERS[username]["name"]
        logged_user["role"]     = USERS[username]["role"]
        logged_user["username"] = username
        logged_user["store"]    = USERS[username]["store"]
        return True
    return False


def logout_user():
    """logged_user ka data clear karo"""
    logged_user["name"]     = ""
    logged_user["role"]     = ""
    logged_user["username"] = ""
    logged_user["store"]    = None


def get_store_filter():
    """
    MongoDB query ke liye filter return karo.
    Admin      → sirf apna store  e.g. {"region": "Delhi"}
    Superadmin → sab stores       {}
    """
    store = logged_user.get("store")
    if store:
        return {"region": store}
    return {}