# ===========================
# ExpenseTracker.py (Final Version with Secure Login, Enter Login, Dismissible Reminder)
# ===========================

import streamlit as st
import pandas as pd
import sqlite3
import datetime
import os

# Streamlit Config
st.set_page_config(page_title="Expense Tracker", layout="wide")

# Database Config
DB_FILE = "expense_data.db"

# ---------- Database Functions ----------

def create_tables():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            date TEXT,
            month TEXT,
            amount REAL,
            category TEXT,
            description TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS savings (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            amount REAL
        )
    ''')
    c.execute('INSERT OR IGNORE INTO savings (id, amount) VALUES (1, 0)')
    conn.commit()
    conn.close()

def add_transaction(trx):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        INSERT INTO transactions (type, date, month, amount, category, description)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (trx["type"], trx["date"], trx["month"], trx["amount"], trx["category"], trx["description"]))
    conn.commit()
    conn.close()

def get_transactions():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM transactions", conn)
    conn.close()
    return df

def delete_transaction(trx_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('DELETE FROM transactions WHERE id = ?', (trx_id,))
    conn.commit()
    conn.close()

def update_transaction(trx_id, amount, description):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('UPDATE transactions SET amount = ?, description = ? WHERE id = ?', (amount, description, trx_id))
    conn.commit()
    conn.close()

def add_savings(amount):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('UPDATE savings SET amount = amount + ?', (amount,))
    conn.commit()
    conn.close()

def get_savings():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT amount FROM savings WHERE id = 1')
    savings = c.fetchone()[0]
    conn.close()
    return savings

# Create database tables
create_tables()

# ---------- App Start ----------

# Secure Login
def login(username, password):
    correct_username = st.secrets.credentials.username
    correct_password = st.secrets.credentials.password
    return username == correct_username and password == correct_password

# Initialize login and reminder states
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "show_reminder" not in st.session_state:
    st.session_state.show_reminder = True

# Login Page with Form (Enter Key Support)
if not st.session_state.logged_in:
    st.title("Login to Expense Tracker")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            if login(username, password):
                st.session_state.logged_in = True
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Incorrect username or password")
    st.stop()

# Reminder with Dismiss Option
if st.session_state.show_reminder:
    with st.container():
        st.info(f"🔔 Reminder: Please record today's expenses! ({datetime.date.today().strftime('%B %d, %Y')})")
        if st.button("Dismiss Reminder ❌"):
            st.session_state.show_reminder = False
            st.rerun()

# Title
st.title("Expense Tracker Dashboard")

# Sidebar
st.sidebar.header("Add Transactions")

# Add Income
st.sidebar.subheader("Add Income")
income_amount = st.sidebar.number_input("Income Amount", min_value=0.0, step=0.01)
if st.sidebar.button("Add Income"):
    today = datetime.date.today()
    trx = {
        "type": "Income",
        "date": today,
        "month": today.strftime("%B %Y"),
        "amount": income_amount,
        "category": "Income",
        "description": "Salary / Income"
    }
    add_transaction(trx)
    st.success(f"Income of ₹{income_amount} added!")

# Add Savings
st.sidebar.subheader("Set Savings Contribution")
savings_amount = st.sidebar.number_input("Savings Amount", min_value=0.0, step=0.01)
if st.sidebar.button("Contribute to Savings"):
    add_savings(savings_amount)
    st.success(f"₹{savings_amount} contributed to Savings!")

# Add Expense
st.sidebar.subheader("Add Expense")
expense_amount = st.sidebar.number_input("Expense Amount", min_value=0.0, step=0.01)
expense_category = st.sidebar.selectbox("Category", [
    "Food", "Grocery", "Rent", "Utilities", "Education",
    "Transportation", "Medical", "Entertainment", "Insurance",
    "Investments", "Shopping", "Miscellaneous"
])
expense_description = st.sidebar.text_input("Description (optional)")
expense_date = st.sidebar.date_input("Expense Date", datetime.date.today())

if st.sidebar.button("Add Expense"):
    trx = {
        "type": "Expense",
        "date": expense_date,
        "month": expense_date.strftime("%B %Y"),
        "amount": expense_amount,
        "category": expense_category,
        "description": expense_description
    }
    add_transaction(trx)
    st.success(f"Expense of ₹{expense_amount} added under {expense_category}!")

# Show Transactions
st.subheader("Transaction History")

df = get_transactions()

if not df.empty:
    st.dataframe(df)

    for i, row in df.iterrows():
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button(f"Edit {row['id']}"):
                with st.form(f"edit_form_{row['id']}"):
                    new_amount = st.number_input("New Amount", value=row['amount'])
                    new_desc = st.text_input("New Description", value=row['description'])
                    submit_edit = st.form_submit_button("Update")
                    if submit_edit:
                        update_transaction(row['id'], new_amount, new_desc)
                        st.success("Transaction Updated!")
                        st.rerun()
        with col2:
            if st.button(f"Delete {row['id']}"):
                delete_transaction(row['id'])
                st.success("Transaction Deleted!")
                st.rerun()
else:
    st.info("No transactions yet!")

# Summary
st.subheader("Summary")

if not df.empty:
    income_total = df[df["type"] == "Income"]["amount"].sum()
    expense_total = df[df["type"] == "Expense"]["amount"].sum()
    savings_total = get_savings()
    remaining_balance = income_total - savings_total - expense_total

    st.metric("Total Income", f"₹{income_total:,.2f}")
    st.metric("Total Savings", f"₹{savings_total:,.2f}")
    st.metric("Total Expenses", f"₹{expense_total:,.2f}")
    st.metric("Remaining Balance", f"₹{remaining_balance:,.2f}")

    # Expenses by Category
    st.subheader("Expenses by Category")
    exp_chart = df[df["type"] == "Expense"].groupby("category")["amount"].sum()
    st.bar_chart(exp_chart)
else:
    st.info("No transactions recorded yet.")

# Download Transactions
st.subheader("Download Transactions")
if st.button("Download CSV"):
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(label="Download Transactions", data=csv, file_name='transactions.csv', mime='text/csv')
