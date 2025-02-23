import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
import io
import os
from dotenv import load_dotenv

load_dotenv()


def extract_revenue_from_pdf(pdf_bytes):
    # Replace with your PDF parsing logic (e.g., using PyPDF2 or pdfplumber)
    return {"revenue": 1000, "details": "Sample extracted revenue data"}


# function to retrieve data from a PostgreSQL database
def get_postgres_data():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="scavenger_task_db",
            user=os.getenv("DB_USERNAME"),
            password=os.getenv("DB_PASSWORD"),
        )
        query = "SELECT * FROM revenue_data;"  # Update with your actual table name and query
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error connecting to database: {e}")
        return pd.DataFrame()


st.title("PDF Revenue Extractor")

# PDF Upload Section
st.header("Upload a PDF File")
uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

if uploaded_file is not None:
    # read the file bytes
    pdf_bytes = uploaded_file.read()

    # extract revenue information from the PDF
    revenue_info = extract_revenue_from_pdf(pdf_bytes)
    st.subheader("Extracted Revenue")
    st.write(revenue_info)

    # option to view the Postgres table
    if st.button("Show Postgres Revenue Table"):
        df = get_postgres_data()
        if not df.empty:
            st.subheader("Revenue Data from Postgres")
            st.dataframe(df)

    # option to display an interactive revenue plot
    if st.button("Show Revenue Plot"):
        df = get_postgres_data()
        if not df.empty:
            st.subheader("Revenue per Company")
            # Create an interactive bar chart using Plotly Express
            fig = px.bar(
                df,
                x="company_name",  # x-axis: company names
                y="revenue",  # y-axis: revenue values
                title="Revenue per Company",
                labels={"company_name": "Company", "revenue": "Revenue"},
                hover_data=[
                    "year",
                    "currency",
                ],  # Optional: show additional info on hover
            )
            st.plotly_chart(fig)
