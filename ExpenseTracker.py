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
    for card in ['RBC', 'Rogers', 'CIBC', 'CIBC Costco', 'Walmart', 'Triangle', 'Scotia']:
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
    
# Initialize default and custom categories
default_categories = [
    "🧒 Day Care", "🎓 Education", "🎮 Entertainment", "🍽️ Food", "🛒 Grocery",
    "🛡️ Insurance", "📈 Investments", "🏥 Medical", "🧾 Miscellaneous",
    "🏠 Rent", "🛍️ Shopping", "🚌 Transportation", "💡 Utilities"
]

if "categories" not in st.session_state:
    st.session_state.categories = default_categories.copy()


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

# Jobin
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
        st.sidebar.success(f"₹{jobin} Jobin Income added!")

# Anna
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
        st.sidebar.success(f"₹{anna} Anna Income added!")

# Izaak
with st.sidebar.form("izaak_form"):
    izaak = st.number_input("Izaak Income", min_value=0.0, step=1.0, key="izaak_income_input")
    if st.form_submit_button("Add Izaak Income"):
        today = datetime.date.today()
        add_transaction({
            "type": "Income",
            "date": today,
            "month": today.strftime("%B %Y"),
            "amount": izaak,
            "category": "Income",
            "description": "Izaak CCB",
            "card": ""
        })
        st.sidebar.success(f"₹{izaak} Izaak Income added!")



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


# -----------------------------
# Category Management (sorted + safe)
# -----------------------------
# Ensure categories are sorted
st.session_state.categories = sorted(st.session_state.categories)

# Select category with no default selected
category_options = ["-- Select Category --"] + st.session_state.categories
e_cat = st.sidebar.selectbox("Category", category_options, index=0, key="category_select")

# Add Custom Category
st.sidebar.markdown("### ➕ Add Custom Category")
new_cat = st.sidebar.text_input("Add Category", key="new_category_input")
if st.sidebar.button("Add Category", key="add_category_btn") and new_cat.strip():
    cat_to_add = new_cat.strip()
    if cat_to_add not in st.session_state.categories:
        st.session_state.categories.append(cat_to_add)
        st.sidebar.success(f"✅ Added: {cat_to_add}")
    else:
        st.sidebar.warning("Category already exists.")

# Remove Category
st.sidebar.markdown("### ➖ Remove Category")
remove_cat = st.sidebar.selectbox(
    "Select category to remove",
    ["-- Select Category --"] + st.session_state.categories,
    index=0,
    key="remove_category"
)
if st.sidebar.button("Remove Selected Category", key="remove_category_btn"):
    if remove_cat != "-- Select Category --":
        st.session_state.categories.remove(remove_cat)
        st.sidebar.success(f"❌ Removed: {remove_cat}")
        st.rerun()
    else:
        st.sidebar.warning("Please select a valid category.")


e_desc = st.sidebar.text_area("Notes / Tags (optional)")
e_card = st.sidebar.selectbox("Paid using Card?", ["None"] + get_card_limits()["card"].tolist())
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
rep_card = st.sidebar.selectbox("Repayment Card", get_card_limits()["card"].tolist())
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


st.sidebar.header("Manage Credit Cards")

new_card = st.sidebar.text_input("Add New Credit Card")
if st.sidebar.button("Add Credit Card") and new_card.strip():
    card_name = new_card.strip()
    existing_cards = [c.strip().lower() for c in get_card_limits()["card"].tolist()]
    if card_name.lower() in existing_cards:
        st.sidebar.warning("Card already exists.")
    else:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO card_limits (card, max_limit) VALUES (?, ?)", (card_name, 0))
        conn.commit()
        conn.close()
        st.sidebar.success(f"✅ Card '{card_name}' added!")
        st.rerun()

DEFAULT_CARDS = ["RBC", "Rogers", "CIBC", "CIBC Costco", "Walmart", "Triangle", "Scotia"]
# -----------------------------
# Remove Credit Card (any card)
# -----------------------------
st.sidebar.markdown("### ➖ Remove Credit Card")

all_cards = get_card_limits()["card"].tolist()

