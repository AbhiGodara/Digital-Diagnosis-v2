import json
import numpy as np
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv
from pathlib import Path
import pickle
import os

load_dotenv(override=True)
model=ChatGroq(model="llama-3.3-70b-versatile", temperature=0.0)

ROOT         = Path(__file__).parent.parent
SYMPTOMS_TXT = ROOT / "data" / "symptom_list_clean.txt"

with open(SYMPTOMS_TXT, "r")  as f:
        SYMPTOMS = [line.strip() for line in f if line.strip()]

def extract_symptoms(patient_text: str) -> list:
    """
    Uses LLM to extract symptoms from patient text.
    Matches directly against the official symptom list.
    Returns a list of matched symptom strings from SYMPTOMS.
    """

    symptoms_formatted = "\n".join(f"- {s}" for s in SYMPTOMS)

    # system = SystemMessage(content=f"""You are a precise medical symptom extraction system.

    #     Your job is to read a patient's description and return ONLY the symptoms that are present, from the official symptom list provided below.

    #     OFFICIAL SYMPTOM LIST:
    #     {symptoms_formatted}

    #     STRICT RULES — follow every rule exactly, no exceptions:
    #     1. ONLY return symptoms from the official list above. Do not invent or add any symptom not in this list.
    #     2. Match symptoms by meaning, not just exact words. If the patient describes something that clearly means the same as a symptom in the list, include that symptom from the list.
    #     - Example: patient says "I feel dizzy" → match "dizziness"
    #     - Example: patient says "my heart is racing" → match "increased heart rate" and "palpitations"
    #     - Example: patient says "I can't sleep" → match "insomnia"
    #     - Example: patient says "tired all the time" → match "fatigue"
    #     3. NEGATION RULE — this is critical: if the patient says they do NOT have a symptom, or uses words like "no", "not", "without", "never", "doesn't", "don't", strictly exclude that symptom.
    #     - Example: "no fever" → do NOT include "fever"
    #     - Example: "I don't have a headache" → do NOT include "headache"
    #     - Example: "no chest pain but I feel dizzy" → include "dizziness", exclude "sharp chest pain"
    #     4. If the patient uses clinical or medical terminology, translate it to 
    #         plain English first, then match against the symptom list.
    #     5. If a symptom is described indirectly, through synonyms, or implied 
    #         by the context — still match it to the closest symptom in the list.
    #         Be generous in matching, not strict.
    #     6. Only include symptoms that are clearly present or strongly implied. Do not guess.
    #     7. Return ONLY a valid JSON array of strings. No explanation, no markdown, no extra text.
    #     8. Each string in the array must exactly match a symptom from the official list word for word.

    #     Output format:
    #     ["symptom one", "symptom two", "symptom three"]""")


    system = SystemMessage(content=f"""You are a precise medical symptom extraction system.

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
        ["symptom one", "symptom two", "symptom three"]""")
    

    human = HumanMessage(content=f"Patient description:\n{patient_text}")

    response = model.invoke([system, human])

    raw = response.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    matched_symptoms = json.loads(raw)

    # Safety filter — keep only symptoms that are actually in our list
    matched_symptoms = [s for s in matched_symptoms if s in SYMPTOMS]

    return matched_symptoms


def to_binary_vector(matched_symptoms: list) -> list:
    """
    Converts matched symptom list to a binary vector of size 84.
    Position of each symptom matches its index in SYMPTOMS list.
    """
    matched_set = set(matched_symptoms)
    return [1 if symptom in matched_set else 0 for symptom in SYMPTOMS]


def parse_symptoms(patient_text: str) -> dict:
    """
    Full pipeline: patient free text → binary vector of size 84.

    Returns:
        binary_vector    → list of 84 ints (0/1), feed into LightGBM
        matched_symptoms → list of matched symptom names from official list
    """
    matched = extract_symptoms(patient_text)
    binary_vector = to_binary_vector(matched)

    return {
        "binary_vector":    binary_vector,   # → directly into model.predict()
        "matched_symptoms": matched,          # → for display/debugging
    }


if __name__ == "__main__":
    test_input = "I have been feeling really anxious, high fever and bad headache. No cough but my throat is sore and I feel very tired. Also feeling dizzy and no appetite."

    result = parse_symptoms(test_input)

    print("Matched Symptoms:")
    for s in result["matched_symptoms"]:
        print(f"  ✓ {s}")

    print(f"\nBinary vector size  : {len(result['binary_vector'])}")
    print(f"Active symptoms     : {sum(result['binary_vector'])}")
    print(f"Binary vector sample: {result['binary_vector'][:20]}")