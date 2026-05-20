import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import hashlib
from datetime import datetime

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
# SESSION STATE
# =========================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = ""

# =========================================================
# HASH PASSWORD
# =========================================================

def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

# =========================================================
# AUTH SYSTEM
# =========================================================

if not st.session_state.logged_in:

    st.title("💰 SmartSpend AI Pro")

    mode = st.sidebar.radio("Auth", ["Login", "Signup"])

    # ---------------- SIGNUP ----------------
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

    # ---------------- LOGIN ----------------
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

    # =========================================================
    # SAFE MODERN THEME (NO VISIBILITY ISSUE)
    # =========================================================

    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #0f172a, #1e293b);
        color: #E5E7EB;
    }

    h1, h2, h3 {
        color: #00FFD1 !important;
        font-weight: 800;
    }

    input, textarea {
        background-color: #111827 !important;
        color: #E5E7EB !important;
    }

    .stButton > button {
        background: linear-gradient(90deg, #00FFD1, #00C2FF);
        color: black;
        font-weight: 700;
        border-radius: 10px;
        width: 100%;
    }

    [data-testid="stMetricValue"] {
        color: #00FFD1 !important;
        font-size: 26px;
        font-weight: 800;
    }

    section[data-testid="stSidebar"] {
        background-color: #0f172a;
    }

    </style>
    """, unsafe_allow_html=True)

    # =========================================================
    # LOAD USER DATA
    # =========================================================

    user = st.session_state.user

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
        [
            "🏠 Dashboard",
            "➕ Add Transaction",
            "📊 Analytics",
            "📋 History",
            "💡 AI Insights",
            "📥 Download Report",
            "🚪 Logout"
        ]
    )

    # =========================================================
    # DASHBOARD (RAZORPAY STYLE)
    # =========================================================

    if page == "🏠 Dashboard":

        st.title("💰 Financial Dashboard")

        income = df[df["type"] == "Income"]["amount"].sum() if not df.empty else 0
        expense = df[df["type"] == "Expense"]["amount"].sum() if not df.empty else 0
        balance = income - expense

        col1, col2, col3 = st.columns(3)

        col1.metric("💰 Income", f"₹{income:,.2f}")
        col2.metric("💸 Expense", f"₹{expense:,.2f}")
        col3.metric("📊 Balance", f"₹{balance:,.2f}")

        st.markdown("---")

        if not df.empty:

            cat = df[df["type"] == "Expense"].groupby("category")["amount"].sum().reset_index()

            c1, c2 = st.columns(2)

            with c1:
                st.subheader("Expense Distribution")
                fig = px.pie(cat, names="category", values="amount", hole=0.6)
                st.plotly_chart(fig, use_container_width=True)

            with c2:
                st.subheader("Category Spending")
                fig2 = px.bar(cat, x="category", y="amount", color="category")
                st.plotly_chart(fig2, use_container_width=True)

    # =========================================================
    # ADD TRANSACTION
    # =========================================================

    elif page == "➕ Add Transaction":

        st.subheader("Add Income / Expense")

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
    # ANALYTICS
    # =========================================================

    elif page == "📊 Analytics":

        if not df.empty:

            st.subheader("Category Analytics")

            cat = df.groupby("category")["amount"].sum().reset_index()

            fig = px.bar(cat, x="category", y="amount", color="category")
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("Income vs Expense Trend")

            trend = df.groupby("type")["amount"].sum().reset_index()

            fig2 = px.pie(trend, names="type", values="amount")
            st.plotly_chart(fig2, use_container_width=True)

    # =========================================================
    # HISTORY
    # =========================================================

    elif page == "📋 History":

        st.subheader("Transaction History")

        st.dataframe(df, use_container_width=True)

    # =========================================================
    # AI INSIGHTS (RULE-BASED)
    # =========================================================

    elif page == "💡 AI Insights":

        st.subheader("Smart Insights")

        if not df.empty:

            top_cat = df[df["type"] == "Expense"].groupby("category")["amount"].sum().idxmax()

            st.success(f"🔥 Highest spending category: {top_cat}")

            st.info("💡 Try reducing non-essential spending by 10–20%")
            st.info("💡 Track weekly expenses for better control")
            st.info("💡 Avoid repeated small UPI transactions")

    # =========================================================
    # DOWNLOAD REPORT
    # =========================================================

    elif page == "📥 Download Report":

        st.subheader("Download CSV Report")

        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "Download Report",
            csv,
            "smartspend_report.csv",
            "text/csv"
        )

    # =========================================================
    # LOGOUT
    # =========================================================

    elif page == "🚪 Logout":

        st.session_state.logged_in = False
        st.session_state.user = ""
        st.rerun()
