import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import hashlib

# ================= PAGE CONFIG ================= #

st.set_page_config(
    page_title="SmartSpend AI Pro",
    page_icon="💰",
    layout="wide"
)

# ================= DATABASE ================= #

conn = sqlite3.connect(
    "finance.db",
    check_same_thread=False
)

cursor = conn.cursor()

# ================= CREATE TABLES ================= #

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
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

# ================= SESSION ================= #

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ================= FUNCTIONS ================= #

def hash_password(password):
    return hashlib.sha256(
        password.encode()
    ).hexdigest()

# ================= LOGIN / SIGNUP ================= #

if not st.session_state.logged_in:

    st.title("🔐 SmartSpend AI Pro")

    auth_menu = st.sidebar.radio(
        "Choose Option",
        [
            "Login",
            "Signup"
        ]
    )

    # ================= SIGNUP ================= #

    if auth_menu == "Signup":

        st.subheader("📝 Create Account")

        new_user = st.text_input(
            "Username"
        )

        new_pass = st.text_input(
            "Password",
            type="password"
        )

        if st.button("Create Account"):

            if new_user == "" or new_pass == "":

                st.error(
                    "Please fill all fields."
                )

            else:

                cursor.execute(
                    """
                    INSERT INTO users
                    (username, password)
                    VALUES (?, ?)
                    """,
                    (
                        new_user,
                        hash_password(new_pass)
                    )
                )

                conn.commit()

                st.success(
                    "Account Created Successfully ✅"
                )

    # ================= LOGIN ================= #

    elif auth_menu == "Login":

        st.subheader("🔑 Login")

        username = st.text_input(
            "Username"
        )

        password = st.text_input(
            "Password",
            type="password"
        )

        if st.button("Login"):

            cursor.execute(
                """
                SELECT * FROM users
                WHERE username=? AND password=?
                """,
                (
                    username,
                    hash_password(password)
                )
            )

            user = cursor.fetchone()

            if user:

                st.session_state.logged_in = True
                st.success("Login Successful ✅")
                st.rerun()

            else:

                st.error(
                    "Invalid Username or Password"
                )

# ================= MAIN APP ================= #

