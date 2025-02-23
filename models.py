# models.py
from flask_sqlalchemy import SQLAlchemy
from pydantic import BaseModel, Field

db = SQLAlchemy()


# SQLAlchemy Model
class RevenueData(db.Model):
    __tablename__ = "revenue_data"
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.Text, nullable=False)
    year = db.Column(db.Integer, default=2022)
    revenue = db.Column(db.BigInteger, nullable=False)
    currency = db.Column(db.Text, default="EUR")


# Pydantic Model for Structured Extraction
class RevenueExtraction(BaseModel):
    company_name: str = Field(..., description="The name of the company")
    year: int = Field(..., description="The fiscal year (default is 2022)")
    revenue: float = Field(..., description="The revenue amount in full Euros")
    currency: str = Field(..., description="Currency (default is EUR)")
