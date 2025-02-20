from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy


from google import genai
from langchain.chains import LLMChain
from langchain_community.document_loaders import PyPDFLoader
import os
import logging
import pickle
from dotenv import (
    load_dotenv,
)  # use python-dotenv in your Python script to load the environment variables
import sqlalchemy
from models import db, RevenueData
from revenue_extractor import create_gemini_client, extract_revenue_from_pdf

# load the environment variables from .env file
load_dotenv()


# api keys load from env
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
FLAKS_KEY = os.getenv("FLASK_SECRET_KEY")
DB_URL = os.getenv("DB_URL")

app = Flask(__name__)

# app settings
app.config["UPLOAD_FOLDER"] = "uploads"
app.secret_key = FLAKS_KEY
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# use database URL from .env
app.config["SQLALCHEMY_DATABASE_URI"] = DB_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# configure loggin to catch capture errors and infos
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# gemini implementation
"""response = client.models.generate_content(
    model="gemini-2.0-flash-001", contents="Whats the revenue in 2022"
)"""

# Create a Gemini API client (make sure GEMINI_API_KEY is set in your .env)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
gemini_client = genai.Client(api_key=GEMINI_KEY)
MODEL_ID = "gemini-2.0-flash-001"


# vector Store Setup
vector_store = None

# Load existing vector store if available
if os.path.exists("vector_store.pkl"):
    with open("vector_store.pkl", "rb") as f:
        vector_store = pickle.load(f)


@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for("index"))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    try:
        # Check if a file is present in the request
        if "pdf_file" not in request.files:
            flash("No file part")
            return redirect(url_for("index"))

        file = request.files["pdf_file"]
        if file.filename == "":
            flash("No file selected")
            return redirect(url_for("index"))

        # Save the uploaded file
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(file_path)

        # Extract revenue data from the PDF
        revenue_extraction = extract_revenue_from_pdf(
            file_path, gemini_client, MODEL_ID
        )

        # Insert the extracted data into the database
        new_entry = RevenueData(
            company_name=revenue_extraction.company_name,
            year=revenue_extraction.year,
            revenue=int(revenue_extraction.revenue),  # Convert to integer if necessary
            currency=revenue_extraction.currency,
        )
        db.session.add(new_entry)
        db.session.commit()

        flash(f"Revenue Extraction Result: {revenue_extraction.model_dump_json()}")
        return redirect(url_for("index"))
    except Exception as e:
        logger.error("Error processing PDF: %s", e)
        flash("An error occurred while processing the PDF.")
        return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
