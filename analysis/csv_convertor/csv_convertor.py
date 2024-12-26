import pandas as pd
import mysql.connector
import os
from dotenv import load_dotenv
from pathlib import Path

base_path = Path(__file__).resolve().parent.parent.parent
env_path = base_path / 'env_files' / 'special_detail.env'
load_dotenv(dotenv_path=env_path)

db_config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
    }

conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

cursor.execute("SHOW TABLES")
tables = cursor.fetchall()
table_names = tables[:13]

for table in table_names:

    df = pd.read_sql_query(f"SELECT * FROM {table[0]}", con=conn)
    print(table[0])
    df.to_csv(f"{table[0]}_data.csv", index=False)