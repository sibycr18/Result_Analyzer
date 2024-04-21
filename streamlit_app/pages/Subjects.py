import streamlit as st
import sqlite3
import csv
import os

# App Title
st.title("Result :orange[Analyzer]")
st.subheader("", divider="gray")


# Connect to an existing database or create a new one
db_path = os.path.join(os.path.dirname(__file__), '..', 'marian.db')
conn = sqlite3.connect(db_path)
# Create a cursor object
cur = conn.cursor()

# Place the upload button in the first column
uploaded_file = st.file_uploader("Upload subject details (.csv):", type="csv")

if uploaded_file is not None:
    # Read the CSV file
    csv_data = csv.reader(uploaded_file.getvalue().decode('utf-8').splitlines())
    # Column names
    columns = next(csv_data)

    columns_with_datatypes = []
    for col in columns:
        columns_with_datatypes.append(f'{col} TEXT')
    print(columns_with_datatypes)

    table_name = "Subjects"
    # Create the table if it doesn't exist
    cur.execute(f'''CREATE TABLE IF NOT EXISTS {table_name} ({', '.join([col for col in columns_with_datatypes])}, UNIQUE(Code, Class))''')
    # Insert the data into the table
    for row in csv_data:
        try:
            cur.execute(f"INSERT INTO {table_name} VALUES ({', '.join(['?' for _ in row])})", row)
        except sqlite3.IntegrityError:
            st.warning(f"Subject {row[0]} for class {row[2]} already exists in the database.")

    conn.commit()
    st.success(f"CSV data has been uploaded and inserted into the '{table_name}' table.")

# Close the connection
conn.close()