import os
import logging
import requests  # CHANGED: Added requests import to send HTTP requests

import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
from dotenv import load_dotenv

# CHANGED: Removed unused imports (tempfile, genai, extract_revenue_from_pdf)

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# CHANGED: Define the Flask upload URL via an environment variable or default to localhost
FLASK_UPLOAD_URL = os.getenv("FLASK_UPLOAD_URL", "http://localhost:5000/upload")


def get_postgres_data():
    try:
        # CHANGED: Using context manager for the connection to improve resource management
        with psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            database=os.getenv("DB_NAME", "scavenger_task_db"),
            user=os.getenv("DB_USERNAME"),
            password=os.getenv("DB_PASSWORD"),
        ) as conn:
            query = "SELECT * FROM revenue_data;"
            df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        st.error(f"Error connecting to database: {e}")
        return pd.DataFrame()


st.title("PDF Revenue Extractor Dashboard")

with st.form("upload_form"):
    st.header("Upload a PDF File to Flask App")
    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])
    submit = st.form_submit_button("Upload to Flask")

if submit:
    if not uploaded_file:
        st.error("Please upload a PDF file.")
    else:
        try:
            # CHANGED: Prepare the file upload payload for the Flask endpoint.
            # uploaded_file is a BytesIO object so we use getvalue() to get its content.
            files = {
                "pdf_file": (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    "application/pdf",
                )
            }
            response = requests.post(FLASK_UPLOAD_URL, files=files)
            # CHANGED: Check for success status codes (200 or redirect 302)
            if response.status_code in [200, 302]:
                st.success("File uploaded successfully to the Flask app!")
                st.write("Response from Flask app:")
                st.write(response.text)
            else:
                st.error(f"Upload failed with status code {response.status_code}")
        except Exception as e:
            st.error(f"Error uploading file to Flask app: {e}")

st.header("Current Revenue Data")
df = get_postgres_data()
if not df.empty:
    st.subheader("Revenue Data from Postgres")
    st.dataframe(df)

    st.subheader("Revenue Data per Company")
    try:
        fig = px.bar(
            df,
            x="company_name",
            y="revenue",
            title="Revenue per Company",
            labels={"company_name": "Company", "revenue": "Revenue"},
            hover_data=["year", "currency"],
        )
        st.plotly_chart(fig)
    except Exception as e:
        st.error(f"Error generating plot: {e}")
else:
    st.info("No revenue data found in the database.")
