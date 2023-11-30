import pandas as pd
import psycopg2
from sqlalchemy import create_engine

# Connection details
DATABASE = 'lytihzus'
USER = 'lytihzus'
PASSWORD = '7fXi38ffXgDuG0koLg7ZfD5FkvwQQHGE'
HOST = 'cornelius.db.elephantsql.com'
PORT = '5432'

# Create the connection string
conn_string = f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"

# Create an engine for the connection
engine = create_engine(conn_string)

# Path to the Excel file
file_path = r"C:\Users\rasmu\Desktop\Config VIRKER\data_i_excel.xlsx"

# Read the Excel file into a DataFrame
df = pd.read_excel(file_path, engine='openpyxl')

# Update the table
# Note: if_exists='replace' will delete the existing data and replace it with the new data.
# Use if_exists='append' to add the new data to the existing data.
df.to_sql('maindata', engine, if_exists='replace', index=False)

print("The table has been updated.")
