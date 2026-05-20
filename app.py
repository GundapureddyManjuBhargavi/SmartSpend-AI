import streamlit as st
import pandas as pd
import sqlite3
import hashlib

# =========================================================
# CONFIG
# =========================================================

st.set_page_config(
    page_title="SmartSpend AI Pro",
    page_icon="💰",
    layout="wide"
)

# =========================================================
# SAFE DB CONNECTION (NO CRASH MODE)
# =========================================================

def get_connection():
    conn = sqlite3.connect("finance.db", check_same_thread=False)
    cur = conn.cursor()

    # ALWAYS FORCE TABLES (NO DEPENDENCY ON OLD DB)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        title TEXT,
        amount REAL,
        type TEXT,
        category TEXT,
        payment_method TEXT,
        date TEXT,
        notes TEXT
    )
    """)

    conn.commit()
    return conn, cur

conn, cursor = get_connection()

# =========================================================
# SESSION
# =========================================================

if "user" not in st.session_state:
    st.session_state.user = ""

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# =========================================================
# HASH
# =========================================================

def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

# =========================================================
# LOAD DATA SAFE
# =========================================================

def load_data(user):
    try:
        return pd.read_sql_query(
            "SELECT * FROM expenses WHERE username=?",
            conn,
            params=(user,)
        )
    except:
        return pd.DataFrame()

# =========================================================
# LOGIN
# =========================================================

if not st.session_state.logged_in:

    st.title("💰 SmartSpend AI Pro")

    mode = st.sidebar.radio("Choose", ["Login", "Signup"])

    if mode == "Signup":

        u = st.text_input("Username")
        p = st.text_input("Password", type="password")

        if st.button("Create Account"):
            try:
                cursor.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)",
                    (u, hash_password(p))
                )
                conn.commit()
                st.success("Account created")
            except:
                st.error("User exists")

    else:

        u = st.text_input("Username")
        p = st.text_input("Password", type="password")

        if st.button("Login"):

            cursor.execute(
                "SELECT * FROM users WHERE username=? AND password=?",
                (u, hash_password(p))
            )

            if cursor.fetchone():
                st.session_state.user = u
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Invalid login")

# =========================================================
# MAIN APP
# =========================================================

else:

    user = st.session_state.user

    df = load_data(user)

    st.sidebar.title("SmartSpend AI")

    page = st.sidebar.radio(
        "Menu",
        ["Dashboard", "Add", "History", "Logout"]
    )

    # ---------------- DASHBOARD ----------------
    if page == "Dashboard":
        st.title("Dashboard")

        income = df[df["type"] == "Income"]["amount"].sum() if not df.empty else 0
        expense = df[df["type"] == "Expense"]["amount"].sum() if not df.empty else 0

        st.metric("Income", income)
        st.metric("Expense", expense)
        st.metric("Balance", income - expense)

    # ---------------- ADD ----------------
    elif page == "Add":

        st.subheader("Add Transaction")

        t = st.selectbox("Type", ["Income", "Expense"])
        title = st.text_input("Title")
        amount = st.number_input("Amount", min_value=0.0)
        cat = st.selectbox("Category", ["Food", "Travel", "Other"])
        pay = st.selectbox("Payment", ["Cash", "UPI", "Card"])
        date = st.date_input("Date")
        notes = st.text_area("Notes")

        if st.button("Save"):

            if title == "" or amount <= 0:
                st.error("Fill properly")
                st.stop()

            try:
                cursor.execute("""
                INSERT INTO expenses
                (username, title, amount, type, category, payment_method, date, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (user, title, amount, t, cat, pay, str(date), notes))

                conn.commit()
                st.success("Saved")

            except Exception:
                st.error("DB error - refresh app")

    # ---------------- HISTORY ----------------
    elif page == "History":
        st.dataframe(df)

    # ---------------- LOGOUT ----------------
    elif page == "Logout":
        st.session_state.logged_in = False
        st.session_state.user = ""
        st.rerun()
