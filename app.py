import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
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
# AUTH PAGE
# =========================================================

if not st.session_state.logged_in:

    st.title("🔐 SmartSpend AI Pro")

    auth_menu = st.sidebar.radio("Choose Option", ["Login", "Signup"])

    # ---------------- SIGNUP ----------------
    if auth_menu == "Signup":

        st.subheader("📝 Create Account")

        new_user = st.text_input("Username")
        new_pass = st.text_input("Password", type="password")

        if st.button("Create Account"):

            if new_user == "" or new_pass == "":
                st.error("Please fill all fields.")
            else:
                try:
                    cursor.execute("""
                        INSERT INTO users (username, password)
                        VALUES (?, ?)
                    """, (new_user, hash_password(new_pass)))

                    conn.commit()
                    st.success("Account Created Successfully ✅")

                except:
                    st.error("Username already exists.")

    # ---------------- LOGIN ----------------
    elif auth_menu == "Login":

        st.subheader("🔑 Login")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):

            cursor.execute("""
                SELECT * FROM users
                WHERE username=? AND password=?
            """, (username, hash_password(password)))

            user = cursor.fetchone()

            if user:
                st.session_state.logged_in = True
                st.success("Login Successful ✅")
                st.rerun()
            else:
                st.error("Invalid Username or Password")

# =========================================================
# MAIN APP
# =========================================================

else:

    # ---------------- SIDEBAR ----------------
    st.sidebar.title("💡 SmartSpend AI Pro")

    st.session_state.dark_mode = st.sidebar.toggle(
        "🌙 Dark Mode",
        value=st.session_state.dark_mode
    )

    menu = st.sidebar.radio(
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

    # =====================================================
    # THEME
    # =====================================================

    if dark_mode:
        bg_color = "#0E1117"
        text_color = "#FFFFFF"
        card_bg = "#161B22"
        input_bg = "#1E1E1E"
        input_text = "#FFFFFF"
        dropdown_bg = "#1E1E1E"
        dropdown_text = "#FFFFFF"
    else:
        bg_color = "#F7F9FC"
        text_color = "#000000"
        card_bg = "#FFFFFF"
        input_bg = "#FFFFFF"
        input_text = "#000000"
        dropdown_bg = "#FFFFFF"
        dropdown_text = "#000000"

    # =====================================================
    # CSS
    # =====================================================

    st.markdown(f"""
    <style>

    .stApp {{
        background-color: {bg_color};
        color: {text_color};
    }}

    html, body, p, span, label, div {{
        color: {text_color} !important;
    }}

    h1, h2, h3 {{
        color: #00FFD1 !important;
        font-weight: bold;
    }}

    section[data-testid="stSidebar"] {{
        background-color: {card_bg};
    }}

    section[data-testid="stSidebar"] * {{
        color: {text_color} !important;
    }}

    .stTextInput input,
    .stNumberInput input,
    textarea {{
        background-color: {input_bg} !important;
        color: {input_text} !important;
        -webkit-text-fill-color: {input_text} !important;
        caret-color: {input_text} !important;
        border-radius: 10px !important;
        border: 2px solid #00FFD1 !important;
    }}

    .stButton > button {{
        background-color: #00FFD1 !important;
        color: black !important;
        border-radius: 10px !important;
        font-weight: bold !important;
        width: 100%;
        height: 3em;
    }}

    .stButton > button:hover {{
        background-color: #00c9a7 !important;
        color: {input_text} !important;
    }}

    [data-testid="stMetricValue"] {{
        color: #00FFD1 !important;
        font-size: 28px;
        font-weight: bold;
    }}

    footer {{
        visibility: hidden;
    }}

    </style>
    """, unsafe_allow_html=True)

    # =====================================================
    # LOAD DATA
    # =====================================================

    df = pd.read_sql_query("SELECT * FROM expenses", conn)

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # =====================================================
    # DASHBOARD
    # =====================================================

    if menu == "🏠 Dashboard":

        st.subheader("📊 Financial Dashboard")

        total = df["amount"].sum() if not df.empty else 0
        avg = df["amount"].mean() if not df.empty else 0
        highest = df["amount"].max() if not df.empty else 0

        col1, col2, col3 = st.columns(3)

        col1.metric("💸 Total", f"₹{total:.2f}")
        col2.metric("📈 Average", f"₹{avg:.2f}")
        col3.metric("🔥 Highest", f"₹{highest:.2f}")

        if not df.empty:

            cat = df.groupby("category")["amount"].sum().reset_index()

            fig1 = px.pie(cat, names="category", values="amount", hole=0.5)
            st.plotly_chart(fig1, use_container_width=True)

    # =====================================================
    # ADD EXPENSE
    # =====================================================

    elif menu == "➕ Add Expense":

        st.subheader("➕ Add Expense")

        title = st.text_input("Title")
        amount = st.number_input("Amount", min_value=0.0)

        category = st.selectbox("Category",
            ["Food","Travel","Shopping","Bills","Other"])

        payment = st.selectbox("Payment", ["Cash","UPI","Card"])

        date = st.date_input("Date")
        notes = st.text_area("Notes")

        if st.button("Save Expense"):

            cursor.execute("""
                INSERT INTO expenses
                (title, amount, category, payment_method, date, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (title, amount, category, payment, str(date), notes))

            conn.commit()
            st.success("Saved ✅")
            st.balloons()

    # =====================================================
    # VIEW
    # =====================================================

    elif menu == "📋 View Expenses":

        st.subheader("📋 Records")

        search = st.text_input("Search")

        filtered = df[df["title"].str.contains(search, case=False, na=False)]

        st.dataframe(filtered, use_container_width=True)

        st.download_button(
            "Download CSV",
            filtered.to_csv(index=False),
            "expenses.csv"
        )

    # =====================================================
    # ANALYTICS
    # =====================================================

    elif menu == "📈 Analytics":

        st.subheader("📈 Analytics")

        if not df.empty:

            monthly = df.groupby(df["date"].dt.strftime("%Y-%m"))["amount"].sum().reset_index()

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=monthly["date"], y=monthly["amount"], mode="lines+markers"))

            st.plotly_chart(fig, use_container_width=True)

    # =====================================================
    # SAVINGS
    # =====================================================

    elif menu == "🎯 Savings Goals":

        st.subheader("🎯 Goals")

        goal = st.number_input("Goal", min_value=1000, value=10000)

        spent = df["amount"].sum() if not df.empty else 0

        st.progress(min(spent / goal, 1.0))

        st.metric("Remaining", f"₹{goal - spent:.2f}")

    # =====================================================
    # AI INSIGHTS
    # =====================================================

    elif menu == "🤖 AI Insights":

        st.subheader("🤖 Insights")

        if not df.empty:

            top = df.groupby("category")["amount"].sum().idxmax()

            st.success(f"Top spending: {top}")
            st.info("Save 20% monthly 💡")
            st.info("Avoid unnecessary shopping 🛍️")

    # =====================================================
    # LOGOUT
    # =====================================================

    elif menu == "🚪 Logout":
        st.session_state.logged_in = False
        st.rerun()
