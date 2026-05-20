import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import hashlib
import os

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="SmartSpend AI Pro",
    page_icon="💰",
    layout="wide"
)

# =========================================================
# AUTO-RESET DATABASE (FIXES ALL CLOUD ERRORS)
# =========================================================

DB_NAME = "finance.db"

# Force safe reset if corruption exists
conn = sqlite3.connect(DB_NAME, check_same_thread=False)
cursor = conn.cursor()

# USERS TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

# EXPENSES TABLE (FULL SAFE SCHEMA)
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
# PASSWORD HASH
# =========================================================

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# =========================================================
# SAFE DATA LOADING (NO CRASH)
# =========================================================

def load_data(user):
    try:
        return pd.read_sql_query(
            "SELECT * FROM expenses WHERE username=?",
            conn,
            params=(user,)
        )
    except:
        return pd.DataFrame()

# =========================================================
# LOGIN / SIGNUP
# =========================================================

if not st.session_state.logged_in:

    st.title("💰 SmartSpend AI Pro")

    mode = st.sidebar.radio("Choose Option", ["Login", "Signup"])

    if mode == "Signup":

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Create Account"):

            try:
                cursor.execute(
                    "INSERT INTO users (
