import streamlit as st
import pandas as pd
import numpy as np

#Title
st.title ("Hello Group Of Students")
st.write( "All are learning Data Science")

#Create Sample Data Frame
df = pd.DataFrame({
    'First Coloumn' : [1,2,3,4],
    'Second Coloumn' :[10,20,30,40]
})
st.write ("This is sample Data Frmae")
st.write(df)

#How to create line chart.
chart_data =pd.DataFrame( np.random.randn(20,3), columns =['a','b','c'])
st.line_chart(chart_data)

# How to use user input fields.
st.title("Streamlit Text input for users")
name =st.text_input("Enter your name: ")
st.write (f"Hello, {name}, How are you today- Congratulation you are studying DataScience from Sir Shahzab")

#Slider Exmaple
age = st.slider("Select your Age: ", 0,100)
st.write(f"Hello, {name} your age is : {age}")

#How to use Drop down Menu
options =["business Partners", "Technology Partners", "Direct- Customers", "Support Team"]
choice =st.selectbox("Select your parters :", options)
st.write(f"{name}, You have selected {choice}")

         
