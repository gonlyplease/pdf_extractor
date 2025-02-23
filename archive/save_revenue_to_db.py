import os
import psycopg2
from dotenv import (
    load_dotenv,
)

load_dotenv()


def save_revenue_to_db(company_name, year, revenue_value):
    conn = psycopg2.connect(
        host="localhost",
        database="scavenger_task_db",
        user=os.getenv("DB_USERNAME"),
        password=os.getenv("DB_PASSWORD"),
    )

    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Insert data into the table

    cur.execute(
        "INSERT INTO revenue_data (company_name, year, revenue)"
        "VALUES (%s, %s, %s) RETURNING id;",
        (
            company_name,
            year,
            revenue_value,
        ),
    )

    conn.commit()
    cur.close()
    conn.close()
    print(f"Umsatz gespeichert: {company_name} - {year} - {revenue_value} EUR")
