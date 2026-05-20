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
    st.session_state.logged_in = True  # skip auth for simplicity demo

# =========================================================
# LOAD DATA
# =========================================================

df = pd.read_sql_query("SELECT * FROM expenses", conn)

# =========================================================
# RAZORPAY STYLE CSS (CLEAN + SAFE)
# =========================================================

st.markdown("""
<style>

/* BACKGROUND */
.stApp {
    background: radial-gradient(circle at top, #0f172a, #020617);
    color: white;
}

/* HEADER */
h1, h2, h3 {
    font-weight: 800;
    color: #00FFD1 !important;
    letter-spacing: 0.5px;
}

/* GLASS CARDS */
div[data-testid="stMetric"] {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.08);
    padding: 20px;
    border-radius: 18px;
    backdrop-filter: blur(10px);
    transition: all 0.3s ease;
}

div[data-testid="stMetric"]:hover {
    transform: translateY(-6px);
    box-shadow: 0 10px 30px rgba(0,255,209,0.15);
}

/* METRIC VALUE */
[data-testid="stMetricValue"] {
    font-size: 28px;
    font-weight: 800;
    color: #00FFD1 !important;
}

/* BUTTON */
.stButton > button {
    background: linear-gradient(90deg, #00FFD1, #00C2FF);
    color: black;
    font-weight: 700;
    border-radius: 12px;
    transition: 0.3s;
}

.stButton > button:hover {
    transform: scale(1.03);
    box-shadow: 0 10px 20px rgba(0,255,209,0.25);
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background: rgba(2,6,23,0.9);
    border-right: 1px solid rgba(255,255,255,0.1);
}

/* INPUTS */
input, textarea {
    background-color: #111827 !important;
    color: white !important;
    border-radius: 10px !important;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# HEADER (RAZORPAY STYLE)
# =========================================================

st.markdown("## 💰 SmartSpend Pro Dashboard")
st.markdown("### 🚀 Razorpay-style Financial Overview")

# =========================================================
# KPI CALCULATION
# =========================================================

total = df["amount"].sum() if not df.empty else 0
avg = df["amount"].mean() if not df.empty else 0
highest = df["amount"].max() if not df.empty else 0

# =========================================================
# ANIMATED KPI ROW
# =========================================================

col1, col2, col3 = st.columns(3)

with col1:
    placeholder = st.empty()
    for i in range(1, 101, 10):
        placeholder.metric("💸 Total Spend", f"₹{total*i/100:,.2f}")
        time.sleep(0.02)
    placeholder.metric("💸 Total Spend", f"₹{total:,.2f}")

with col2:
    st.metric("📊 Average Spend", f"₹{avg:,.2f}")

with col3:
    st.metric("🔥 Highest Expense", f"₹{highest:,.2f}")

st.markdown("---")

# =========================================================
# CHART SECTION (RAZORPAY STYLE GRID)
# =========================================================

if not df.empty:

    cat = df.groupby("category")["amount"].sum().reset_index()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📊 Category Breakdown")
        fig1 = px.pie(cat, names="category", values="amount", hole=0.6)
        fig1.update_traces(textinfo="percent+label")
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.markdown("### 📈 Spending Trend")
        fig2 = px.bar(cat, x="category", y="amount", color="category")
        st.plotly_chart(fig2, use_container_width=True)

else:
    st.info("No data yet — add expenses to see dashboard 🚀")

# =========================================================
# QUICK INSIGHTS CARD
# =========================================================

st.markdown("## ⚡ Smart Insights")

if not df.empty:
    top = df.groupby("category")["amount"].sum().idxmax()
    st.success(f"🔥 Highest spending category: **{top}**")

    st.info("💡 Tip: Try reducing top category spending by 10–20%")
