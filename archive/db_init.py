import os
import psycopg2
from dotenv import (
    load_dotenv,
)

load_dotenv()


conn = psycopg2.connect(
    host="localhost",
    database="scavenger_task_db",
    user=os.getenv("DB_USERNAME"),
    password=os.getenv("DB_PASSWORD"),
)

# Open a cursor to perform database operations
cur = conn.cursor()

cur.execute("SELECT current_user;")
print("Connected as:", cur.fetchone()[0])

# Execute a command: this creates a new table
cur.execute("DROP TABLE IF EXISTS books;")
cur.execute(
    "CREATE TABLE IF NOT EXISTS revenue_data("
    "id SERIAL PRIMARY KEY,"
    "company_name TEXT NOT NULL,"
    "year INT NOT NULL,"
    "revenue BIGINT NOT NULL,"
    "currency TEXT DEFAULT 'EUR');"
)

# Insert data into the table

cur.execute(
    "INSERT INTO revenue_data (company_name, year, revenue)"
    "VALUES (%s, %s, %s) RETURNING id;",
    (
        "Apple",
        2022,
        123456789,
    ),
)

inserted_id = cur.fetchone()[0]
print("Inserted row with id:", inserted_id)


conn.commit()

cur.close()
conn.close()
