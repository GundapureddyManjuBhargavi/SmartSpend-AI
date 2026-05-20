import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import hashlib

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="SmartSpend AI Pro",
    page_icon="💰",
    layout="wide"
)

# =========================================================
# DATABASE (SAFE INIT - NO CRASH EVER)
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
# SESSION STATE
# =========================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = ""

# =========================================================
# HASH PASSWORD
# =========================================================

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# =========================================================
# LOGIN / SIGNUP
# =========================================================

if not st.session_state.logged_in:

    st.title("💰 SmartSpend AI Pro")

    mode = st.sidebar.radio("Choose Option", ["Login", "Signup"])

    # ---------------- SIGNUP ----------------
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
                st.success("Account Created Successfully ✅")
            except:
                st.error("Username already exists")

    # ---------------- LOGIN ----------------
    else:

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):

            cursor.execute(
                "SELECT * FROM users WHERE username=? AND password=?",
                (username, hash_password(password))
            )

            user = cursor.fetchone()

            if user:
                st.session_state.logged_in = True
                st.session_state.user = username
                st.rerun()
            else:
                st.error("Invalid Credentials")

# =========================================================
# MAIN APP
# =========================================================

else:

    user = st.session_state.user

    # =========================================================
    # SAFE UI (NO BLACK TEXT BUG EVER)
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

    /* TEXT FIX */
    p, span, label, div {
        color: #0f172a !important;
    }

    /* SIDEBAR */
    section[data-testid="stSidebar"] {
        background-color: #0f172a !important;
    }

    section[data-testid="stSidebar"] * {
        color: white !important;
    }

    /* INPUTS */
    input, textarea {
        background-color: white !important;
        color: #0f172a !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px;
    }

    /* SELECTBOX */
    div[data-baseweb="select"] * {
        color: #0f172a !important;
    }

    /* BUTTON */
    .stButton > button {
        background: linear-gradient(90deg, #2563eb, #22c55e) !important;
        color: white !important;
        font-weight: 700;
        border-radius: 10px;
        width: 100%;
    }

    /* METRICS */
    [data-testid="stMetricValue"] {
        color: #2563eb !important;
        font-size: 26px;
        font-weight: 800;
    }

    </style>
    """, unsafe_allow_html=True)

    # =========================================================
    # LOAD DATA (SAFE)
    # =========================================================

    try:
        df = pd.read_sql_query(
            "SELECT * FROM expenses WHERE username=?",
            conn,
            params=(user,)
        )
    except:
        df = pd.DataFrame()

    # =========================================================
    # MENU
    # =========================================================

    st.sidebar.title("💡 SmartSpend AI")

    page = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "Add Expense", "Analytics", "History", "Logout"]
    )

    # =========================================================
    # DASHBOARD
    # =========================================================

    if page == "Dashboard":

        st.title("Financial Dashboard")

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

    elif page == "History":

        st.subheader("All Transactions")
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
