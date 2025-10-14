import streamlit as st
import mysql.connector
import pandas as pd

st.title("MySQL Data Entry Form for Account Table")
st.write("Search, edit, or add new accounts in MySQL.")

# --- MySQL connection ---
def get_connection():
    return mysql.connector.connect(
        host="myhsldb.cjsysowmeja2.us-east-2.rds.amazonaws.com",
        user="admin",
        password="Mmahin2006",
        database="myhsldb"
    )

# --- Insert or Update ---
def upsert_account(id, name, phone, industry, rating, country, active, account_type):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        if id:
            query = """
                UPDATE Account SET
                Name=%s, Phone=%s, Industry=%s, Rating=%s, Country=%s, Active=%s, AccountType=%s
                WHERE id=%s
            """
            cursor.execute(query, (name, phone, industry, rating, country, active, account_type, id))
        else:
            query = """
                INSERT INTO Account
                (Name, Phone, Industry, Rating, Country, Active, AccountType)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (name, phone, industry, rating, country, active, account_type))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        st.error(f"❌ Database Error: {e}")
        return False

# --- Search ---
def search_accounts(name_search):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM Account WHERE Name LIKE %s"
        cursor.execute(query, (f"%{name_search}%",))
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results
    except Exception as e:
        st.error(f"❌ Database Error: {e}")
        return []

def normalize_keys(record):
    return {
        "id": record.get("id"),
        "name": record.get("Name", ""),
        "phone": record.get("Phone", ""),
        "industry": record.get("Industry", ""),
        "rating": record.get("Rating", ""),
        "country": record.get("Country", ""),
        "active": record.get("Active", ""),
        "account_type": record.get("AccountType", "")
    }

# --- Form Widget Builder ---
def build_account_fields(prefix="new", account=None):
    if account is None:
        account = {}

    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Name", value=account.get("name", ""), key=f"name_{prefix}")

        AccountType = [""] + [
            "Business Partners", "Technology Partners", "Direct Customers", "Support Team", "Prospect",
            "Customer - Direct", "Customer - Channel", "Channel Partner / Reseller",
            "Installation Partner", "Technology Partner"
        ]
        account_type_index = AccountType.index(account.get("account_type", "")) if account.get("account_type") in AccountType else 0
        account_type = st.selectbox("Account Type", AccountType, index=account_type_index, key=f"account_type_{prefix}")

        Rating = [""] + ["Hot", "Warm", "Cold"]
        rating_index = Rating.index(account.get("rating", "")) if account.get("rating") in Rating else 0
        rating = st.selectbox("Rating", Rating, index=rating_index, key=f"rating_{prefix}")

        country = st.text_input("Country", value=account.get("country", ""), key=f"country_{prefix}")

    with col2:
        phone = st.text_input("Phone", value=account.get("phone", ""), key=f"phone_{prefix}")

        Industry = [""] + [
            "Apparel", "Banking", "Biotechnology", "Chemicals", "Communications", "Construction",
            "Consulting", "Education", "Electronics", "Energy", "Engineering", "Entertainment",
            "Environmental", "Finance", "Food & Beverage", "Government", "Healthcare", "Hospitality",
            "Insurance", "Machinery", "Manufacturing", "Media", "Not For Profit", "Recreation",
            "Retail", "Shipping", "Technology", "Telecommunications", "Transportation", "Utilities",
            "Other"
        ]
        industry_index = Industry.index(account.get("industry", "")) if account.get("industry") in Industry else 0
        industry = st.selectbox("Industry", Industry, index=industry_index, key=f"industry_{prefix}")

        Active = [""] + ["Yes", "No"]
        active_index = Active.index(account.get("active", "")) if account.get("active") in Active else 0
        active = st.selectbox("Active", Active, index=active_index, key=f"active_{prefix}")

    return {
        "name": name,
        "phone": phone,
        "industry": industry,
        "rating": rating,
        "country": country,
        "active": active,
        "account_type": account_type
    }

# --- Search Section ---
st.write("---")
st.subheader("Search Accounts by Name")
search_name = st.text_input("Enter Name to search for editing")
if search_name:
    results = search_accounts(search_name)
    if results:
        st.success(f"Found {len(results)} record(s)")
        df = pd.DataFrame(results).drop(columns=["id"])
        st.dataframe(df)

        options = [f"{r['Name']} | {r['Phone']} | {r['Industry']}" for r in results]
        selected_idx = st.selectbox("Select record to edit", range(len(results)), format_func=lambda x: options[x])
        record_to_edit = normalize_keys(results[selected_idx])

        st.write("Edit the selected record:")
        # Removed clear_on_submit=True so fields stay after update
        with st.form(f"edit_form_{record_to_edit['id']}"):
            updated_data = build_account_fields(prefix=f"edit_{record_to_edit['id']}", account=record_to_edit)
            updated_data["id"] = record_to_edit["id"]
            submitted = st.form_submit_button("Update Record")
            if submitted:
                success = upsert_account(**updated_data)
                if success:
                    st.success("✅ Record updated successfully!")

# --- Insert New Record ---
st.write("---")
st.subheader("Add New Account")
with st.form("new_form", clear_on_submit=True):
    new_account = build_account_fields(prefix="new")
    submitted_new = st.form_submit_button("Save New Record")
    if submitted_new:
        if new_account["name"] and new_account["phone"]:
            success = upsert_account(id=None, **new_account)
            if success:
                st.success("✅ New record successfully saved to MySQL!")
        else:
            st.warning("Please enter at least Name and Phone before saving.")
