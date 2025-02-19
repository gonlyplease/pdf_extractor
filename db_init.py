import os
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="flask_db",
    user=os.environ["DB_USERNAME"],
    password=os.environ["DB_PASSWORD"],
)

# Open a cursor to perform database operations
cur = conn.cursor()

# Execute a command: this creates a new table
cur.execute("DROP TABLE IF EXISTS books;")
cur.execute(
    "CREATE TABLE revenue_data("
    "id SERIAL PRIMARY KEY,"
    "company_name TEXT NOT NULL,"
    "year INT NOT NULL,"
    "revenue BIGINT NOT NULL,"
    "currency TEXT DEFAULT 'EUR');"
)

# Insert data into the table

cur.execute(
    "INSERT INTO books (title, author, pages_num, review)" "VALUES (%s, %s, %s, %s)",
    ("A Tale of Two Cities", "Charles Dickens", 489, "A great classic!"),
)


conn.commit()

cur.close()
conn.close()
