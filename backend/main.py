"""
main.py
FastAPI entry point for the Digital Diagnosis 2.0 backend.

Run from project root:
    uvicorn backend.main:app --reload --port 8000

Endpoints:
    POST /api/diagnose      — main diagnosis pipeline
    GET  /api/health        — health check
    GET  /api/diseases      — list all diseases the model knows
    GET  /api/symptoms      — list all 377 symptoms
"""

import logging
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from classifier import classifier
from symptom_parser import parse_symptoms
from knowledge_base import get_disease_info

# ── Logging ───────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s"
)
logger = logging.getLogger(__name__)


# ── Lifespan — load model once at startup ────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Loading classifier...")
    classifier.load()
    logger.info(f"Classifier ready — {classifier.num_diseases} diseases | {classifier.num_symptoms} symptoms")
    yield
    logger.info("Shutting down...")


# ── App ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="Digital Diagnosis 2.0",
    description="LightGBM + LLM disease prediction from free-text symptoms",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # tighten this in production
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Schemas ───────────────────────────────────────────────────────────
class DiagnoseRequest(BaseModel):
    symptoms_text: str          # free text from the user

class PredictionItem(BaseModel):
    disease:     str
    probability: float          # 0–100
    confidence:  str            # "high" | "medium" | "low"
    info:        dict           # from knowledge_base

class DiagnoseResponse(BaseModel):
    success:            bool
    predictions:        list[PredictionItem]
    matched_symptoms:   list[str]
    active_symptom_count: int
    processing_time_ms: float
    timestamp:          str


# ── Routes ────────────────────────────────────────────────────────────

@app.post("/api/diagnose", response_model=DiagnoseResponse)
async def diagnose(request: DiagnoseRequest):
    """
    Full pipeline:
        1. Parse free text → matched symptoms + binary vector  (LLM)
        2. Binary vector → top-3 disease predictions           (LightGBM)
        3. Enrich each prediction with disease info            (knowledge base)
    """
    if not request.symptoms_text.strip():
        raise HTTPException(status_code=400, detail="symptoms_text cannot be empty")

    if len(request.symptoms_text.strip()) < 10:
        raise HTTPException(status_code=400, detail="Please describe your symptoms in more detail")

    start = datetime.now()

    try:
        # Step 1 — symptom parser
        logger.info(f"Parsing symptoms — input length: {len(request.symptoms_text)} chars")
        parsed = parse_symptoms(request.symptoms_text)
        binary_vector    = parsed["binary_vector"]
        matched_symptoms = parsed["matched_symptoms"]
        logger.info(f"Matched {len(matched_symptoms)} symptoms")

        if sum(binary_vector) == 0:
            raise HTTPException(
                status_code=422,
                detail="Could not match any symptoms from your description. Please be more specific."
            )

        # Step 2 — classifier
        raw_predictions = classifier.predict(binary_vector, top_k=3)
        logger.info(f"Top prediction: {raw_predictions[0]['disease']} ({raw_predictions[0]['probability']}%)")

        # Step 3 — enrich with knowledge base
        predictions = []
        for pred in raw_predictions:
            predictions.append(PredictionItem(
                disease=     pred["disease"],
                probability= pred["probability"],
                confidence=  pred["confidence"],
                info=        get_disease_info(pred["disease"]),
            ))

        processing_ms = round((datetime.now() - start).total_seconds() * 1000, 2)

        return DiagnoseResponse(
            success=              True,
            predictions=          predictions,
            matched_symptoms=     matched_symptoms,
            active_symptom_count= sum(binary_vector),
            processing_time_ms=   processing_ms,
            timestamp=            datetime.now().isoformat(),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Diagnosis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.get("/api/health")
async def health():
    """Returns system status and model info."""
    return {
        "status":        "healthy" if classifier._loaded else "model_not_loaded",
        "num_diseases":  classifier.num_diseases,
        "num_symptoms":  classifier.num_symptoms,
        "version":       "2.0.0",
        "timestamp":     datetime.now().isoformat(),
    }


@app.get("/api/diseases")
async def get_diseases():
    """Returns the full list of diseases the model can predict."""
    return {
        "total":    classifier.num_diseases,
        "diseases": classifier.diseases,
    }


@app.get("/api/symptoms")
async def get_symptoms():
    """Returns the full list of 377 symptoms used as model features."""
    return {
        "total":    classifier.num_symptoms,
        "symptoms": classifier.symptom_list,
    }


# ── Run ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)