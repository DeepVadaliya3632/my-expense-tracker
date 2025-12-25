import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# --- CONFIGURATION ---
DATA_FILE = 'expenses.csv'

# --- FUNCTIONS ---
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        # Create an empty dataframe if file doesn't exist
        return pd.DataFrame(columns=["Date", "Category", "Item", "Amount"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# --- APP LAYOUT ---
st.set_page_config(page_title="Personal Expense Tracker", layout="wide")
st.title("💰 Personal Expense Tracker")

# Load existing data
df = load_data()

# --- SIDEBAR: ADD EXPENSE ---
st.sidebar.header("Add New Expense")

with st.sidebar.form("expense_form", clear_on_submit=True):
    date = st.date_input("Date", datetime.now())
    category = st.selectbox("Category", ["Food", "Transport", "Housing", "Utilities", "Entertainment", "Healthcare", "Other"])
    item = st.text_input("Description (e.g., Lunch, Uber)")
    amount = st.number_input("Amount (₹)", min_value=0.01, format="%.2f")
    
    submitted = st.form_submit_button("Add Expense")
    
    if submitted:
        new_data = pd.DataFrame({
            "Date": [date],
            "Category": [category],
            "Item": [item],
            "Amount": [amount]
        })
        df = pd.concat([df, new_data], ignore_index=True)
        save_data(df)
        st.success("Expense added successfully!")

# --- MAIN DASHBOARD ---

if not df.empty:
    # Ensure proper data types
    df["Date"] = pd.to_datetime(df["Date"])
    df["Amount"] = pd.to_numeric(df["Amount"])

    # Top Metrics
    total_spent = df["Amount"].sum()
    st.metric(label="Total Lifetime Spending", value=f"${total_spent:,.2f}")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📝 Recent Transactions")
        # Show most recent first
        st.dataframe(df.sort_values(by="Date", ascending=False), use_container_width=True)

        # Delete functionality (Simple implementation by index)
        st.write("---")
        idx_to_delete = st.number_input("Enter Index to Delete (see left column above)", min_value=0, step=1, value=0)
        if st.button("Delete Entry"):
            if idx_to_delete in df.index:
                df = df.drop(idx_to_delete).reset_index(drop=True)
                save_data(df)
                st.rerun()
            else:
                st.error("Index not found.")

    with col2:
        st.subheader("📊 Spending by Category")
        # Group data by category
        category_group = df.groupby("Category")["Amount"].sum().reset_index()
        
        # Donut Chart
        fig = px.pie(category_group, values='Amount', names='Category', hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

        # Monthly Trend
        st.subheader("📅 Monthly Trend")
        df['Month'] = df['Date'].dt.to_period('M').astype(str)
        monthly_group = df.groupby("Month")["Amount"].sum().reset_index()
        fig2 = px.bar(monthly_group, x='Month', y='Amount')
        st.plotly_chart(fig2, use_container_width=True)

else:
    st.info("No expenses found. Add your first expense using the sidebar!")