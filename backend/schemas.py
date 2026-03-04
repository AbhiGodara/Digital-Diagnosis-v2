"""
schemas.py
All Pydantic request and response models for the FastAPI backend.
Imported by main.py for request validation and response serialization.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Literal
from datetime import datetime


# ── Request Schemas ───────────────────────────────────────────────────

class DiagnoseRequest(BaseModel):
    """
    Sent by the frontend to POST /api/diagnose
    """
    symptoms_text: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="Free-text description of symptoms from the patient",
        examples=["I have a bad headache, high fever, and I keep coughing. Feeling very tired."]
    )

    @field_validator("symptoms_text")
    @classmethod
    def strip_and_check(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("symptoms_text cannot be empty or whitespace")
        return v


# ── Sub-schemas used inside responses ────────────────────────────────

class DiseaseInfo(BaseModel):
    """Medical info pulled from knowledge base for each predicted disease."""
    symptom_category:          str
    primary_symptoms:          list[str]
    immediate_advice:          list[str]
    quick_solutions:           list[str]
    when_to_seek_help:         str
    severity_level:            Literal["mild", "moderate", "serious", "critical"]
    specialist_recommendation: str


class PredictionItem(BaseModel):
    """One disease prediction with probability, confidence and enriched info."""
    rank:        int                              # 1, 2, 3
    disease:     str
    probability: float = Field(ge=0.0, le=100.0) # percentage 0–100
    confidence:  Literal["high", "medium", "low"]
    info:        DiseaseInfo


# ── Response Schemas ──────────────────────────────────────────────────

class DiagnoseResponse(BaseModel):
    """
    Returned by POST /api/diagnose
    """
    success:              bool
    predictions:          list[PredictionItem]   # always top-3
    matched_symptoms:     list[str]              # symptoms the LLM found
    active_symptom_count: int                    # number of 1s in binary vector
    processing_time_ms:   float
    timestamp:            str


class HealthResponse(BaseModel):
    """
    Returned by GET /api/health
    """
    status:        Literal["healthy", "model_not_loaded"]
    num_diseases:  int
    num_symptoms:  int
    version:       str
    timestamp:     str


class DiseasesResponse(BaseModel):
    """
    Returned by GET /api/diseases
    """
    total:    int
    diseases: list[str]


class SymptomsResponse(BaseModel):
    """
    Returned by GET /api/symptoms
    """
    total:    int
    symptoms: list[str]


class ErrorResponse(BaseModel):
    """
    Returned on any error (400, 422, 500)
    """
    success: bool = False
    detail:  str