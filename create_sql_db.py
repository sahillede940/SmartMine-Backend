import sqlite3
import pandas as pd

# Parameters
csv_file_path = 'crop_production.csv'  # Path to your CSV file
db_name = 'crop_production.db'     # Name of the SQLite database
table_name = 'crop_production'   # Name of the table to insert data into

# Load CSV into DataFrame
df = pd.read_csv(csv_file_path)

# Connect to SQLite database (creates it if it doesn't exist)
conn = sqlite3.connect(db_name)
cursor = conn.cursor()

# Dynamically create a table with column names and types based on the DataFrame
columns = ', '.join([f"{col} TEXT" for col in df.columns])
cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})")

# Insert data into the table
df.to_sql(table_name, conn, if_exists='append', index=False)

# Commit and close
conn.commit()
conn.close()

print(f"Data from {csv_file_path} successfully inserted into {table_name} table in {db_name}.")

# print top 20 rows
conn = sqlite3.connect(db_name)
cursor = conn.cursor()
cursor.execute(f"SELECT * FROM {table_name} LIMIT 20")
rows = cursor.fetchall()

for row in rows:
    print(row)
    
conn.close()