else:

    # ================= SIDEBAR ================= #

    st.sidebar.title("💡 SmartSpend AI Pro")

    dark_mode = st.sidebar.toggle(
        "🌙 Dark Mode",
        value=True
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

    # ================= THEME ================= #

    if dark_mode:

        bg_color = "#0E1117"
        text_color = "white"
        card_bg = "#161B22"
        input_bg = "#1E1E1E"

    else:

        bg_color = "#FFFFFF"
        text_color = "#000000"
        card_bg = "#F0F2F6"
        input_bg = "#FFFFFF"

    # ================= CSS ================= #

    st.markdown(f"""
    <style>

    .stApp {{
        background-color: {bg_color};
        color: {text_color};
    }}

    html, body, [class*="css"] {{
        color: {text_color} !important;
    }}

    h1, h2, h3 {{
        color: #00FFD1 !important;
    }}

    section[data-testid="stSidebar"] {{
        background-color: {card_bg};
    }}

    section[data-testid="stSidebar"] * {{
        color: {text_color} !important;
    }}

    .stTextInput input,
    .stNumberInput input,
    .stDateInput input,
    textarea {{

        background-color: {input_bg} !important;
        color: white !important;

        -webkit-text-fill-color: white !important;
        caret-color: white !important;

        border-radius: 10px !important;
        border: 2px solid #00FFD1 !important;
    }}

    div[data-baseweb="select"] > div {{

        background-color: {input_bg} !important;
        color: white !important;

        border-radius: 10px !important;
        border: 2px solid #00FFD1 !important;
    }}

    div[data-baseweb="select"] * {{
        color: white !important;
    }}

    .stButton > button {{

        background-color: #00FFD1 !important;
        color: black !important;

        border-radius: 10px !important;
        border: none !important;

        font-weight: bold !important;
        height: 3em;
        width: 100%;
    }}

    .stButton > button:hover {{

        background-color: #00c9a7 !important;
        color: white !important;
    }}

    [data-testid="stMetricValue"] {{
        color: #00FFD1 !important;
        font-size: 30px;
        font-weight: bold;
    }}

    .stAlert {{
        border-radius: 10px !important;
    }}

    </style>
    """, unsafe_allow_html=True)

    # ================= TITLE ================= #

    st.title("💰 SmartSpend AI Pro")

    # ================= LOAD DATA ================= #

    df = pd.read_sql_query(
        "SELECT * FROM expenses",
        conn
    )

    # ================= FIX OLD DATABASE ================= #

    try:
        df["date"] = pd.to_datetime(
            df["date"],
            errors="coerce"
        )

    except:

        cursor.execute(
            """
            ALTER TABLE expenses
            ADD COLUMN date TEXT
            """
        )

        conn.commit()

        df = pd.read_sql_query(
            "SELECT * FROM expenses",
            conn
        )

        df["date"] = pd.to_datetime(
            datetime.now()
        )

    # ================= DASHBOARD ================= #

    if menu == "🏠 Dashboard":

        st.subheader("📊 Financial Dashboard")

        total_expense = (
            df["amount"].sum()
            if not df.empty else 0
        )

        total_records = len(df)

        avg_expense = (
            df["amount"].mean()
            if not df.empty else 0
        )

        highest_expense = (
            df["amount"].max()
            if not df.empty else 0
        )

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "💸 Total Expenses",
            f"₹{total_expense:.2f}"
        )

        col2.metric(
            "📋 Records",
            total_records
        )

        col3.metric(
            "📈 Average",
            f"₹{avg_expense:.2f}"
        )

        col4.metric(
            "🔥 Highest",
            f"₹{highest_expense:.2f}"
        )

        if not df.empty:

            category_data = (
                df.groupby("category")["amount"]
                .sum()
                .reset_index()
            )

            col1, col2 = st.columns(2)

            with col1:

                fig = px.pie(
                    category_data,
                    names="category",
                    values="amount",
                    hole=0.5
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

            with col2:

                fig2 = px.bar(
                    category_data,
                    x="category",
                    y="amount"
                )

                st.plotly_chart(
                    fig2,
                    use_container_width=True
                )

    # ================= ADD EXPENSE ================= #

    elif menu == "➕ Add Expense":

        st.subheader("➕ Add Expense")

        title = st.text_input(
            "Expense Title"
        )

        amount = st.number_input(
            "Amount",
            min_value=0.0
        )

        category = st.selectbox(
            "Category",
            [
                "Food",
                "Travel",
                "Shopping",
                "Bills",
                "Entertainment",
                "Health",
                "Education",
                "Other"
            ]
        )

        payment_method = st.selectbox(
            "Payment Method",
            [
                "Cash",
                "UPI",
                "Debit Card",
                "Credit Card"
            ]
        )

        expense_date = st.date_input(
            "Expense Date"
        )

        notes = st.text_area(
            "Notes"
        )

        if st.button("💾 Save Expense"):

            cursor.execute(
                """
                INSERT INTO expenses
                (
                    title,
                    amount,
                    category,
                    payment_method,
                    date,
                    notes
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    title,
                    amount,
                    category,
                    payment_method,
                    str(expense_date),
                    notes
                )
            )

            conn.commit()

            st.success(
                "Expense Added Successfully ✅"
            )

            st.balloons()

    # ================= VIEW EXPENSES ================= #

    elif menu == "📋 View Expenses":

        st.subheader("📋 Expense Records")

        if not df.empty:

            search = st.text_input(
                "🔍 Search Expense"
            )

            filtered_df = df[
                df["title"]
                .str.contains(
                    search,
                    case=False,
                    na=False
                )
            ]

            st.dataframe(
                filtered_df,
                use_container_width=True
            )

            csv = filtered_df.to_csv(
                index=False
            )

            st.download_button(
                "📥 Download CSV",
                csv,
                "expenses.csv",
                "text/csv"
            )

            st.subheader("🗑️ Delete Expense")

            delete_id = st.number_input(
                "Expense ID",
                min_value=1
            )

            if st.button("Delete Expense"):

                cursor.execute(
                    """
                    DELETE FROM expenses
                    WHERE id=?
                    """,
                    (delete_id,)
                )

                conn.commit()

                st.success(
                    "Expense Deleted Successfully"
                )

    # ================= ANALYTICS ================= #

    elif menu == "📈 Analytics":

        st.subheader("📈 Expense Analytics")

        if not df.empty:

            monthly_data = (
                df.groupby(
                    df["date"].dt.strftime("%Y-%m")
                )["amount"]
                .sum()
                .reset_index()
            )

            fig = go.Figure()

            fig.add_trace(
                go.Scatter(
                    x=monthly_data["date"],
                    y=monthly_data["amount"],
                    mode="lines+markers"
                )
            )

            fig.update_layout(
                title="Monthly Expense Trend"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            category_data = (
                df.groupby("category")["amount"]
                .sum()
                .reset_index()
            )

            fig2 = px.treemap(
                category_data,
                path=["category"],
                values="amount"
            )

            st.plotly_chart(
                fig2,
                use_container_width=True
            )

    # ================= SAVINGS GOALS ================= #

    elif menu == "🎯 Savings Goals":

        st.subheader("🎯 Savings Goal Tracker")

        goal = st.number_input(
            "Enter Savings Goal",
            min_value=1000,
            value=10000
        )

        spent = (
            df["amount"].sum()
            if not df.empty else 0
        )

        remaining = goal - spent

        progress = min(
            spent / goal,
            1.0
        )

        st.progress(progress)

        st.metric(
            "Remaining Savings",
            f"₹{remaining:.2f}"
        )

    # ================= AI INSIGHTS ================= #

    elif menu == "🤖 AI Insights":

        st.subheader("🤖 AI Financial Insights")

        if not df.empty:

            highest_category = (
                df.groupby("category")["amount"]
                .sum()
                .idxmax()
            )

            highest_amount = (
                df.groupby("category")["amount"]
                .sum()
                .max()
            )

            st.success(
                f"Highest spending category: "
                f"{highest_category} "
                f"(₹{highest_amount:.2f})"
            )

            st.info(
                "💡 Save at least 20% every month."
            )

            st.info(
                "💡 Reduce unnecessary shopping."
            )

            st.info(
                "💡 Track subscriptions carefully."
            )

        else:

            st.warning(
                "No expense data available."
            )

    # ================= LOGOUT ================= #

    elif menu == "🚪 Logout":

        st.session_state.logged_in = False
        st.rerun()

    # ================= FOOTER ================= #

    st.markdown("""
    <hr>
    <center>
    Made with ❤️ by Gundapureddy Manju Bhargavi
    </center>
    """, unsafe_allow_html=True)