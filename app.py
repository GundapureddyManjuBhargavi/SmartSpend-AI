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
# ALWAYS CREATE FRESH DB CONNECTION (FIXES LOCK ISSUE)
# =========================================================

def get_conn():
    conn = sqlite3.connect("finance.db", check_same_thread=False)
    cur = conn.cursor()

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

# =========================================================
# SESSION
# =========================================================

if "user" not in st.session_state:
    st.session_state.user = ""

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# =========================================================
# PASSWORD HASH
# =========================================================

def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

# =========================================================
# SAFE LOAD DATA (NEW CONNECTION EVERY TIME)
# =========================================================

def load_data(user):
    conn = sqlite3.connect("finance.db", check_same_thread=False)
    try:
        return pd.read_sql_query(
            "SELECT * FROM expenses WHERE username=?",
            conn,
            params=(user,)
        )
    except:
        return pd.DataFrame()

# =========================================================
# LOGIN / SIGNUP
# =========================================================

if not st.session_state.logged_in:

    st.title("💰 SmartSpend AI Pro")

    mode = st.sidebar.radio("Choose", ["Login", "Signup"])

    conn, cursor = get_conn()

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
                st.error("User already exists")

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

    conn, cursor = get_conn()

    df = load_data(user)

    st.sidebar.title("SmartSpend AI")

    page = st.sidebar.radio(
        "Menu",
        ["Dashboard", "Add Transaction", "History", "Logout"]
    )

    # ---------------- DASHBOARD ----------------
    if page == "Dashboard":

        st.title("Dashboard")

        income = df[df["type"] == "Income"]["amount"].sum() if not df.empty else 0
        expense = df[df["type"] == "Expense"]["amount"].sum() if not df.empty else 0

        col1, col2, col3 = st.columns(3)
        col1.metric("Income", income)
        col2.metric("Expense", expense)
        col3.metric("Balance", income - expense)

    # ---------------- ADD TRANSACTION ----------------
    elif page == "Add Transaction":

        st.subheader("Add Transaction")

        ttype = st.selectbox("Type", ["Income", "Expense"])
        title = st.text_input("Title")
        amount = st.number_input("Amount", min_value=0.0)

        category = st.selectbox("Category", ["Food", "Travel", "Other"])
        payment = st.selectbox("Payment", ["Cash", "UPI", "Card"])
        date = st.date_input("Date")
        notes = st.text_area("Notes")

        if st.button("Save"):

            if title.strip() == "" or amount <= 0:
                st.error("Enter valid data")
                st.stop()

            try:
                conn, cursor = get_conn()

                cursor.execute("""
                    INSERT INTO expenses
                    (username, title, amount, type, category, payment_method, date, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user, title, amount, ttype,
                    category, payment, str(date), notes
                ))

                conn.commit()
                st.success("Saved successfully")

            except Exception as e:
                st.error("Database error — restart app")

    # ---------------- HISTORY ----------------
    elif page == "History":
        st.dataframe(df, use_container_width=True)

    # ---------------- LOGOUT ----------------
    elif page == "Logout":
        st.session_state.logged_in = False
        st.session_state.user = ""
        st.rerun()
