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
# PASSWORD HASH
# =========================================================

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# =========================================================
# AUTH
# =========================================================

if not st.session_state.logged_in:

    st.title("💰 SmartSpend AI Pro")

    auth = st.sidebar.radio("Choose Option", ["Login", "Signup"])

    if auth == "Signup":

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
        ["🏠 Dashboard", "➕ Add Expense", "📋 View Expenses", "📈 Analytics", "🎯 Savings Goals", "🤖 AI Insights", "🚪 Logout"]
    )

    dark = st.session_state.dark_mode

    # =========================================================
    # THEME
    # =========================================================

    if dark:
        bg = "#0B1220"
        text = "#FFFFFF"
        card = "#111827"
        input_bg = "#1E293B"
        input_text = "#FFFFFF"
    else:
        bg = "#F5F7FB"
        text = "#0F172A"
        card = "#FFFFFF"
        input_bg = "#FFFFFF"
        input_text = "#0F172A"

    # =========================================================
    # 🔥 FINTECH ANIMATED UI CSS (FINAL)
    # =========================================================

    st.markdown(f"""
    <style>

    .stApp {{
        background: linear-gradient(135deg, {bg}, #0f172a);
        color: {text};
    }}

    html, body, p, span, label, div {{
        color: {text} !important;
    }}

    h1, h2, h3 {{
        color: #00FFD1 !important;
        font-weight: 800;
    }}

    /* ================= GLASS CARDS ================= */

    div[data-testid="stMetric"] {{
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        padding: 18px;
        border-radius: 18px;
        backdrop-filter: blur(10px);
        transition: 0.3s;
    }}

    div[data-testid="stMetric"]:hover {{
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(0,255,209,0.2);
    }}

    [data-testid="stMetricValue"] {{
        color: #00FFD1 !important;
        font-weight: 800;
        font-size: 26px;
    }}

    /* ================= SIDEBAR ================= */

    section[data-testid="stSidebar"] {{
        background: rgba(17,24,39,0.9);
        backdrop-filter: blur(10px);
    }}

    section[data-testid="stSidebar"] * {{
        color: {text} !important;
    }}

    /* ================= INPUTS ================= */

    input, textarea {{
        background-color: rgba(255,255,255,0.05) !important;
        color: {input_text} !important;
        border-radius: 12px !important;
        border: 1px solid rgba(0,255,209,0.3) !important;
    }}

    input:focus {{
        border: 1px solid #00FFD1 !important;
        box-shadow: 0 0 10px rgba(0,255,209,0.3);
    }}

    /* ================= SELECTBOX FIX (FINAL) ================= */

    div[data-baseweb="select"] * {{
        color: {input_text} !important;
    }}

    div[role="listbox"] {{
        background: {card} !important;
    }}

    div[role="option"] {{
        background: {card} !important;
        color: {text} !important;
    }}

    div[role="option"]:hover {{
        background: #00FFD1 !important;
        color: black !important;
    }}

    /* ================= BUTTON ================= */

    .stButton > button {{
        background: linear-gradient(90deg, #00FFD1, #00C9A7);
        color: black;
        font-weight: 700;
        border-radius: 12px;
        width: 100%;
        transition: 0.3s;
    }}

    .stButton > button:hover {{
        transform: scale(1.03);
        box-shadow: 0 10px 20px rgba(0,255,209,0.3);
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
    # DASHBOARD (PHONEPE STYLE)
    # =========================================================

    if page == "🏠 Dashboard":

        st.markdown("## 💰 SmartSpend Dashboard")

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
                fig1 = px.pie(cat, names="category", values="amount", hole=0.55)
                st.plotly_chart(fig1, use_container_width=True)

            with c2:
                fig2 = px.bar(cat, x="category", y="amount")
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
            ["Food", "Travel", "Shopping", "Bills", "Entertainment", "Health", "Other"]
        )

        payment = st.selectbox(
            "Payment Method",
            ["Cash", "UPI", "Debit Card", "Credit Card"]
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
