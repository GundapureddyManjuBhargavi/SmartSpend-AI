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
# DATABASE
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
    title TEXT,
    amount REAL,
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

# =========================================================
# PASSWORD HASH
# =========================================================

def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

# =========================================================
# AUTH SYSTEM
# =========================================================

if not st.session_state.logged_in:

    st.title("💰 SmartSpend AI Pro")

    choice = st.sidebar.radio("Choose Option", ["Login", "Signup"])

    if choice == "Signup":

        u = st.text_input("Username")
        p = st.text_input("Password", type="password")

        if st.button("Create Account"):
            try:
                cursor.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)",
                    (u, hash_password(p))
                )
                conn.commit()
                st.success("Account Created ✅")
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
                st.rerun()
            else:
                st.error("Invalid credentials")

# =========================================================
# MAIN APP
# =========================================================

else:

    st.sidebar.title("💡 SmartSpend AI Pro")

    page = st.sidebar.radio(
        "Navigation",
        ["🏠 Dashboard", "➕ Add Expense", "📋 View Expenses", "📊 Analytics", "🎯 Savings Goals", "🚪 Logout"]
    )

    # =========================================================
    # SIMPLE CLEAN THEME (NO CSS BUGS)
    # =========================================================

    st.markdown("""
    <style>
        .stApp {
            background-color: #0B1220;
            color: white;
        }

        h1, h2, h3, h4 {
            color: #00FFD1 !important;
        }

        .stButton > button {
            background-color: #00FFD1 !important;
            color: black !important;
            font-weight: bold;
            border-radius: 10px;
        }
    </style>
    """, unsafe_allow_html=True)

    # =========================================================
    # LOAD DATA
    # =========================================================

    df = pd.read_sql_query("SELECT * FROM expenses", conn)

    # =========================================================
    # DASHBOARD
    # =========================================================

    if page == "🏠 Dashboard":

        st.title("💰 Dashboard")

        total = df["amount"].sum() if not df.empty else 0
        avg = df["amount"].mean() if not df.empty else 0
        highest = df["amount"].max() if not df.empty else 0

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Spend", f"₹{total:,.2f}")
        col2.metric("Average Spend", f"₹{avg:,.2f}")
        col3.metric("Highest Expense", f"₹{highest:,.2f}")

        if not df.empty:
            cat = df.groupby("category")["amount"].sum().reset_index()
            fig = px.pie(cat, names="category", values="amount")
            st.plotly_chart(fig, use_container_width=True)

    # =========================================================
    # ADD EXPENSE (FIXED UI - NO SELECTBOX ISSUES)
    # =========================================================

    elif page == "➕ Add Expense":

        st.subheader("Add Expense")

        title = st.text_input("Title")
        amount = st.number_input("Amount", min_value=0.0)

        # SAFE UI (NO INVISIBLE TEXT EVER)
        st.markdown("### Category")
        category = st.radio(
            "",
            ["Food", "Travel", "Shopping", "Bills", "Health", "Other"],
            horizontal=True
        )

        st.markdown("### Payment Method")
        payment = st.radio(
            "",
            ["Cash", "UPI", "Card"],
            horizontal=True
        )

        date = st.date_input("Date")
        notes = st.text_area("Notes")

        if st.button("Save Expense"):

            cursor.execute("""
                INSERT INTO expenses
                (title, amount, category, payment_method, date, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (title, amount, category, payment, str(date), notes))

            conn.commit()
            st.success("Expense Saved Successfully ✅")

    # =========================================================
    # VIEW
    # =========================================================

    elif page == "📋 View Expenses":

        st.subheader("All Expenses")

        st.dataframe(df, use_container_width=True)

    # =========================================================
    # ANALYTICS
    # =========================================================

    elif page == "📊 Analytics":

        st.subheader("Analytics")

        if not df.empty:
            cat = df.groupby("category")["amount"].sum().reset_index()
            fig = px.bar(cat, x="category", y="amount", color="category")
            st.plotly_chart(fig, use_container_width=True)

    # =========================================================
    # SAVINGS
    # =========================================================

    elif page == "🎯 Savings Goals":

        st.subheader("Savings Goal")

        goal = st.number_input("Enter Goal", min_value=1000, value=10000)

        spent = df["amount"].sum() if not df.empty else 0

        st.progress(min(spent / goal, 1.0))

        st.metric("Remaining", f"₹{goal - spent:,.2f}")

    # =========================================================
    # LOGOUT
    # =========================================================

    elif page == "🚪 Logout":

        st.session_state.logged_in = False
        st.rerun()
