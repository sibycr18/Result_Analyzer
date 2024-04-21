import streamlit as st
import sqlite3
import csv
import os
import re
import pandas as pd
import plotly.express as px

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
db_path = os.path.join(os.path.dirname(__file__), 'marian.db')
conn = sqlite3.connect(db_path)
# Create a cursor object
cur = conn.cursor()

st.subheader("Upload Exam Details:")

# Create two columns side by side
col1, col2 = st.columns([1, 3], gap="medium")

# Place the text input for the class name in the second column
exam_name = col1.text_input("Enter exam name:", placeholder="eg: Series1")

# Place the upload button in the first column
uploaded_file = col2.file_uploader("Upload csv file:", type="csv")

if uploaded_file is not None:
    if not exam_name:
        st.warning("Please enter the name of the exam being added...")
    # Read the CSV file
    csv_data = csv.reader(uploaded_file.getvalue().decode('utf-8').splitlines())
    # Skipping college name in the csv file
    next(csv_data)
    # Column names
    columns = next(csv_data)
    columns_with_datatypes = []
    for col in columns:
        if clean(col) == 'AdmnNo':
            columns_with_datatypes.append('AdmnNo TEXT PRIMARY KEY')
        else:
            columns_with_datatypes.append(f'{clean(col)} TEXT')
    # Create the table if it doesn't exist
    table_name = clean(exam_name)
    cur.execute(f'''CREATE TABLE IF NOT EXISTS {table_name} ({', '.join([col for col in columns_with_datatypes])})''')
    # Insert the data into the table
    for row in csv_data:
        # Replace "-" with None in each value of the row
        row = [None if value == "-" else value for value in row]
        try:
            cur.execute(f"INSERT INTO {table_name} VALUES ({', '.join(['?' for _ in row])})", row)
        except sqlite3.IntegrityError:
            st.warning(f"Record with Admission Number {row[0]} already exists in the database.")
            break
    conn.commit()
    st.success(f"CSV data has been uploaded and inserted into the '{table_name}' table.")


st.subheader("", divider="gray")
st.subheader("Generate Report:")


# Fetch all table names that contain exam data
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
exam_tables = cur.fetchall()
exam_names = [table[0] for table in exam_tables if table[0] not in ["Students", "Subjects"]]

# Fetch all distinct classes from the Students table
cur.execute("SELECT DISTINCT Class FROM Students")
class_names = cur.fetchall()


col3, col4 = st.columns([1, 1], gap="medium")

# Create dropdowns for selecting an exam and a class
exam_name = col3.selectbox("Select an exam:", exam_names)
class_name = col4.selectbox("Select a class:", [_class[0] for _class in class_names])

# Generate button
if st.button("Generate", ):
    # Perform analysis based on the selected exam and class
    st.write(f"Analyzing data for exam '{exam_name}' and class '{class_name}'...")

    query = f"""
    SELECT Code FROM Subjects WHERE Class='{class_name}'
    """
    cur.execute(query)
    subjects = cur.fetchall()
    subjects = [subject[0] for subject in subjects]

    results = []
    for subject in subjects:
        result = [subject]
        query = f"""
                SELECT COUNT(*) FROM {exam_name} WHERE {subject} NOT NULL
                """
        cur.execute(query)
        total = list(cur.fetchall())[0][0]
        result.append(total)

        query = f"""
                SELECT COUNT(*) FROM {exam_name} WHERE {subject}>=20 AND {subject} NOT NULL
                """
        cur.execute(query)
        passed = list(cur.fetchall())[0][0]
        result.append(passed)

        results.append(result)

    # # Fetch data from SQLite
    # query = f"""
    # SELECT DISTINCT * FROM {exam_name}, Students
    # WHERE {exam_name}.UniversityRegNo = Students.UniversityRegNo
    # AND Students.Class = '{class_name}'
    # """
    # cur.execute(query)
    # # print(cur.description)
    # results = cur.fetchall()

    # Convert data to DataFrame
    df = pd.DataFrame(results, columns=['Subject', 'Total', 'Passed'])
    df['Pass Percentage'] = (df['Passed'] / df['Total']) * 100

    # Display table
    st.write("Pass Percentage of Each Subject:")
    st.write(df)

    # # Create pie chart
    # fig = px.pie(df, values='Pass Percentage', names='Subject', title='Pass Percentage of Each Subject')
    # st.plotly_chart(fig)


# Close the connection
conn.close()
