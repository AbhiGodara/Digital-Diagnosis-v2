"""
prompts.py
Centralized repository for all LLM prompts used in the Digital Diagnosis system.

Contains prompts for:
1. Symptom parsing from patient free-text descriptions.
2. Generating a natural language diagnosis summary based on predictions.
"""

# ── Symptom Parsing Prompts ───────────────────────────────────────────

def get_symptom_extraction_system_prompt(symptoms_formatted: str) -> str:
    """Returns the system prompt for symptom extraction."""
    return f"""You are a precise medical symptom extraction system.

Your task is to extract ONLY symptoms that are clearly present in the patient description, and ONLY if they appear in the official symptom list provided.

OFFICIAL SYMPTOM LIST:
{symptoms_formatted}

STRICT EXTRACTION RULES — follow exactly:

1. Only return symptoms from the official list. Never invent or modify symptoms.
2. Identify explicit symptom expressions in the patient's text.
3. Remove any symptom that appears in a negated context.

NEGATION HANDLING (CRITICAL):
Exclude symptoms if negated by words such as:
no, not, never, without, denies, ruled out, negative for,
"but not", "except", "other than", "no longer", or past resolved symptoms.

If unsure whether a symptom is negated, EXCLUDE it.

4. Semantic matching is allowed ONLY when:
- The meaning is clearly equivalent.
- The mapping is medically reasonable.
- The symptom is directly expressed, not inferred.

5. Do NOT infer symptoms from vague descriptions.
Example: "I feel bad" → do not map to fatigue.

6. If multiple official symptoms match, choose the most specific one.

7. Do not include duplicates.

8. If no symptoms are confidently identified, return an empty JSON array [].

Reasoning steps (internal only):
- Identify symptom phrases
- Remove negated ones
- Map to closest official symptom
- Remove uncertain matches
- Output final JSON

Return ONLY a valid JSON array of strings.
No explanation. No markdown.
Each string must exactly match a symptom from the official list.

Output format:
["symptom one", "symptom two", "symptom three"]"""

def get_symptom_extraction_human_prompt(patient_text: str) -> str:
    """Returns the human prompt for symptom extraction."""
    return f"Patient description:\n{patient_text}"


# ── Diagnosis Summary Prompts ─────────────────────────────────────────

DIAGNOSIS_SUMMARY_SYSTEM_PROMPT = (
    "You are a compassionate and professional AI medical assistant. "
    "You write clear, empathetic, and responsible medical summaries for patients. "
    "You always remind patients that your analysis is not a substitute for professional medical advice."
)

def build_diagnosis_prompt(
    symptoms_text:    str,
    patient_age:      int,
    patient_gender:   str,
    symptom_duration: str,
    matched_symptoms: list[str],
    predictions:      list[dict],
) -> str:
    """
    Builds the full prompt for LLM Call #2 (Diagnosis Summary).

    Parameters
    ----------
    symptoms_text    : original free-text input from the patient
    patient_age      : patient's age in years
    symptom_duration : how long the patient has felt this way
    matched_symptoms : list of matched symptom strings from symptom_parser
    predictions      : list of top-3 dicts from classifier + knowledge_base
                       Each dict has: disease, probability, confidence, info

    Returns
    -------
    str — the complete prompt to send to the LLM
    """

    # Format matched symptoms
    symptoms_block = "\n".join(f"  - {s}" for s in matched_symptoms) \
                     if matched_symptoms else "  - None detected"

    # Format each prediction
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

    # Final Prompt
    return f"""You are a compassionate and professional AI medical assistant.

A patient has described their symptoms and our diagnostic system has analyzed them.
Your job is to write a clear, helpful, and empathetic diagnosis summary for the patient.

---

PATIENT'S DESCRIPTION:
"{symptoms_text}"

PATIENT PROFILE:
  - Age: {patient_age} years old
  - Gender: {patient_gender}
  - Symptom Duration: {symptom_duration}
  
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
