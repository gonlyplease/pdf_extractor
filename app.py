# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import (
    secure_filename,
)  # Changed: Import secure_filename for safer file names

from google import genai
import os
import logging
from dotenv import load_dotenv
from models import db, RevenueData
from revenue_extractor import extract_revenue_from_pdf


# Changed: Removed unused import: PyPDFLoader from langchain_community.document_loaders

# Load the environment variables from .env file
load_dotenv()

# API keys loaded from env
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
FLASK_KEY = os.getenv("FLASK_SECRET_KEY")
DB_URL = os.getenv("DB_URL")

app = Flask(__name__)


# App settings
app.config["UPLOAD_FOLDER"] = "uploads"
app.secret_key = FLASK_KEY
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Use database URL from .env
app.config["SQLALCHEMY_DATABASE_URI"] = DB_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# Configure logging to capture errors and info
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a Gemini API client (make sure GEMINI_API_KEY is set in your .env)
gemini_client = genai.Client(api_key=GEMINI_KEY)
MODEL_ID = "gemini-2.0-flash-001"


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

        # Changed: Use secure_filename to prevent directory traversal issues
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(file_path)

        # Extract the JSON revenue data from the PDF
        revenue_extraction = extract_revenue_from_pdf(
            file_path, gemini_client, MODEL_ID
        )

        # Insert data into the database
        new_entry = RevenueData(
            company_name=revenue_extraction.company_name,
            year=revenue_extraction.year,
            revenue=int(revenue_extraction.revenue),  # convert to integer if necessary
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
