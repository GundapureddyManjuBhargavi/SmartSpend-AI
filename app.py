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
# DB SETUP
# =========================================================

conn = sqlite3.connect("finance.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

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
# SESSION
# =========================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = ""

# =========================================================
# PASSWORD HASH
# =========================================================

def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

# =========================================================
# LOGIN / SIGNUP
# =========================================================

if not st.session_state.logged_in:

    st.title("💰 SmartSpend AI Pro")

    mode = st.sidebar.radio("Auth", ["Login", "Signup"])

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
                st.success("Account created ✅")
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
                st.session_state.logged_in = True
                st.session_state.user = u
                st.rerun()
            else:
                st.error("Invalid credentials")

# =========================================================
# MAIN APP
# =========================================================

else:

    user = st.session_state.user

    # =========================================================
    # SAFE FINTECH LIGHT THEME (NO VISIBILITY ISSUES)
    # =========================================================

    st.markdown("""
    <style>

    /* LIGHT BACKGROUND (BEST READABILITY) */
    .stApp {
        background: #f5f7fb !important;
        color: #0f172a !important;
    }

    /* HEADINGS */
    h1, h2, h3 {
        color: #0ea5e9 !important;
        font-weight: 800;
    }

    /* TEXT */
    p, span, label, div {
        color: #0f172a !important;
    }

    /* SIDEBAR */
    section[data-testid="stSidebar"] {
        background-color: #0f172a !important;
        color: white !important;
    }

    section[data-testid="stSidebar"] * {
        color: white !important;
    }

    /* INPUTS */
    input, textarea {
        background-color: white !important;
        color: #0f172a !important;
        border: 1px solid #cbd5e1 !important;
    }

    /* SELECTBOX (SAFE) */
    div[data-baseweb="select"] {
        background-color: white !important;
        color: #0f172a !important;
    }

    div[role="option"] {
        background-color: white !important;
        color: #0f172a !important;
    }

    div[role="option"]:hover {
        background-color: #0ea5e9 !important;
        color: white !important;
    }

    /* BUTTON */
    .stButton > button {
        background: linear-gradient(90deg, #0ea5e9, #22c55e) !important;
        color: white !important;
        font-weight: 700;
        border-radius: 10px;
        width: 100%;
    }

    /* METRICS */
    [data-testid="stMetricValue"] {
        color: #0ea5e9 !important;
        font-size: 26px;
        font-weight: 800;
    }

    </style>
    """, unsafe_allow_html=True)

    # =========================================================
    # LOAD DATA
    # =========================================================

    df = pd.read_sql_query(
        "SELECT * FROM expenses WHERE username=?",
        conn,
        params=(user,)
    )

    # =========================================================
    # SIDEBAR
    # =========================================================

    st.sidebar.title(f"💡 {user}")

    page = st.sidebar.radio(
        "Navigation",
        ["🏠 Dashboard", "➕ Add Expense", "📊 Analytics", "📋 History", "🎯 Savings", "🚪 Logout"]
    )

    # =========================================================
    # DASHBOARD
    # =========================================================

    if page == "🏠 Dashboard":

        st.title("💰 Financial Dashboard")

        income = df[df["type"] == "Income"]["amount"].sum() if not df.empty else 0
        expense = df[df["type"] == "Expense"]["amount"].sum() if not df.empty else 0
        balance = income - expense

        col1, col2, col3 = st.columns(3)

        col1.metric("Income", f"₹{income:,.2f}")
        col2.metric("Expense", f"₹{expense:,.2f}")
        col3.metric("Balance", f"₹{balance:,.2f}")

        if not df.empty:
            cat = df.groupby("category")["amount"].sum().reset_index()
            fig = px.pie(cat, names="category", values="amount", hole=0.5)
            st.plotly_chart(fig, use_container_width=True)

    # =========================================================
    # ADD EXPENSE
    # =========================================================

    elif page == "➕ Add Expense":

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

        if st.button("Save"):

            cursor.execute("""
                INSERT INTO expenses
                (username, title, amount, type, category, payment_method, date, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (user, title, amount, ttype, category, payment, str(date), notes))

            conn.commit()
            st.success("Saved Successfully ✅")

    # =========================================================
    # HISTORY
    # =========================================================

    elif page == "📋 History":

        st.dataframe(df, use_container_width=True)

    # =========================================================
    # ANALYTICS
    # =========================================================

    elif page == "📊 Analytics":

        if not df.empty:
            cat = df.groupby("category")["amount"].sum().reset_index()
            fig = px.bar(cat, x="category", y="amount", color="category")
            st.plotly_chart(fig, use_container_width=True)

    # =========================================================
    # SAVINGS
    # =========================================================

    elif page == "🎯 Savings":

        goal = st.number_input("Goal", min_value=1000, value=10000)

        spent = df["amount"].sum() if not df.empty else 0

        st.progress(min(spent / goal, 1.0))

        st.metric("Remaining", f"₹{goal - spent:,.2f}")

    # =========================================================
    # LOGOUT
    # =========================================================

    elif page == "🚪 Logout":
        st.session_state.logged_in = False
        st.session_state.user = ""
        st.rerun()
