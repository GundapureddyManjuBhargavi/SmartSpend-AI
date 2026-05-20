import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import hashlib
import time

# =========================================================
# CONFIG
# =========================================================

st.set_page_config(
    page_title="SmartSpend Pro",
    page_icon="💰",
    layout="wide"
)

# =========================================================
# DB
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
# SESSION
# =========================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = ""

# =========================================================
# HASH
# =========================================================

def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

# =========================================================
# LOGIN / SIGNUP PAGE
# =========================================================

if not st.session_state.logged_in:

    st.title("💰 SmartSpend AI Pro")

    menu = st.sidebar.radio("Auth", ["Login", "Signup"])

    # ---------------- SIGNUP ----------------
    if menu == "Signup":

        st.subheader("Create Account")

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

        st.subheader("Login")

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
    # LOAD DATA
    # =========================================================

    df = pd.read_sql_query("SELECT * FROM expenses", conn)

    # =========================================================
    # RAZORPAY STYLE UI
    # =========================================================

    st.markdown("""
    <style>

    .stApp {
        background: radial-gradient(circle at top, #0f172a, #020617);
        color: white;
    }

    h1, h2, h3 {
        color: #00FFD1 !important;
        font-weight: 800;
    }

    /* METRIC CARDS */
    div[data-testid="stMetric"] {
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.08);
        padding: 18px;
        border-radius: 16px;
        backdrop-filter: blur(10px);
        transition: 0.3s;
    }

    div[data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(0,255,209,0.15);
    }

    [data-testid="stMetricValue"] {
        color: #00FFD1 !important;
        font-size: 26px;
        font-weight: 800;
    }

    /* BUTTON */
    .stButton > button {
        background: linear-gradient(90deg, #00FFD1, #00C2FF);
        color: black;
        font-weight: 700;
        border-radius: 12px;
        width: 100%;
    }

    /* SIDEBAR */
    section[data-testid="stSidebar"] {
        background: rgba(2,6,23,0.9);
    }

    </style>
    """, unsafe_allow_html=True)

    # =========================================================
    # SIDEBAR NAVIGATION
    # =========================================================

    st.sidebar.title("💡 SmartSpend Pro")

    page = st.sidebar.radio(
        "Navigation",
        ["🏠 Dashboard", "➕ Add Expense", "📊 Analytics", "📋 View Expenses", "🎯 Savings Goals", "🚪 Logout"]
    )

    st.sidebar.write(f"👤 Logged in as: **{st.session_state.user}**")

    # =========================================================
    # DASHBOARD (RAZORPAY STYLE)
    # =========================================================

    if page == "🏠 Dashboard":

        st.markdown("## 💰 Financial Dashboard")

        total = df["amount"].sum() if not df.empty else 0
        avg = df["amount"].mean() if not df.empty else 0
        highest = df["amount"].max() if not df.empty else 0

        col1, col2, col3 = st.columns(3)

        col1.metric("💸 Total Spend", f"₹{total:,.2f}")
        col2.metric("📊 Average Spend", f"₹{avg:,.2f}")
        col3.metric("🔥 Highest Expense", f"₹{highest:,.2f}")

        st.markdown("---")

        if not df.empty:

            cat = df.groupby("category")["amount"].sum().reset_index()

            c1, c2 = st.columns(2)

            with c1:
                st.markdown("### Category Split")
                fig = px.pie(cat, names="category", values="amount", hole=0.6)
                st.plotly_chart(fig, use_container_width=True)

            with c2:
                st.markdown("### Spending")
                fig2 = px.bar(cat, x="category", y="amount", color="category")
                st.plotly_chart(fig2, use_container_width=True)

    # =========================================================
    # ADD EXPENSE
    # =========================================================

    elif page == "➕ Add Expense":

        st.subheader("Add Expense")

        title = st.text_input("Title")
        amount = st.number_input("Amount", min_value=0.0)

        category = st.selectbox(
            "Category",
            ["Food", "Travel", "Shopping", "Bills", "Health", "Other"]
        )

        payment = st.selectbox(
            "Payment Method",
            ["Cash", "UPI", "Card"]
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
            st.success("Saved Successfully ✅")

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
