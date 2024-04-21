import streamlit as st
import sqlite3
import csv
import os
import re

def clean(string):
    # Remove any characters that are not alphanumeric or underscores
    cleaned_name = re.sub(r'\W+', '', string)
    # Replace spaces with underscores
    cleaned_name = cleaned_name.replace(' ', '_')
    # Ensure the first character is not a number
    if cleaned_name[0].isdigit():
        cleaned_name = '_' + cleaned_name
    return cleaned_name

# App Title
st.title("Result :orange[Analyzer]")
st.subheader("", divider="gray")

# Connect to an existing database or create a new one
db_path = os.path.join(os.path.dirname(__file__), '..', 'marian.db')
conn = sqlite3.connect(db_path)
# Create a cursor object
cur = conn.cursor()

# Create two columns side by side
col1, col2 = st.columns([1, 3], gap="medium")

# Place the text input for the class name in the second column
class_name = col1.text_input("Enter class name:", placeholder="eg: S6R2")

# Place the upload button in the first column
uploaded_file = col2.file_uploader("Upload student details (.csv):", type="csv")

if uploaded_file is not None:
    if not class_name:
        st.warning("Please enter the name of the class being added...")
    # Read the CSV file
    csv_data = csv.reader(uploaded_file.getvalue().decode('utf-8').splitlines())
    # Skipping college name in the csv file
    next(csv_data)
    # Column names
    columns = next(csv_data)
    columns.append("Class")  # Add the class name column
    print(columns)
    # Use the class name entered by the user

    columns_with_datatypes = []
    for col in columns:
        if clean(col) == 'AdmnNo':
            columns_with_datatypes.append('AdmnNo TEXT PRIMARY KEY')
        else:
            columns_with_datatypes.append(f'{clean(col)} TEXT')
            
        # columns_with_datatypes.append(f'{clean(col)} TEXT')
    print(columns_with_datatypes)

    table_name = "Students"
    # Create the table if it doesn't exist
    # print(f'''CREATE TABLE IF NOT EXISTS {table_name} ({', '.join([col for col in columns_with_datatypes])})''')
    cur.execute(f'''CREATE TABLE IF NOT EXISTS {table_name} ({', '.join([col for col in columns_with_datatypes])})''')
    # Insert the data into the table
    for row in csv_data:
        row.append(class_name)  # Add the class name to the row
        try:
            cur.execute(f"INSERT INTO {table_name} VALUES ({', '.join(['?' for _ in row])})", row)
        except sqlite3.IntegrityError:
            st.warning(f"Student with University Registration Number {row[4]} already exists in the database.")
            break
    conn.commit()
    st.success(f"CSV data has been uploaded and inserted into the '{table_name}' table.")

# Close the connection
conn.close()