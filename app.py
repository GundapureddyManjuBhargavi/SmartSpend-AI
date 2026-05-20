import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# ---------------- PAGE CONFIG ---------------- #

st.set_page_config(
    page_title="SmartSpend AI",
    page_icon="💰",
    layout="wide"
)

# ---------------- DATABASE ---------------- #

conn = sqlite3.connect(
    "finance.db",
    check_same_thread=False
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    amount REAL,
    category TEXT,
    date TEXT
)
""")

conn.commit()

# ---------------- SIDEBAR ---------------- #

st.sidebar.title("💡 SmartSpend AI")

dark_mode = st.sidebar.toggle(
    "🌙 Dark Mode",
    value=True
)

menu = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Add Expense",
        "View Expenses"
    ]
)

# ---------------- THEME COLORS ---------------- #

if dark_mode:

    bg_color = "#0E1117"
    text_color = "white"
    sidebar_color = "#161B22"

else:

    bg_color = "#FFFFFF"
    text_color = "#000000"
    sidebar_color = "#F0F2F6"

# ---------------- CUSTOM CSS ---------------- #

st.markdown(f"""
<style>

/* MAIN APP */

.stApp {{
    background-color: {bg_color};
    color: {text_color};
}}

/* GLOBAL TEXT */

html,
body,
[class*="css"] {{
    color: {text_color} !important;
}}

/* HEADINGS */

h1,
h2,
h3,
h4 {{
    color: #00FFD1 !important;
    font-weight: bold;
}}

/* SIDEBAR */

section[data-testid="stSidebar"] {{
    background-color: {sidebar_color};
}}

/* SIDEBAR TEXT */

section[data-testid="stSidebar"] * {{
    color: {text_color} !important;
}}

/* TEXT INPUT */

.stTextInput input {{
    background-color: #1E1E1E !important;
    color: white !important;
    -webkit-text-fill-color: white !important;
    caret-color: white !important;

    border-radius: 10px !important;
    border: 2px solid #00FFD1 !important;
}}

/* NUMBER INPUT */

.stNumberInput input {{
    background-color: #1E1E1E !important;
    color: white !important;
    -webkit-text-fill-color: white !important;
    caret-color: white !important;

    border-radius: 10px !important;
    border: 2px solid #00FFD1 !important;
}}

/* DATE INPUT */

.stDateInput input {{
    background-color: #1E1E1E !important;
    color: white !important;
    -webkit-text-fill-color: white !important;
    caret-color: white !important;

    border-radius: 10px !important;
    border: 2px solid #00FFD1 !important;
}}

/* SELECT BOX */

div[data-baseweb="select"] > div {{
    background-color: #1E1E1E !important;
    color: white !important;

    border-radius: 10px !important;
    border: 2px solid #00FFD1 !important;
}}

/* DROPDOWN TEXT */

div[data-baseweb="select"] * {{
    color: white !important;
}}

/* PLACEHOLDER */

input::placeholder {{
    color: #BBBBBB !important;
}}

/* METRICS */

[data-testid="stMetricValue"] {{
    color: #00FFD1 !important;
    font-size: 32px;
    font-weight: bold;
}}

/* BUTTON */

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

/* ALERTS */

.stAlert {{
    border-radius: 10px !important;
}}

</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ---------------- #

st.title("💰 SmartSpend AI")

# ---------------- LOAD DATA ---------------- #

df = pd.read_sql_query(
    "SELECT * FROM expenses",
    conn
)

total_expense = (
    df["amount"].sum()
    if not df.empty else 0
)

# ---------------- BUDGET TRACKER ---------------- #

st.sidebar.subheader("💵 Monthly Budget")

budget = st.sidebar.number_input(
    "Set Budget",
    min_value=1000,
    value=5000
)

remaining = budget - total_expense

progress = min(
    total_expense / budget,
    1.0
)

st.sidebar.progress(progress)

st.sidebar.metric(
    "Remaining Budget",
    f"₹{remaining}"
)

# ---------------- DASHBOARD ---------------- #

if menu == "Dashboard":

    st.subheader(
        "Welcome to Your AI Finance Dashboard 🚀"
    )

    total_records = len(df)

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Total Expenses",
            f"₹{total_expense}"
        )

    with col2:

        st.metric(
            "Total Records",
            total_records
        )

    st.info(
        "Track your spending smartly 💡"
    )

    if not df.empty:

        category_summary = (
            df.groupby("category")["amount"]
            .sum()
        )

        highest_category = (
            category_summary.idxmax()
        )

        highest_amount = (
            category_summary.max()
        )

        st.subheader(
            "🤖 AI Financial Insights"
        )

        st.success(
            f"Highest spending category: "
            f"{highest_category} "
            f"(₹{highest_amount})"
        )

        if highest_category == "Food":

            st.warning(
                "🍔 Food expenses are high."
            )

        elif highest_category == "Shopping":

            st.warning(
                "🛍️ Shopping expenses are increasing."
            )

        elif highest_category == "Entertainment":

            st.warning(
                "🎬 Entertainment spending is high."
            )

        else:

            st.success(
                "✅ Spending looks balanced."
            )

        # ---------------- PIE CHART ---------------- #

        st.subheader(
            "📊 Expense Distribution"
        )

        category_data = (
            df.groupby("category")["amount"]
            .sum()
            .reset_index()
        )

        fig = px.pie(
            category_data,
            names="category",
            values="amount",
            hole=0.4
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

# ---------------- ADD EXPENSE ---------------- #

elif menu == "Add Expense":

    st.subheader("➕ Add New Expense")

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
            "Entertainment"
        ]
    )

    expense_date = st.date_input(
        "Select Date"
    )

    if st.button("💾 Save Expense"):

        if title == "" or amount == 0:

            st.error(
                "Please fill all fields."
            )

        else:

            cursor.execute(
                """
                INSERT INTO expenses
                (
                    title,
                    amount,
                    category,
                    date
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    title,
                    amount,
                    category,
                    str(expense_date)
                )
            )

            conn.commit()

            st.success(
                "Expense Saved Successfully ✅"
            )

            st.balloons()

# ---------------- VIEW EXPENSES ---------------- #

elif menu == "View Expenses":

    st.subheader("📋 All Expenses")

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

        # ---------------- ANALYTICS ---------------- #

        st.subheader(
            "📊 Expense Analytics"
        )

        category_data = (
            filtered_df.groupby("category")["amount"]
            .sum()
            .reset_index()
        )

        st.bar_chart(
            category_data.set_index("category")
        )

        fig = px.pie(
            category_data,
            names="category",
            values="amount",
            title="Expense Distribution"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # ---------------- DOWNLOAD CSV ---------------- #

        csv = filtered_df.to_csv(
            index=False
        )

        st.download_button(
            label="📥 Download Expense Report",
            data=csv,
            file_name="expense_report.csv",
            mime="text/csv"
        )

    else:

        st.warning(
            "No expenses added yet."
        )

# ---------------- FOOTER ---------------- #

st.markdown("""
<hr>
<center>
Made with ❤️ by Gundapureddy Manju Bhargavi
</center>
""", unsafe_allow_html=True)