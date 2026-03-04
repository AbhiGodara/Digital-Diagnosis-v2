"""
classifier.py
Loads the trained LightGBM model and label encoder at startup.
Called by main.py to get top-3 disease predictions from a binary symptom vector.
"""

import pickle
import numpy as np
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────
BASE_DIR      = Path(__file__).parent.parent
MODEL_PATH    = BASE_DIR / "models" / "lightgbm_model.pkl"
ENCODER_PATH  = BASE_DIR / "models" / "label_encoder.pkl"
SYMPTOMS_PATH = BASE_DIR / "data"   / "symptoms_list.txt"


class Classifier:

    def __init__(self):
        self.model         = None
        self.label_encoder = None
        self.symptom_list  = []
        self._loaded       = False

    # ── Load ──────────────────────────────────────────────────────────
    def load(self):
        """Load model, label encoder and symptom list from disk."""

        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"Model not found at: {MODEL_PATH}")
        if not ENCODER_PATH.exists():
            raise FileNotFoundError(f"Label encoder not found at: {ENCODER_PATH}")
        if not SYMPTOMS_PATH.exists():
            raise FileNotFoundError(f"Symptom list not found at: {SYMPTOMS_PATH}")

        with open(MODEL_PATH,   "rb") as f:
            self.model = pickle.load(f)

        with open(ENCODER_PATH, "rb") as f:
            self.label_encoder = pickle.load(f)

        with open(SYMPTOMS_PATH, "r") as f:
            self.symptom_list = [line.strip() for line in f if line.strip()]

        self._loaded = True
        print(f"[Classifier] Loaded — {len(self.label_encoder.classes_)} diseases | {len(self.symptom_list)} symptoms")

    # ── Predict ───────────────────────────────────────────────────────
    def predict(self, binary_vector: list, top_k: int = 3) -> list:
        """
        Takes a binary vector of size 377 and returns top-k predictions.

        Parameters
        ----------
        binary_vector : list of 0/1 ints — must match order of symptom_list
        top_k         : number of top predictions to return (default 3)

        Returns
        -------
        list of dicts:
            [
                { "disease": "pneumonia",  "probability": 84.21, "confidence": "high"   },
                { "disease": "bronchitis", "probability": 9.43,  "confidence": "medium" },
                { "disease": "laryngitis", "probability": 3.12,  "confidence": "low"    },
            ]
        """
        if not self._loaded:
            raise RuntimeError("Classifier not loaded. Call classifier.load() first.")

        if len(binary_vector) != len(self.symptom_list):
            raise ValueError(
                f"Vector size mismatch: got {len(binary_vector)}, expected {len(self.symptom_list)}"
            )

        x     = np.array(binary_vector, dtype=np.float32).reshape(1, -1)
        probs = self.model.predict_proba(x)[0]

        top_indices = np.argsort(probs)[::-1][:top_k]

        predictions = []
        for idx in top_indices:
            probability = round(float(probs[idx]) * 100, 2)
            predictions.append({
                "disease":     self.label_encoder.inverse_transform([idx])[0],
                "probability": probability,
                "confidence":  self._confidence_label(probability),
            })

        return predictions

    # ── Helpers ───────────────────────────────────────────────────────
    def _confidence_label(self, probability: float) -> str:
        if probability >= 60:
            return "high"
        elif probability >= 30:
            return "medium"
        else:
            return "low"

    @property
    def diseases(self) -> list:
        """All disease names the model knows."""
        return self.label_encoder.classes_.tolist() if self._loaded else []

    @property
    def num_symptoms(self) -> int:
        return len(self.symptom_list)

    @property
    def num_diseases(self) -> int:
        return len(self.label_encoder.classes_) if self._loaded else 0


# Singleton — imported and used by main.py
classifier = Classifier()