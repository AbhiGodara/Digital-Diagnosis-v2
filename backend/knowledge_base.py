"""
knowledge_base.py
Loads data/disease_knowledge.json at startup and provides disease info
for the top-3 predictions returned by the classifier.

Used by main.py:
    from knowledge_base import get_disease_info
    info = get_disease_info("pneumonia")
"""

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# ── Path ──────────────────────────────────────────────────────────────
BASE_DIR     = Path(__file__).parent.parent
ADVICE_PATH  = BASE_DIR / "data" / "disease_knowledge.json"

# ── Default fallback returned when disease is not in JSON ─────────────
DEFAULT_INFO = {
    "symptom_category":        "general",
    "primary_symptoms":        [],
    "immediate_advice":        ["Monitor your symptoms carefully.", "Rest and stay hydrated."],
    "quick_solutions":         ["Consult a healthcare provider for proper diagnosis."],
    "when_to_seek_help":       "If symptoms persist or worsen, consult a doctor.",
    "severity_level":          "moderate",
    "specialist_recommendation": "General Practitioner",
}


# ── KnowledgeBase class ───────────────────────────────────────────────
class KnowledgeBase:

    def __init__(self):
        self._data: dict = {}
        self._loaded: bool = False

    def load(self):
        """Load disease_knowledge.json from disk. Called once at startup."""
        if not ADVICE_PATH.exists():
            logger.warning(f"disease_knowledge.json not found at {ADVICE_PATH}. Falling back to defaults.")
            self._loaded = True
            return

        with open(ADVICE_PATH, "r", encoding="utf-8") as f:
            raw = json.load(f)

        # Normalise all keys to lowercase for case-insensitive lookup
        self._data = {k.lower().strip(): v for k, v in raw.items()}
        self._loaded = True
        logger.info(f"[KnowledgeBase] Loaded — {len(self._data)} diseases")

    def get(self, disease_name: str) -> dict:
        """
        Returns the medical_advice dict for a disease.
        Falls back gracefully if disease is not found.

        Parameters
        ----------
        disease_name : str — e.g. "pneumonia", "Pneumonia", "PNEUMONIA"

        Returns
        -------
        dict with keys:
            symptom_category, primary_symptoms, immediate_advice,
            quick_solutions, when_to_seek_help, severity_level,
            specialist_recommendation
        """
        if not self._loaded:
            self.load()

        key = disease_name.lower().strip()

        # 1. Exact match
        if key in self._data:
            return self._extract_advice(self._data[key])

        # 2. Partial match — disease name contains key or vice versa
        for stored_key, value in self._data.items():
            if key in stored_key or stored_key in key:
                logger.debug(f"Partial match: '{key}' → '{stored_key}'")
                return self._extract_advice(value)

        # 3. Not found — return default
        logger.warning(f"No knowledge base entry for: '{disease_name}' — using defaults")
        return {**DEFAULT_INFO, "disease_name": disease_name}

    def _extract_advice(self, entry: dict) -> dict:
        """Pull the advice block out of the raw entry."""
        advice = entry
        return {
            "symptom_category":          advice.get("symptom_category",          DEFAULT_INFO["symptom_category"]),
            "primary_symptoms":          advice.get("primary_symptoms",          DEFAULT_INFO["primary_symptoms"]),
            "immediate_advice":          advice.get("immediate_advice",          DEFAULT_INFO["immediate_advice"]),
            "quick_solutions":           advice.get("quick_solutions",           DEFAULT_INFO["quick_solutions"]),
            "when_to_seek_help":         advice.get("when_to_seek_help",         DEFAULT_INFO["when_to_seek_help"]),
            "severity_level":            advice.get("severity_level",            DEFAULT_INFO["severity_level"]),
            "specialist_recommendation": advice.get("specialist_recommendation", DEFAULT_INFO["specialist_recommendation"]),
        }

    @property
    def all_diseases(self) -> list:
        return list(self._data.keys())

    @property
    def total(self) -> int:
        return len(self._data)


# ── Singleton + convenience function used by main.py ─────────────────
knowledge_base = KnowledgeBase()
knowledge_base.load()


def get_disease_info(disease_name: str) -> dict:
    """Convenience wrapper — import and call this directly in main.py."""
    return knowledge_base.get(disease_name)