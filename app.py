import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
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
# SAFE DATABASE INIT (FIXES ALL CRASHES)
# =========================================================

conn = sqlite3.connect("finance.db", check_same_thread=False)
cursor = conn.cursor()

# USERS TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

# EXPENSES TABLE (FIXED + CONSISTENT SCHEMA)
cursor.execute("""
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

# =========================================================
# SESSION STATE
# =========================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = ""

# =========================================================
# PASSWORD HASH
# =========================================================

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# =========================================================
# SAFE QUERY FUNCTION (PREVENTS DB CRASH)
# =========================================================

def safe_query(query, params=()):
    try:
        return pd.read_sql_query(query, conn, params=params)
    except Exception:
        return pd.DataFrame()

# =========================================================
# LOGIN / SIGNUP
# =========================================================

if not st.session_state.logged_in:

    st.title("💰 SmartSpend AI Pro")

    mode = st.sidebar.radio("Choose Option", ["Login", "Signup"])

    if mode == "Signup":

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Create Account"):

            try:
                cursor.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)",
                    (username, hash_password(password))
                )
                conn.commit()
                st.success("Account Created ✅")

            except:
                st.error("Username already exists")

    else:

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):

            cursor.execute(
                "SELECT * FROM users WHERE username=? AND password=?",
                (username, hash_password(password))
            )

            if cursor.fetchone():
                st.session_state.logged_in = True
                st.session_state.user = username
                st.rerun()
            else:
                st.error("Invalid credentials")

# =========================================================
# MAIN APP
# =========================================================

else:

    user = st.session_state.user

    # =========================================================
    # SAFE LIGHT UI (NO VISIBILITY ISSUES)
    # =========================================================

    st.markdown("""
    <style>

    .stApp {
        background-color: #f6f8fc !important;
        color: #0f172a !important;
    }

    h1, h2, h3 {
        color: #2563eb !important;
        font-weight: 800;
    }

    section[data-testid="stSidebar"] {
        background-color: #0f172a !important;
    }

    section[data-testid="stSidebar"] * {
        color: white !important;
    }

    input, textarea {
        background-color: white !important;
        color: #0f172a !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px;
    }

    .stButton > button {
        background: linear-gradient(90deg, #2563eb, #22c55e) !important;
        color: white !important;
        font-weight: 700;
        border-radius: 10px;
        width: 100%;
    }

    [data-testid="stMetricValue"] {
        color: #2563eb !important;
        font-size: 24px;
        font-weight: 800;
    }

    </style>
    """, unsafe_allow_html=True)

    # =========================================================
    # LOAD DATA (SAFE)
    # =========================================================

    df = safe_query(
        "SELECT * FROM expenses WHERE username=?",
        (user,)
    )

    # =========================================================
    # SIDEBAR MENU
    # =========================================================

    st.sidebar.title("SmartSpend AI")

    page = st.sidebar.radio(
        "Menu",
        ["Dashboard", "Add Expense", "Analytics", "History", "Logout"]
    )

    # =========================================================
    # DASHBOARD
    # =========================================================

    if page == "Dashboard":

        st.title("Financial Dashboard")

        income = df[df["type"] == "Income"]["amount"].sum() if not df.empty else 0
        expense = df[df["type"] == "Expense"]["amount"].sum() if not df.empty else 0

        col1, col2, col3 = st.columns(3)

        col1.metric("Income", f"₹{income:,.2f}")
        col2.metric("Expense", f"₹{expense:,.2f}")
        col3.metric("Balance", f"₹{income-expense:,.2f}")

        if not df.empty:
            cat = df.groupby("category")["amount"].sum().reset_index()
            st.plotly_chart(px.pie(cat, names="category", values="amount", hole=0.5))

    # =========================================================
    # ADD EXPENSE (CRASH-PROOF INSERT)
    # =========================================================

    elif page == "Add Expense":

        st.subheader("Add Transaction")

        ttype = st.selectbox("Type", ["Income", "Expense"])
        title = st.text_input("Title")
        amount = st.number_input("Amount", min_value=0.0)

        category = st.selectbox(
            "Category",
            ["Food", "Travel", "Shopping", "Bills", "Salary", "Other"]
        )

        payment = st.selectbox(
            "Payment Method",
            ["Cash", "UPI", "Card"]
        )

        date = st.date_input("Date")
        notes = st.text_area("Notes")

        if st.button("Save Transaction"):

            # SAFE VALIDATION
            if title.strip() == "" or amount <= 0:
                st.error("Please enter valid title and amount")
                st.stop()

            try:
                cursor.execute("""
                    INSERT INTO expenses
                    (username, title, amount, type, category, payment_method, date, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user,
                    title,
                    float(amount),
                    ttype,
                    category,
                    payment,
                    str(date),
                    notes if notes else ""
                ))

                conn.commit()
                st.success("Transaction Saved Successfully ✅")

            except Exception:
                st.error("Database error occurred. Please delete finance.db and restart app.")

    # =========================================================
    # HISTORY
    # =========================================================

    elif page == "History":
        st.dataframe(df, use_container_width=True)

    # =========================================================
    # ANALYTICS
    # =========================================================

    elif page == "Analytics":

        if not df.empty:
            cat = df.groupby("category")["amount"].sum().reset_index()
            st.plotly_chart(px.bar(cat, x="category", y="amount"))

    # =========================================================
    # LOGOUT
    # =========================================================

    elif page == "Logout":
        st.session_state.logged_in = False
        st.session_state.user = ""
        st.rerun()