if all_cards:
    card_to_remove = st.sidebar.selectbox(
        "Select a card to remove",
        ["-- Select card --"] + all_cards,
        index=0,
        key="remove_credit_card"
    )

    if st.sidebar.button("Remove Selected Card"):
        if card_to_remove != "-- Select card --":
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("DELETE FROM card_limits WHERE card = ?", (card_to_remove,))
            conn.commit()
            conn.close()
            st.sidebar.success(f"❌ Removed card: {card_to_remove}")
            st.rerun()
        else:
            st.sidebar.warning("Please select a card to remove.")
else:
    st.sidebar.info("No cards available to remove.")



# -----------------------------
# Dashboard Summary (Always Show)
# -----------------------------
st.subheader("Dashboard Summary")
# Get data BEFORE using df
df = get_transactions()
savings_total = get_savings()

# Safely calculate totals
income_total = df[df["type"] == "Income"]["amount"].sum() if not df.empty else 0
expense_total = df[df["type"] == "Expense"]["amount"].sum() if not df.empty else 0
balance = income_total - expense_total

# Show summary metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Income", f"₹{income_total:,.2f}")
col2.metric("Total Expenses", f"₹{expense_total:,.2f}")
col3.metric("Total Savings", f"₹{savings_total:,.2f}")
col4.metric("Remaining Balance", f"₹{balance:,.2f}")

# Pie Chart of Expenses
st.subheader("Expenses by Category (Pie Chart)")
if not df.empty:
    chart = df[df["type"] == "Expense"].groupby("category")["amount"].sum()
    if not chart.empty:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            fig, ax = plt.subplots(figsize=(4, 4))
            chart.plot.pie(autopct='%1.1f%%', ax=ax)
            plt.ylabel("")
            plt.tight_layout()
            st.pyplot(fig, bbox_inches='tight')
    else:
        st.info("No expenses yet to plot.")
else:
    st.info("No transactions to display.")

        
# -----------------------------
# Monthly Report Section
# -----------------------------
st.subheader("Monthly Report")

# Step 1: Get available months
available_months = df['month'].unique().tolist()

if available_months:
    selected_month = st.selectbox("Select Month for Report", sorted(available_months))

    # Step 2: Filter by selected month
    df_month = df[df['month'] == selected_month]

    # Step 3: Monthly Summary
    income_total = df_month[df_month["type"] == "Income"]["amount"].sum()
    expense_total = df_month[df_month["type"] == "Expense"]["amount"].sum()
    balance = income_total - expense_total

    col1, col2, col3 = st.columns(3)
    col1.metric("Monthly Income", f"₹{income_total:,.2f}")
    col2.metric("Monthly Expenses", f"₹{expense_total:,.2f}")
    col3.metric("Monthly Balance", f"₹{balance:,.2f}")

    # Step 4: Download Monthly CSV
    csv_month = df_month.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=f"Download {selected_month} Report (CSV)",
        data=csv_month,
        file_name=f"{selected_month.replace(' ', '_')}_report.csv",
        mime="text/csv"
    )
else:
    st.info("No transactions available yet for Monthly Report.")

# -----------------------------
# Edit/Delete by Date Section
# -----------------------------
st.subheader("Edit or Delete Transactions by Date")

if not df.empty:
    selected_date = st.date_input("Select a date to view/edit transactions", datetime.date.today())
    df_selected = df[df['date'] == str(selected_date)]

    if not df_selected.empty:
        st.success(f"{len(df_selected)} transactions found for {selected_date}")
        
        for i, row in df_selected.iterrows():
            col1, col2, col3, col4 = st.columns([4, 4, 1, 1])
            with col1:
                st.write(f"₹{row['amount']} | {row['category']} | {row['description']}")
            with col2:
                st.write(f"Card: {row['card']}")
            with col3:
                if st.button("✏️ Edit", key=f"edit_button_{row['id']}"):
                    st.session_state[f"edit_mode_{row['id']}_edit"] = True
            with col4:
                if st.button("🗑️ Delete", key=f"delete_button_{row['id']}"):
                    delete_transaction(row['id'])
                    st.success("Transaction Deleted!")
                    st.rerun()

            if st.session_state.get(f"edit_mode_{row['id']}_edit", False):
                with st.form(f"edit_form_{row['id']}_edit"):
                    new_amt = st.number_input("New Amount", value=row['amount'], key=f"amt_{row['id']}_edit")
                    new_desc = st.text_input("New Description", value=row['description'], key=f"desc_{row['id']}_edit")
                    col_save, col_cancel = st.columns(2)
                    with col_save:
                        if st.form_submit_button("Update"):
                            update_transaction(row['id'], new_amt, new_desc)
                            st.success("Transaction Updated!")
                            st.session_state[f"edit_mode_{row['id']}_edit"] = False
                            st.rerun()
                    with col_cancel:
                        if st.form_submit_button("Cancel"):
                            st.session_state[f"edit_mode_{row['id']}_edit"] = False
                            st.rerun()
    else:
        st.warning("No transactions found for selected date.")
