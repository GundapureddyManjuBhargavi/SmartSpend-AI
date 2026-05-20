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
    layout="wide",
    initial_sidebar_state="expanded"
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

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

# =========================================================
# PASSWORD HASH
# =========================================================

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# =========================================================
# LOGIN / SIGNUP
# =========================================================

if not st.session_state.logged_in:

    st.title("💰 SmartSpend AI Pro")

    auth = st.sidebar.radio("Choose Option", ["Login", "Signup"])

    if auth == "Signup":

        st.subheader("Create Account")

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

        st.subheader("Login")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            cursor.execute(
                "SELECT * FROM users WHERE username=? AND password=?",
                (username, hash_password(password))
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

    # SIDEBAR
    st.sidebar.title("💡 SmartSpend AI Pro")

    st.session_state.dark_mode = st.sidebar.toggle(
        "🌙 Dark Mode",
        value=st.session_state.dark_mode
    )

    page = st.sidebar.radio(
        "Navigation",
        ["🏠 Dashboard", "➕ Add Expense", "📋 View Expenses", "📊 Analytics", "🎯 Savings Goals", "🚪 Logout"]
    )

    dark = st.session_state.dark_mode

    # =========================================================
    # SAFE THEME (NO VISIBILITY BUG)
    # =========================================================

    if dark:
        bg = "#0B1220"
        text = "#FFFFFF"
        card = "#111827"
        input_bg = "#1E293B"
    else:
        bg = "#F5F7FB"
        text = "#0F172A"
        card = "#FFFFFF"
        input_bg = "#FFFFFF"

    # =========================================================
    # CLEAN CSS (FINAL SAFE VERSION)
    # =========================================================

    st.markdown(f"""
    <style>

    .stApp {{
        background-color: {bg} !important;
        color: {text} !important;
    }}

    html, body, p, span, label, div, h1, h2, h3 {{
        color: {text} !important;
    }}

    section[data-testid="stSidebar"] {{
        background-color: {card} !important;
    }}

    section[data-testid="stSidebar"] * {{
        color: {text} !important;
    }}

    /* INPUT FIX */
    input, textarea {{
        background-color: {input_bg} !important;
        color: {text} !important;
        -webkit-text-fill-color: {text} !important;
    }}

    /* SELECTBOX FIX (IMPORTANT) */
    div[data-baseweb="select"] * {{
        color: {text} !important;
    }}

    div[role="listbox"] {{
        background-color: {card} !important;
    }}

    div[role="option"] {{
        background-color: {card} !important;
        color: {text} !important;
    }}

    div[role="option"]:hover {{
        background-color: #00FFD1 !important;
        color: black !important;
    }}

    /* BUTTON */
    .stButton > button {{
        background-color: #00FFD1 !important;
        color: black !important;
        font-weight: bold;
        border-radius: 10px;
        width: 100%;
    }}

    /* METRICS */
    [data-testid="stMetricValue"] {{
        color: #00FFD1 !important;
        font-size: 26px;
        font-weight: 800;
    }}

    footer {{
        visibility: hidden;
    }}

    </style>
    """, unsafe_allow_html=True)

    # =========================================================
    # LOAD DATA
    # =========================================================

    df = pd.read_sql_query("SELECT * FROM expenses", conn)

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # =========================================================
    # DASHBOARD
    # =========================================================

    if page == "🏠 Dashboard":

        st.title("💰 SmartSpend Dashboard")

        total = df["amount"].sum() if not df.empty else 0
        avg = df["amount"].mean() if not df.empty else 0
        highest = df["amount"].max() if not df.empty else 0

        col1, col2, col3 = st.columns(3)

        col1.metric("💸 Total", f"₹{total:,.2f}")
        col2.metric("📊 Average", f"₹{avg:,.2f}")
        col3.metric("🔥 Highest", f"₹{highest:,.2f}")

        if not df.empty:
            cat = df.groupby("category")["amount"].sum().reset_index()
            fig = px.pie(cat, names="category", values="amount", hole=0.5)
            st.plotly_chart(fig, use_container_width=True)

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
            st.success("Expense Saved ✅")

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
        st.rerun()
