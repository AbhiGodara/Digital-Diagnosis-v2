"""
prompt_builder.py
Assembles the prompt for LLM Call #2.

LLM Call #1 (symptom_parser.py) → extracts symptoms from free text
LLM Call #2 (this file builds the prompt) → generates a natural language
    diagnosis summary for the patient based on:
        - their original symptom description
        - matched symptoms
        - top-3 model predictions + probabilities
        - knowledge base info (advice, severity, specialist)

Used by llm_client.py:
    from prompt_builder import build_diagnosis_prompt
    prompt = build_diagnosis_prompt(data)
    summary = llm_client.get_summary(prompt)
"""


def build_diagnosis_prompt(
    symptoms_text:    str,
    matched_symptoms: list[str],
    predictions:      list[dict],
) -> str:
    """
    Builds the full prompt for LLM Call #2.

    Parameters
    ----------
    symptoms_text    : original free-text input from the patient
    matched_symptoms : list of matched symptom strings from symptom_parser
    predictions      : list of top-3 dicts from classifier + knowledge_base
                       Each dict has: disease, probability, confidence, info

    Returns
    -------
    str — the complete prompt to send to the LLM
    """

    # ── Format matched symptoms ───────────────────────────────────────
    symptoms_block = "\n".join(f"  - {s}" for s in matched_symptoms) \
                     if matched_symptoms else "  - None detected"

    # ── Format each prediction ────────────────────────────────────────
    predictions_block = ""
    for i, pred in enumerate(predictions, 1):
        info = pred.get("info", {})
        predictions_block += f"""
Prediction #{i} — {pred['disease'].title()}
  Probability       : {pred['probability']}%
  Confidence        : {pred['confidence']}
  Severity          : {info.get('severity_level', 'unknown')}
  Category          : {info.get('symptom_category', 'general')}
  Specialist        : {info.get('specialist_recommendation', 'General Practitioner')}
  Primary Symptoms  : {', '.join(info.get('primary_symptoms', []))}
  Immediate Advice  : {' | '.join(info.get('immediate_advice', []))}
  Quick Solutions   : {' | '.join(info.get('quick_solutions', []))}
  When to Seek Help : {info.get('when_to_seek_help', 'If symptoms worsen, consult a doctor.')}
"""

    # ── Final Prompt ──────────────────────────────────────────────────
    prompt = f"""You are a compassionate and professional AI medical assistant.

A patient has described their symptoms and our diagnostic system has analyzed them.
Your job is to write a clear, helpful, and empathetic diagnosis summary for the patient.

---

PATIENT'S DESCRIPTION:
"{symptoms_text}"

SYMPTOMS IDENTIFIED:
{symptoms_block}

TOP 3 DIAGNOSTIC PREDICTIONS:
{predictions_block}

---

INSTRUCTIONS — follow every point carefully:

1. Write in simple, clear language that a non-medical person can understand. Avoid heavy jargon.
2. Start by acknowledging the patient's symptoms briefly and empathetically.
3. Explain the most likely diagnosis (Prediction #1) clearly — what it is, why their symptoms point to it.
4. Mention Prediction #2 and #3 briefly as other possibilities worth discussing with a doctor.
5. Give 2-3 practical immediate steps the patient can take right now.
6. Clearly state which specialist they should see and when.
7. ALWAYS end with a disclaimer that this is an AI-generated analysis and NOT a substitute for professional medical diagnosis.
8. Do NOT be alarming or cause unnecessary panic. Be calm, factual and reassuring.
9. Do NOT make definitive claims like "you have X disease". Use language like "suggests", "may indicate", "could be".
10. Keep the response between 200–300 words. Do not write more than 300 words.

Write the summary now:"""

    return prompt


# ── Test ──────────────────────────────────────────────────────────────
if __name__ == "__main__":

    # Sample data to test the prompt output
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
                "quick_solutions":           ["Antibiotics", "Chest X-ray", "Supportive care"],
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

    prompt = build_diagnosis_prompt(
        symptoms_text="I have a bad fever, keep coughing, and my chest hurts when I breathe. Feeling very tired.",
        matched_symptoms=["fever", "cough", "hurts to breath", "fatigue", "chest tightness"],
        predictions=sample_predictions,
    )

    print(prompt)