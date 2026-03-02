import json
import numpy as np
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv
from pathlib import Path
import pickle
import os

load_dotenv(override=True)
os.environ["GROQ_API_KEY"]=os.getenv("GROQ_API_KEY")
model=ChatGroq(model="llama-3.3-70b-versatile", temperature=0.0)

ROOT         = Path(__file__).parent.parent
SYMPTOMS_TXT = ROOT / "data" / "symptoms_list.txt"

with open(SYMPTOMS_TXT, "r")  as f:
        SYMPTOMS = [line.strip() for line in f if line.strip()]

def extract_symptoms(patient_text: str) -> list:
    """
    Uses LLM to extract symptoms from patient text.
    Matches directly against the official symptom list.
    Returns a list of matched symptom strings from SYMPTOMS.
    """

    symptoms_formatted = "\n".join(f"- {s}" for s in SYMPTOMS)

    system = SystemMessage(content=f"""You are a precise medical symptom extraction system.

        Your job is to read a patient's description and return ONLY the symptoms that are present, from the official symptom list provided below.

        OFFICIAL SYMPTOM LIST:
        {symptoms_formatted}

        STRICT RULES — follow every rule exactly, no exceptions:
        1. ONLY return symptoms from the official list above. Do not invent or add any symptom not in this list.
        2. Match symptoms by meaning, not just exact words. If the patient describes something that clearly means the same as a symptom in the list, include that symptom from the list.
        - Example: patient says "I feel dizzy" → match "dizziness"
        - Example: patient says "my heart is racing" → match "increased heart rate" and "palpitations"
        - Example: patient says "I can't sleep" → match "insomnia"
        - Example: patient says "tired all the time" → match "fatigue"
        3. NEGATION RULE — this is critical: if the patient says they do NOT have a symptom, or uses words like "no", "not", "without", "never", "doesn't", "don't", strictly exclude that symptom.
        - Example: "no fever" → do NOT include "fever"
        - Example: "I don't have a headache" → do NOT include "headache"
        - Example: "no chest pain but I feel dizzy" → include "dizziness", exclude "sharp chest pain"
        4. Only include symptoms that are clearly present or strongly implied. Do not guess.
        5. Return ONLY a valid JSON array of strings. No explanation, no markdown, no extra text.
        6. Each string in the array must exactly match a symptom from the official list word for word.

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
    Converts matched symptom list to a binary vector of size 377.
    Position of each symptom matches its index in SYMPTOMS list.
    """
    matched_set = set(matched_symptoms)
    return [1 if symptom in matched_set else 0 for symptom in SYMPTOMS]


def parse_symptoms(patient_text: str) -> dict:
    """
    Full pipeline: patient free text → binary vector of size 377.

    Returns:
        binary_vector    → list of 377 ints (0/1), feed into LightGBM
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