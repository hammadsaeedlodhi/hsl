import streamlit as st
import mysql.connector

st.title("MySQL Data Entry Form for Account Table")
st.write("Please fill the following fields and press Save to insert the record into MySQL")

# Create two columns for layout
col1, col2 = st.columns(2)

# Left column
with col1:
    name = st.text_input("Name")
    AccountType = ["Business Partners", "Technology Partners", "Direct Customers", "Support Team"]
    account_type = st.selectbox("Account Type", AccountType)
    Rating = ["Hot", "Warm", "Cold"]
    rating = st.selectbox("Rating", Rating)
    country = st.text_input("Country")

# Right column
with col2:
    phone = st.text_input("Phone")
    Industry = ["Banking", "Tele-Communication", "Pharmacists", "Bio Technology"]
    industry = st.selectbox("Industry", Industry)
    Active = ["Yes", "No"]
    active = st.selectbox("Active", Active)

# --- MySQL insert function ---
def insert_account(name, phone, industry, rating, country, active, account_type):
    try:
        conn = mysql.connector.connect(
            host="myhsldb.cjsysowmeja2.us-east-2.rds.amazonaws.com", 
            user="admin",                   
            password="Mmahin2006",               
            database="myhsldb"           
        )
        cursor = conn.cursor()

        insert_query = """
            INSERT INTO Account
            (Name, Phone, Industry, Rating, Country, Active, AccountType)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        values = (name, phone, industry, rating, country, active, account_type)

        cursor.execute(insert_query, values)
        conn.commit()
        cursor.close()
        conn.close()
        return True

    except Exception as e:
        st.error(f"❌ Database Error: {e}")
        return False


# --- Submit button ---
st.write("---")
if st.button("Save Record"):
    if name and phone:
        success = insert_account(name, phone, industry, rating, country, active, account_type)
        if success:
            st.success("✅ Record successfully saved to MySQL!")
    else:
        st.warning("Please enter at least Name and Phone before saving.")
