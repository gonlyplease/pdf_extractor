# dashboard.py
import streamlit as st
import os
import tempfile
import pandas as pd
import logging
from dotenv import load_dotenv

# Import your modules from the Flask app code
from models import RevenueData
from revenue_extractor import extract_revenue_from_pdf
from google import genai

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Load Environment Variables
load_dotenv()
DB_URL = os.getenv("DB_URL")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
MODEL_ID = "gemini-2.0-flash-001"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set Up SQLAlchemy Session
engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Streamlit Frontend Layout
st.title("PDF Revenue Extractor Frontend")

st.header("Upload PDF File")
uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

if uploaded_file is not None:
    # Save the uploaded file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_file_path = tmp_file.name
    st.info("File uploaded. Processing...")

    # Initialize the Gemini API client
    gemini_client = genai.Client(api_key=GEMINI_KEY)

    try:
        # Extract revenue data from the PDF
        revenue_data = extract_revenue_from_pdf(tmp_file_path, gemini_client, MODEL_ID)

        # Insert the extracted data into the database
        new_entry = RevenueData(
            company_name=revenue_data.company_name,
            year=revenue_data.year,
            revenue=int(revenue_data.revenue),  # ensuring it's an integer
            currency=revenue_data.currency,
        )
        session.add(new_entry)
        session.commit()

        st.success("PDF processed and data saved successfully!")
        st.json(revenue_data.model_dump_json())
    except Exception as e:
        logger.error("Error processing PDF: %s", e)
        st.error("An error occurred while processing the PDF.")
    finally:
        # Clean up the temporary file
        os.remove(tmp_file_path)

st.header("Revenue Data Table")
# Retrieve all records from the revenue_data table
entries = session.query(RevenueData).all()

if entries:
    data = []
    for entry in entries:
        data.append(
            {
                "ID": entry.id,
                "Company Name": entry.company_name,
                "Year": entry.year,
                "Revenue": entry.revenue,
                "Currency": entry.currency,
            }
        )
    df = pd.DataFrame(data)
    st.dataframe(df)
else:
    st.write("No revenue data available.")
