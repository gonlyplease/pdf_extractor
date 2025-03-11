# PDF Extractor

## Overview
This project is a PDF extractor that retrieves revenue information from an annual report for a specific year (e.g., 2022). It processes PDF documents to extract structured revenue data which can then be saved into a PostgreSQL database.

## File Structure
- **app.py**  
  The main Flask application file that sets up the web server, handles file uploads, and integrates with the revenue extraction logic.

- **dashboard.py**  
  A Streamlit-based dashboard providing a modern, interactive frontend. It allows users to upload PDF files, processes them using the revenue extraction logic (via the Gemini API), saves the extracted data into the database, and displays the revenue data in an interactive table.

- **models.py**  
  Contains the SQLAlchemy model for the `RevenueData` table as well as the Pydantic model (`RevenueExtraction`) for structured data extraction.

- **revenue_extractor.py**  
  Implements the function `extract_revenue_from_pdf` which loads a PDF, extracts its content, calls the Gemini API to extract revenue data in a structured JSON format, and returns the parsed data.

## Installation


## Notes
Large Language Models (LLMs) were used during development for debugging purposes and to assist in creating the frontend.

## Sources
I was inspired by this post to use pydantic and gemini 2.0 for this task: https://www.philschmid.de/gemini-pdf-to-data

```bash
git clone <repo-url>
cd <repo-name>
pip install -r requirements.txt