else:
    st.info("No transactions to edit yet.")



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
            



st.subheader("Search Transactions")
search_term = st.text_input("Search description, category, or card")

if search_term:
    df_search = df[df.apply(lambda row: search_term.lower() in str(row).lower(), axis=1)]
    if not df_search.empty:
        st.dataframe(df_search)
    else:
        st.warning("No matching transactions found.")

st.subheader("Filter by Category")
selected_cat = st.selectbox("Choose Category", sorted(set(df["category"])))

df_filtered = df[df["category"] == selected_cat]
if not df_filtered.empty:
    st.dataframe(df_filtered)
else:
    st.info("No transactions in this category.")



st.subheader("Income vs Expense Ratio")
income_total = df[df["type"] == "Income"]["amount"].sum()
expense_total = df[df["type"] == "Expense"]["amount"].sum()

if income_total > 0:
    ratio = (income_total - expense_total) / income_total
    st.write(f"🧮 You're saving {ratio*100:.2f}% of your income.")
else:
    st.warning("No income recorded yet.")




st.subheader("Gold Tracker Amount")

goal_name = "Gold Loan"
goal_target = 18500

if "goal_progress_gold" not in st.session_state:
    st.session_state.goal_progress_gold = 0.0

st.write(f"🎯 Goal: {goal_name}")
st.write(f"💰 Target: ₹{goal_target:,}")
st.write(f"✅ Collected: ₹{st.session_state.goal_progress_gold:,}")
st.progress(min(st.session_state.goal_progress_gold / goal_target, 1.0))

with st.form("add_to_goal_form_gold"):
    add_goal_amt = st.number_input("Add to Gold Loan Goal", min_value=0.0, step=100.0)
    if st.form_submit_button("Add"):
        st.session_state.goal_progress_gold += add_goal_amt
        st.success(f"Added ₹{add_goal_amt:.2f} to {goal_name}")
        st.rerun()


st.subheader("Vacation to Kerala")

goal_name = "Naattil Pokan Paisa"
goal_target = 10000

if "goal_progress_kerala" not in st.session_state:
    st.session_state.goal_progress_kerala = 0.0

st.write(f"🎯 Goal: {goal_name}")
st.write(f"💰 Target: ₹{goal_target:,}")
st.write(f"✅ Collected: ₹{st.session_state.goal_progress_kerala:,}")
st.progress(min(st.session_state.goal_progress_kerala / goal_target, 1.0))

with st.form("add_to_goal_form_kerala"):
    add_goal_amt = st.number_input("Add to Kerala Goal", min_value=0.0, step=100.0)
    if st.form_submit_button("Add"):
        st.session_state.goal_progress_kerala += add_goal_amt
        st.success(f"Added ₹{add_goal_amt:.2f} to {goal_name}")
        st.rerun()



# -----------------------------
# Soft Reset
# -----------------------------
st.subheader("Reset Transactions")
if st.button("Reset All Transactions"):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('DELETE FROM transactions')
    c.execute('UPDATE savings SET amount = 0 WHERE id = 1')
    conn.commit()
    conn.close()
    st.success("All transactions and savings reset!")
    st.rerun()


# -----------------------------
# Download CSV
# -----------------------------
st.subheader("Download Transactions")
if not df.empty:
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV File", csv, "transactions.csv", "text/csv")
