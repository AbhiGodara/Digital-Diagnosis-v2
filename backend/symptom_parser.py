import json
import numpy as np
import os
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv
from pathlib import Path
from prompts import get_symptom_extraction_system_prompt, get_symptom_extraction_human_prompt

load_dotenv(override=True)
model_name = os.getenv("LLM_MODEL_NAME", "llama-3.3-70b-versatile")
model = ChatGroq(model=model_name, temperature=0.0)

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

    system_content = get_symptom_extraction_system_prompt(symptoms_formatted)
    system = SystemMessage(content=system_content)

    human_content = get_symptom_extraction_human_prompt(patient_text)
    human = HumanMessage(content=human_content)

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
        print(f"  - {s}")

    print(f"\nBinary vector size  : {len(result['binary_vector'])}")
    print(f"Active symptoms     : {sum(result['binary_vector'])}")
    print(f"Binary vector sample: {result['binary_vector'][:20]}")