from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import sys
import os
from datetime import datetime

# Add root project path to import backend and chatbot modules
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

try:
    from backend.classifier import classifier
    from backend.symptom_parser import parse_symptoms
    from backend.knowledge_base import get_disease_info
    from backend.llm_client import llm_client
    from chatbot.agent import get_agent_response
    from langchain_core.messages import HumanMessage, AIMessage

    # Preload the classifier when views are imported
    if not getattr(classifier, '_loaded', False):
        classifier.load()
except Exception as e:
    print(f"Error loading backend modules: {e}")

_chat_sessions = {}

@csrf_exempt
def diagnose(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        data = json.loads(request.body)
        symptoms_text = data.get("symptoms_text", "")
        patient_age = data.get("patient_age", 30)
        patient_gender = data.get("patient_gender", "unknown")
        symptom_duration = data.get("symptom_duration", "unknown")

        if not symptoms_text.strip():
            return JsonResponse({"detail": "symptoms_text cannot be empty"}, status=400)

        if len(symptoms_text.strip()) < 10:
            return JsonResponse({"detail": "Please describe your symptoms in more detail"}, status=400)

        start = datetime.now()

        # Step 1
        parsed = parse_symptoms(symptoms_text)
        binary_vector = parsed["binary_vector"]
        matched_symptoms = parsed["matched_symptoms"]

        if sum(binary_vector) == 0:
            return JsonResponse({"detail": "Could not match any symptoms from your description. Please be more specific."}, status=422)

        # Step 2
        raw_predictions = classifier.predict(binary_vector, top_k=3)

        # Step 3
        predictions = []
        for pred in raw_predictions:
            predictions.append({
                "disease": pred["disease"],
                "probability": pred["probability"],
                "confidence": pred["confidence"],
                "info": get_disease_info(pred["disease"]),
            })

        # Step 4
        summary = llm_client.get_diagnosis_summary(
            symptoms_text=symptoms_text,
            patient_age=patient_age,
            patient_gender=patient_gender,
            symptom_duration=symptom_duration,
            matched_symptoms=matched_symptoms,
            predictions=predictions
        )

        processing_ms = round((datetime.now() - start).total_seconds() * 1000, 2)

        return JsonResponse({
            "success": True,
            "predictions": predictions,
            "matched_symptoms": matched_symptoms,
            "active_symptom_count": sum(binary_vector),
            "summary": summary,
            "processing_time_ms": processing_ms,
            "timestamp": datetime.now().isoformat(),
        })

    except Exception as e:
        return JsonResponse({"detail": f"Internal error: {str(e)}"}, status=500)

def health(request):
    loaded = getattr(classifier, '_loaded', False)
    return JsonResponse({
        "status": "healthy" if loaded else "model_not_loaded",
        "num_diseases": classifier.num_diseases if loaded else 0,
        "num_symptoms": classifier.num_symptoms if loaded else 0,
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
    })

def get_diseases(request):
    return JsonResponse({
        "total": classifier.num_diseases,
        "diseases": classifier.diseases,
    })

def get_symptoms(request):
    return JsonResponse({
        "total": classifier.num_symptoms,
        "symptoms": classifier.symptom_list,
    })

@csrf_exempt
def chat(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        data = json.loads(request.body)
        session_id = data.get("session_id", "default")
        message = data.get("message", "")

        if not message.strip():
            return JsonResponse({"detail": "message cannot be empty"}, status=400)

        history = _chat_sessions.get(session_id, [])

        if not history:
            history = [
                AIMessage(content="Hello! I am your AI Medical Assistant. 👋 Describe your symptoms and I'll help you understand what might be going on.")
            ]

        history.append(HumanMessage(content=message))

        try:
            reply = get_agent_response(history)
        except Exception as e:
            reply = "I'm sorry, I encountered an issue. Could you rephrase or try again?"

        history.append(AIMessage(content=reply))
        _chat_sessions[session_id] = history

        serialised = [
            {"role": "assistant" if isinstance(m, AIMessage) else "user", "content": m.content}
            for m in history
        ]

        return JsonResponse({"reply": reply, "history": serialised})

    except Exception as e:
        return JsonResponse({"detail": f"Internal error: {str(e)}"}, status=500)
