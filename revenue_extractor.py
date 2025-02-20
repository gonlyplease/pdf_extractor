# revenue_extractor.py
from google import genai
from langchain_community.document_loaders import PyPDFLoader
from models import RevenueExtraction
import logging

logger = logging.getLogger(__name__)


def create_gemini_client(api_key: str):
    """Creates and returns a Gemini API client using the provided API key."""
    return genai.Client(api_key=api_key)


def extract_revenue_from_pdf(
    file_path: str, client, model_id: str = "gemini-2.0-flash-001"
) -> RevenueExtraction:
    """
    Extracts revenue data from a PDF file.

    Loads the PDF, extracts the text, constructs a prompt asking for structured JSON output,
    calls the Gemini API, and returns the parsed RevenueExtraction object.
    """
    # Load PDF and extract text
    pdf_loader = PyPDFLoader(file_path)
    documents = pdf_loader.load()
    full_text = "\n".join(doc.page_content for doc in documents)

    # Construct a prompt with instructions for JSON output matching our schema
    prompt = (
        "Extract the revenue information from the following text in JSON format. "
        "The JSON should match this schema: "
        '{"company_name": string, "year": int, "revenue": float, "currency": string}. '
        "Use full Euro values (not in thousands or millions). "
        "Text: \n" + full_text
    )

    # Call the Gemini API with structured output configuration
    response = client.models.generate_content(
        model=model_id,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": RevenueExtraction.model_json_schema(),  # Provide the JSON schema from the Pydantic model
        },
    )

    try:
        # Parse the JSON response into our Pydantic model
        revenue_data = RevenueExtraction.model_validate_json(response.text)
        return revenue_data
    except Exception as e:
        logger.error("Parsing error: %s", e)
        raise ValueError("Failed to parse revenue extraction response")
