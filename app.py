import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
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
# PASSWORD
# =========================================================

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# =========================================================
# LOGIN / SIGNUP
# =========================================================

if not st.session_state.logged_in:

    st.title("🔐 SmartSpend AI Pro")

    menu = st.sidebar.radio("Choose Option", ["Login", "Signup"])

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
                st.success("Account Created ✅")
            except:
                st.error("Username already exists")

    elif menu == "Login":

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
                st.success("Login Success")
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
        [
            "🏠 Dashboard",
            "➕ Add Expense",
            "📋 View Expenses",
            "📈 Analytics",
            "🎯 Savings Goals",
            "🤖 AI Insights",
            "🚪 Logout"
        ]
    )

    dark_mode = st.session_state.dark_mode

    # =========================================================
    # THEME COLORS
    # =========================================================

    if dark_mode:
        bg = "#0E1117"
        text = "#FFFFFF"
        card = "#161B22"
        input_bg = "#1E1E1E"
        input_text = "#FFFFFF"
    else:
        bg = "#F7F9FC"
        text = "#000000"
        card = "#FFFFFF"
        input_bg = "#FFFFFF"
        input_text = "#000000"

    # =========================================================
    # CSS (FIXED SELECTBOX + VISIBILITY)
    # =========================================================

    st.markdown(f"""
    <style>

    .stApp {{
        background-color: {bg};
        color: {text};
    }}

    html, body, p, span, label, div, h1, h2, h3 {{
        color: {text} !important;
    }}

    section[data-testid="stSidebar"] {{
        background-color: {card};
    }}

    section[data-testid="stSidebar"] * {{
        color: {text} !important;
    }}

    /* INPUT FIX */
    input, textarea {{
        background-color: {input_bg} !important;
        color: {input_text} !important;
        -webkit-text-fill-color: {input_text} !important;
        caret-color: {input_text} !important;
    }}

    /* STREAMLIT INPUT */
    .stTextInput input,
    .stNumberInput input {{
        color: {input_text} !important;
    }}

    /* =====================================================
       🔥 SELECTBOX FIX (THIS FIXES YOUR ISSUE)
    ===================================================== */

    div[data-baseweb="select"] {{
        background-color: {input_bg} !important;
        color: {input_text} !important;
    }}

    div[data-baseweb="select"] * {{
        color: {input_text} !important;
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

    .stButton > button:hover {{
        background-color: #00c9a7 !important;
        color: black !important;
    }}

    /* METRICS */
    [data-testid="stMetricValue"] {{
        color: #00FFD1 !important;
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

        st.subheader("Dashboard")

        total = df["amount"].sum() if not df.empty else 0

        st.metric("Total Expenses", f"₹{total:.2f}")

    # =========================================================
    # ADD EXPENSE (FIXED CATEGORY VISIBILITY HERE)
    # =========================================================

    elif page == "➕ Add Expense":

        st.subheader("Add Expense")

        title = st.text_input("Title")
        amount = st.number_input("Amount", min_value=0.0)

        category = st.selectbox(
            "Category",
            ["Food", "Travel", "Shopping", "Bills", "Entertainment", "Health", "Other"]
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

        st.subheader("Records")

        st.dataframe(df, use_container_width=True)

    # =========================================================
    # ANALYTICS
    # =========================================================

    elif page == "📈 Analytics":

        st.subheader("Analytics")

        if not df.empty:

            cat = df.groupby("category")["amount"].sum().reset_index()

            fig = px.pie(cat, names="category", values="amount")

            st.plotly_chart(fig, use_container_width=True)

    # =========================================================
    # SAVINGS
    # =========================================================

    elif page == "🎯 Savings Goals":

        st.subheader("Savings Goal")

        goal = st.number_input("Goal", min_value=1000, value=10000)

        spent = df["amount"].sum() if not df.empty else 0

        st.progress(min(spent / goal, 1.0))

        st.metric("Remaining", f"₹{goal - spent:.2f}")

    # =========================================================
    # AI INSIGHTS
    # =========================================================

    elif page == "🤖 AI Insights":

        st.subheader("Insights")

        if not df.empty:

            top = df.groupby("category")["amount"].sum().idxmax()

            st.success(f"Top Category: {top}")

    # =========================================================
    # LOGOUT
    # =========================================================

    elif page == "🚪 Logout":
        st.session_state.logged_in = False
        st.rerun()
