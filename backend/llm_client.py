"""
llm_client.py
Single ChatGroq wrapper used by both LLM calls in the pipeline.

LLM Call #1  →  symptom_parser.py  (extract symptoms from free text)
LLM Call #2  →  this file          (generate natural language diagnosis summary)

Usage in main.py:
    from llm_client import llm_client
    summary = llm_client.get_diagnosis_summary(
        symptoms_text, matched_symptoms, predictions
    )
"""

import logging
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.schema import SystemMessage, HumanMessage

from prompt_builder import build_diagnosis_prompt

load_dotenv()
logger = logging.getLogger(__name__)


# ── LLM Client ────────────────────────────────────────────────────────
class LLMClient:

    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise EnvironmentError("GROQ_API_KEY not found. Add it to your .env file.")

        # Single model instance reused for both calls
        self.model = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.0,
            api_key=api_key,
        )
        logger.info("[LLMClient] ChatGroq model initialized")

    # ── LLM Call #2 — Diagnosis Summary ──────────────────────────────
    def get_diagnosis_summary(
        self,
        symptoms_text:    str,
        patient_age:      int,
        patient_gender:   str,
        symptom_duration: str,
        matched_symptoms: list,
        predictions:      list,
    ) -> str:
        """
        Generates a natural language diagnosis summary for the patient.

        Parameters
        ----------
        symptoms_text    : original free-text from the patient
        patient_age      : patient's age in years
        symptom_duration : how long the patient has felt this way
        matched_symptoms : list of matched symptom strings
        predictions      : top-3 dicts from classifier + knowledge base
                           Each has: disease, probability, confidence, info

        Returns
        -------
        str — patient-friendly diagnosis summary (200–300 words)
        """
        prompt = build_diagnosis_prompt(
            symptoms_text=    symptoms_text,
            patient_age=      patient_age,
            patient_gender=   patient_gender,
            symptom_duration= symptom_duration,
            matched_symptoms= matched_symptoms,
            predictions=      predictions,
        )

        system = SystemMessage(content=(
            "You are a compassionate and professional AI medical assistant. "
            "You write clear, empathetic, and responsible medical summaries for patients. "
            "You always remind patients that your analysis is not a substitute for professional medical advice."
        ))
        human = HumanMessage(content=prompt)

        logger.info("[LLMClient] Calling LLM for diagnosis summary...")

        response = self.model.invoke([system, human])
        summary  = response.content.strip()

        logger.info(f"[LLMClient] Summary generated — {len(summary.split())} words")
        return summary


# ── Singleton — imported by main.py ──────────────────────────────────
llm_client = LLMClient()


# ── Test ──────────────────────────────────────────────────────────────
if __name__ == "__main__":

    sample_predictions = [
        {
            "disease":     "pneumonia",
            "probability": 78.4,
            "confidence":  "high",
            "info": {
                "severity_level":            "serious",
                "symptom_category":          "pulmonology",
                "specialist_recommendation": "Pulmonologist",
                "primary_symptoms":          ["fever", "cough", "chest pain"],
                "immediate_advice":          ["Rest", "Stay hydrated", "Avoid cold air"],
                "quick_solutions":           ["Antibiotics", "Chest X-ray"],
                "when_to_seek_help":         "If breathing becomes difficult or fever exceeds 103°F.",
            }
        },
        {
            "disease":     "bronchitis",
            "probability": 12.1,
            "confidence":  "low",
            "info": {
                "severity_level":            "moderate",
                "symptom_category":          "pulmonology",
                "specialist_recommendation": "General Practitioner",
                "primary_symptoms":          ["cough", "mucus", "fatigue"],
                "immediate_advice":          ["Rest", "Drink fluids"],
                "quick_solutions":           ["Cough suppressants", "Steam inhalation"],
                "when_to_seek_help":         "If cough lasts more than 3 weeks.",
            }
        },
        {
            "disease":     "laryngitis",
            "probability": 5.3,
            "confidence":  "low",
            "info": {
                "severity_level":            "mild",
                "symptom_category":          "ENT",
                "specialist_recommendation": "ENT Specialist",
                "primary_symptoms":          ["hoarse voice", "sore throat"],
                "immediate_advice":          ["Rest your voice", "Stay hydrated"],
                "quick_solutions":           ["Voice rest", "Warm fluids"],
                "when_to_seek_help":         "If hoarseness lasts more than 2 weeks.",
            }
        },
    ]

    summary = llm_client.get_diagnosis_summary(
        symptoms_text=    "I have a bad fever, keep coughing, chest hurts when I breathe. Very tired.",
        patient_age=      35,
        patient_gender=   "male",
        symptom_duration= "3 days",
        matched_symptoms= ["fever", "cough", "hurts to breath", "fatigue", "chest tightness"],
        predictions=      sample_predictions,
    )

    print("\n" + "=" * 60)
    print("DIAGNOSIS SUMMARY")
    print("=" * 60)
    print(summary)