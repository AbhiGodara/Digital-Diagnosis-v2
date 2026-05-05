import sys
from pathlib import Path

# Add root directory and backend directory to path
ROOT = Path(__file__).parent.parent
sys.path.append(str(ROOT))
sys.path.append(str(ROOT / "backend"))

from langchain_core.tools import tool
from backend.classifier import classifier
from backend.knowledge_base import get_disease_info
from backend.symptom_parser import SYMPTOMS, to_binary_vector

# Ensure classifier is loaded before using it
if not classifier._loaded:
    classifier.load()

@tool
def get_diagnosis(extracted_symptoms: list[str]) -> str:
    """
    Use this tool when you have extracted a list of symptoms from the user's input and want to predict the diseases.
    This tool takes a list of symptoms exactly matching the allowed list of 84 symptoms.
    It returns the top 3 predicted diseases along with their medical information from the knowledge base.
    
    Args:
        extracted_symptoms (list[str]): A list of exact symptom strings (e.g. ["headache", "fever"]).
        
    Returns:
        str: A JSON string containing the diagnosis results.
    """
    # Filter symptoms to ensure they are in our official list
    valid_symptoms = [s for s in extracted_symptoms if s in SYMPTOMS]
    
    if not valid_symptoms:
        return "Error: None of the provided symptoms match the official list of 84 symptoms. Please clarify with the user and try again."
        
    # Convert the matched symptoms to the 84-dimensional binary vector
    binary_vector = to_binary_vector(valid_symptoms)
    
    # Predict top 3 diseases
    predictions = classifier.predict(binary_vector, top_k=3)
    
    # Fetch rich knowledge base info for each predicted disease
    results = []
    for pred in predictions:
        disease_name = pred["disease"]
        info = get_disease_info(disease_name)
        pred_result = {
            "disease": disease_name,
            "probability": pred["probability"],
            "confidence": pred["confidence"],
            "advice": info
        }
        results.append(pred_result)
        
    import json
    return json.dumps({"diagnosis": results, "used_symptoms": valid_symptoms}, indent=2)
