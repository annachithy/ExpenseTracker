import streamlit as st
import pandas as pd
import sqlite3
import datetime
import matplotlib.pyplot as plt

st.set_page_config(page_title="Expense Tracker", layout="wide")
DB_FILE = "expense_data.db"

# -----------------------------
# Database Setup
# -----------------------------
def create_tables():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT, date TEXT, month TEXT,
            amount REAL, category TEXT,
            description TEXT, card TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS savings (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            amount REAL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS card_limits (
            card TEXT PRIMARY KEY,
            max_limit REAL
        )
    ''')
    c.execute('INSERT OR IGNORE INTO savings (id, amount) VALUES (1, 0)')
    for card in ['RBC', 'Rogers', 'CIBC', 'CIBC Costco', 'Walmart']:
        c.execute('INSERT OR IGNORE INTO card_limits (card, max_limit) VALUES (?, ?)', (card, 0))
    conn.commit()
    conn.close()

create_tables()

# -----------------------------
# Database Functions
# -----------------------------
def add_transaction(trx):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        INSERT INTO transactions (type, date, month, amount, category, description, card)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (trx["type"], trx["date"], trx["month"], trx["amount"], trx["category"], trx["description"], trx["card"]))
    conn.commit()
    conn.close()

def get_transactions():
    return pd.read_sql("SELECT * FROM transactions ORDER BY date DESC", sqlite3.connect(DB_FILE))

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

def update_savings(amount):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('UPDATE savings SET amount = amount + ?', (amount,))
    conn.commit()
    conn.close()

def set_savings(amount):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('UPDATE savings SET amount = ?', (amount,))
    conn.commit()
    conn.close()

def get_savings():
    conn = sqlite3.connect(DB_FILE)
    return conn.execute('SELECT amount FROM savings WHERE id=1').fetchone()[0]

def get_card_limits():
    return pd.read_sql("SELECT * FROM card_limits", sqlite3.connect(DB_FILE))

def update_card_limit(card, limit):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('UPDATE card_limits SET max_limit = ? WHERE card = ?', (limit, card))
    conn.commit()
    conn.close()
# -----------------------------
# Secure Login and Session Setup
# -----------------------------
def login(username, password):
    return username == st.secrets.credentials.username and password == st.secrets.credentials.password

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "show_reminder" not in st.session_state:
    st.session_state.show_reminder = True

if not st.session_state.logged_in:
    st.title("Login to Expense Tracker")
    with st.form("login_form"):
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.form_submit_button("Login"):
            if login(u, p):
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Invalid credentials")
    st.stop()

if st.session_state.show_reminder:
    st.info(f"🔔 Reminder: Record today's expenses! ({datetime.date.today():%B %d, %Y})")
    if st.button("Dismiss Reminder ❌"):
        st.session_state.show_reminder = False
        st.rerun()

st.title("Expense Tracker Dashboard")

# -----------------------------
# Sidebar - Add Income, Savings, Expense, Repayment
# -----------------------------

st.sidebar.header("Add Income")
with st.sidebar.form("jobin_form"):
    jobin = st.number_input("Jobin Income", min_value=0.0, step=1.0, key="jobin_income_input")
    if st.form_submit_button("Add Jobin Income"):
        today = datetime.date.today()
        add_transaction({
            "type": "Income",
            "date": today,
            "month": today.strftime("%B %Y"),
            "amount": jobin,
            "category": "Income",
            "description": "Jobin Salary",
            "card": ""
        })
        st.success(f"₹{jobin} Jobin Income added!")

with st.sidebar.form("anna_form"):
    anna = st.number_input("Anna Income", min_value=0.0, step=1.0, key="anna_income_input")
    if st.form_submit_button("Add Anna Income"):
        today = datetime.date.today()
        add_transaction({
            "type": "Income",
            "date": today,
            "month": today.strftime("%B %Y"),
            "amount": anna,
            "category": "Income",
            "description": "Anna Salary",
            "card": ""
        })
        st.success(f"₹{anna} Anna Income added!")


st.sidebar.header("Savings")
add_save = st.sidebar.number_input("Add to Savings", min_value=0.0, step=1.0)
if st.sidebar.button("Add Savings"):
    update_savings(add_save)
    st.sidebar.success("Savings updated.")

set_save = st.sidebar.number_input("Set Total Savings", min_value=0.0, step=1.0)
if st.sidebar.button("Set Savings"):
    set_savings(set_save)
    st.sidebar.success("Savings manually set.")

st.sidebar.header("Add Expense")
e_amt = st.sidebar.number_input("Expense Amount", min_value=0.0, step=1.0)
e_cat = st.sidebar.selectbox("Category", ["Food", "Grocery", "Rent", "Utilities", "Education",
                                          "Transportation", "Medical", "Entertainment", "Insurance",
                                          "Investments", "Shopping", "Miscellaneous"])
e_desc = st.sidebar.text_input("Expense Description")
e_card = st.sidebar.selectbox("Paid using Card?", ["None", "RBC", "Rogers", "CIBC", "CIBC Costco", "Walmart"])
e_date = st.sidebar.date_input("Expense Date", datetime.date.today())

if st.sidebar.button("Add Expense"):
    add_transaction({
        "type": "Expense",
        "date": e_date,
        "month": e_date.strftime("%B %Y"),
        "amount": e_amt,
        "category": e_cat,
        "description": e_desc,
        "card": e_card if e_card != "None" else ""
    })
    st.sidebar.success("Expense added.")

st.sidebar.header("Credit Card Repayment")
rep_card = st.sidebar.selectbox("Repayment Card", ["RBC", "Rogers", "CIBC", "CIBC Costco", "Walmart"])
rep_amt = st.sidebar.number_input("Repayment Amount", min_value=0.0, step=1.0)
if st.sidebar.button("Add Repayment"):
    today = datetime.date.today()
    add_transaction({
        "type": "Repayment",
        "date": today,
        "month": today.strftime("%B %Y"),
        "amount": rep_amt,
        "category": "Repayment",
        "description": f"Repayment to {rep_card}",
        "card": rep_card
    })
    st.sidebar.success("Repayment added.")

# -----------------------------
# Dashboard Summary
# -----------------------------
df = get_transactions()
savings_total = get_savings()

if not df.empty or savings_total > 0:
    income_total = df[df["type"] == "Income"]["amount"].sum()
    expense_total = df[df["type"] == "Expense"]["amount"].sum()
    balance = income_total - expense_total

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Income", f"₹{income_total:,.2f}")
    col2.metric("Total Expenses", f"₹{expense_total:,.2f}")
    col3.metric("Total Savings", f"₹{savings_total:,.2f}")
    col4.metric("Remaining Balance", f"₹{balance:,.2f}")



    st.subheader("Expenses by Category (Pie Chart)")
    chart = df[df["type"] == "Expense"].groupby("category")["amount"].sum()
    if not chart.empty:
        fig, ax = plt.subplots(figsize=(4, 4))  # reduce from (6,6) to (4,4)
        chart.plot.pie(autopct='%1.1f%%', ax=ax)
        plt.ylabel("")  # remove label
        st.pyplot(fig)

    else:
        st.info("No expenses yet to plot.")

# -----------------------------
# Transaction History (Edit/Delete/Cancel)
# -----------------------------
st.subheader("Transaction History")

if not df.empty:
    for i, row in df.iterrows():
        col1, col2, col3, col4 = st.columns([4, 4, 1, 1])
        with col1:
            st.write(f"₹{row['amount']} | {row['category']} | {row['description']} | {row['date']}")
        with col2:
            st.write(f"Card: {row['card']}")
        with col3:
            if st.button(f"✏️ Edit {row['id']}"):
                st.session_state[f"edit_mode_{row['id']}"] = True
        with col4:
            if st.button(f"🗑️ Delete {row['id']}"):
                delete_transaction(row['id'])
                st.success("Transaction Deleted!")
                st.rerun()

        if st.session_state.get(f"edit_mode_{row['id']}", False):
            with st.form(f"edit_form_{row['id']}"):
                new_amt = st.number_input("New Amount", value=row['amount'], key=f"amt_{row['id']}")
                new_desc = st.text_input("New Description", value=row['description'], key=f"desc_{row['id']}")
                col_save, col_cancel = st.columns(2)
                with col_save:
                    if st.form_submit_button("Update"):
                        update_transaction(row['id'], new_amt, new_desc)
                        st.success("Transaction Updated!")
                        st.session_state[f"edit_mode_{row['id']}"] = False
                        st.rerun()
                with col_cancel:
                    if st.form_submit_button("Cancel"):
                        st.session_state[f"edit_mode_{row['id']}"] = False
                        st.rerun()

else:
    st.info("No transactions yet.")

# -----------------------------
# Credit Card Dashboard
# -----------------------------
st.subheader("Credit Card Summary")
card_limits = get_card_limits()

for _, row in card_limits.iterrows():
    card = row["card"]
    limit = row["max_limit"]
    spent = df[(df["card"] == card) & (df["type"] == "Expense")]["amount"].sum()
    paid = df[(df["card"] == card) & (df["type"] == "Repayment")]["amount"].sum()
    balance = spent - paid
    available = limit - balance

    with st.expander(f"💳 {card}"):
        new_limit = st.number_input(f"{card} Max Limit", value=limit, key=f"limit_{card}")
        if st.button(f"Update {card} Limit", key=f"btn_{card}"):
            update_card_limit(card, new_limit)
            st.success(f"{card} limit updated.")
            st.rerun()
        st.write(f"**Spent:** ₹{spent:.2f}")
        st.write(f"**Repaid:** ₹{paid:.2f}")
        st.write(f"**Outstanding Balance:** ₹{balance:.2f}")
        st.write(f"**Available Credit:** ₹{available:.2f}")
        if limit > 0:
            st.progress(min(spent/limit, 1.0))

# -----------------------------
# Soft Reset
# -----------------------------
st.subheader("Reset Transactions")
if st.button("Reset All Transactions"):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('DELETE FROM transactions')
    conn.commit()
    conn.close()
    st.success("All transactions deleted!")
    st.rerun()

# -----------------------------
# Download CSV
# -----------------------------
st.subheader("Download Transactions")
if not df.empty:
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV File", csv, "transactions.csv", "text/csv")
