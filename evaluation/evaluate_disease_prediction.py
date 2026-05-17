"""
evaluate_disease_prediction.py
==========================================================
Evaluates disease prediction accuracy for 5 Groq LLM models.

Strategy:
  For each test case we GIVE the model the expected_symptoms (ground-truth
  symptoms already extracted) and ask it to predict the disease.
  This isolates prediction accuracy from parsing accuracy.

  We also run our LightGBM classifier on the same symptom vectors
  and include it as "Model 0 (LightGBM-Baseline)" for comparison.

Metrics:
  - Top-1 accuracy  : correct disease is the #1 prediction
  - Top-3 accuracy  : correct disease appears in top 3 predictions
  - Avg confidence  : mean probability of correct disease when found

Results saved to: evaluation/disease_prediction_eval_results.json

Run from project root:
    python evaluation/evaluate_disease_prediction.py
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime

# ── Force UTF-8 output on Windows to support unicode symbols ─────────
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

# ── Path setup ────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "backend"))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env", override=True)

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

# ── Backend imports ───────────────────────────────────────────────────
from classifier import classifier
from symptom_parser import to_binary_vector

# Load LightGBM model
classifier.load()

# ── Load official symptom list ────────────────────────────────────────
SYMPTOMS_TXT = ROOT / "data" / "symptom_list_clean.txt"
with open(SYMPTOMS_TXT, "r") as f:
    SYMPTOMS = [line.strip() for line in f if line.strip()]

# ── Load test cases ───────────────────────────────────────────────────
TEST_CASES_PATH = ROOT / "evaluation" / "test_cases.json"
with open(TEST_CASES_PATH, "r") as f:
    TEST_CASES = json.load(f)

# ── Model configs ─────────────────────────────────────────────────────
LLM_MODELS = [
    {
        "name":    "llama-3.1-8b-instant",
        "api_key": os.getenv("GROQ_API_KEY"),
    },
    {
        "name":    "llama-3.3-70b-versatile",
        "api_key": os.getenv("GROQ_API_KEY_1"),
    },
    {
        "name":    "meta-llama/Llama-4-Scout-17B-16E-Instruct",       # closest available text model
        "api_key": os.getenv("GROQ_API_KEY_2"),
    },
    {
        "name":    "openai/gpt-oss-safeguard-20b",
        "api_key": os.getenv("GROQ_API_KEY_3"),
    },
    {
        "name":    "openai/gpt-oss-120b",
        "api_key": os.getenv("GROQ_API_KEY_4"),
    },
]

# ── Prompt ────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """\
You are a medical diagnosis assistant. Given symptoms and a disease list, \
pick the 3 most likely diseases.

CRITICAL RULES:
1. You MUST copy disease names EXACTLY as written in the provided list (same spelling, spacing, punctuation).
2. Respond with ONLY a JSON object — no explanation, no markdown, no code block.
3. Never invent or rephrase disease names.

Example:
  Symptoms: fever, headache, chill, snuffle
  -> {"top1": "influenza", "top2": "upper respiratory infection", "top3": "pneumonia"}

Your response format:
{"top1": "exact name", "top2": "exact name", "top3": "exact name"}
"""

def normalize(s: str) -> str:
    """Lowercase + strip for consistent comparison."""
    return s.lower().strip()


def diseases_match(pred: str, expected: str) -> bool:
    """True if pred matches expected. Tries exact → partial containment."""
    p = normalize(pred)
    e = normalize(expected)
    if p == e:
        return True
    # Partial: one string contained in the other (handles abbreviations like
    # 'hepatitis b' vs 'hepatitis B', 'parkinson' vs 'parkinson disease', etc.)
    if p in e or e in p:
        return True
    return False


def predict_with_llm(llm: ChatGroq, symptoms: list, disease_list: list) -> dict:
    """Ask an LLM to predict top-3 diseases from a list of symptoms."""
    disease_str  = "\n".join(f"  - {d}" for d in disease_list)  # ALL diseases
    symptoms_str = ", ".join(symptoms)

    human_content = (
        f"Symptoms: {symptoms_str}\n\n"
        f"Disease list (pick EXACTLY from these names):\n{disease_str}\n\n"
        "Return the top 3 most likely diseases from the list above."
    )

    system = SystemMessage(content=SYSTEM_PROMPT)
    human  = HumanMessage(content=human_content)

    try:
        response = llm.invoke([system, human])
        raw = response.content.strip()

        # Extract JSON object
        start = raw.find("{")
        end   = raw.rfind("}") + 1
        if start != -1 and end > start:
            raw = raw[start:end]
        else:
            return {"top1": "", "top2": "", "top3": ""}

        return json.loads(raw)

    except Exception as e:
        print(f"    [ERROR] {e}")
        return {"top1": "", "top2": "", "top3": ""}


def evaluate_lightgbm() -> dict:
    """Evaluate our LightGBM model on all test cases."""
    print(f"\n{'='*60}")
    print("  Model: LightGBM (Baseline — our trained model)")
    print(f"{'='*60}")

    case_results = []
    top1_correct = top3_correct = 0

    for tc in TEST_CASES:
        cid      = tc["id"]
        symptoms = tc["expected_symptoms"]
        expected = tc["expected_disease"].lower()

        binary_vec   = to_binary_vector(symptoms)
        predictions  = classifier.predict(binary_vec, top_k=3)

        pred_diseases = [p["disease"] for p in predictions]
        top1_hit = diseases_match(pred_diseases[0], expected) if pred_diseases else False
        top3_hit = any(diseases_match(p, expected) for p in pred_diseases)

        if top1_hit:
            top1_correct += 1
        if top3_hit:
            top3_correct += 1

        print(f"  Case {cid:2d}: Expected={expected!r:<40} "
              f"Top1={pred_diseases[0] if pred_diseases else 'N/A'!r}  "
              f"{'✓' if top1_hit else '✗'}")

        case_results.append({
            "id":               cid,
            "expected_disease": expected,
            "predicted_top1":  pred_diseases[0] if len(pred_diseases) > 0 else "",
            "predicted_top2":  pred_diseases[1] if len(pred_diseases) > 1 else "",
            "predicted_top3":  pred_diseases[2] if len(pred_diseases) > 2 else "",
            "top1_correct":    top1_hit,
            "top3_correct":    top3_hit,
        })

    n = len(TEST_CASES)
    overall = {
        "top1_accuracy": round(top1_correct / n * 100, 2),
        "top3_accuracy": round(top3_correct / n * 100, 2),
        "top1_correct":  top1_correct,
        "top3_correct":  top3_correct,
        "total_cases":   n,
    }

    print(f"\n  Top-1 Accuracy: {overall['top1_accuracy']}%")
    print(f"  Top-3 Accuracy: {overall['top3_accuracy']}%")

    return {
        "model":   "LightGBM-Baseline",
        "overall": overall,
    }


def evaluate_llm_model(model_cfg: dict, disease_list: list) -> dict:
    """Evaluate a single LLM on all test cases."""
    model_name = model_cfg["name"]
    api_key    = model_cfg["api_key"]

    print(f"\n{'='*60}")
    print(f"  Model: {model_name}")
    print(f"{'='*60}")

    if not api_key:
        print("  [SKIP] No API key.")
        return {"model": model_name, "error": "No API key", "cases": []}

    try:
        llm = ChatGroq(model=model_name, groq_api_key=api_key, temperature=0.0)
    except Exception as e:
        print(f"  [SKIP] Init error: {e}")
        return {"model": model_name, "error": str(e), "cases": []}

    case_results = []
    top1_correct = top3_correct = 0

    for tc in TEST_CASES:
        cid      = tc["id"]
        symptoms = tc["expected_symptoms"]
        expected = tc["expected_disease"].lower()

        print(f"  Case {cid:2d}: ", end="", flush=True)

        preds    = predict_with_llm(llm, symptoms, disease_list)
        top1     = preds.get("top1", "").lower().strip()
        top2     = preds.get("top2", "").lower().strip()
        top3     = preds.get("top3", "").lower().strip()

        top1_hit = diseases_match(top1, expected)
        top3_hit = any(diseases_match(t, expected) for t in [top1, top2, top3])

        if top1_hit:
            top1_correct += 1
        if top3_hit:
            top3_correct += 1

        print(f"Expected={expected!r:<40} Top1={top1!r}  {'✓' if top1_hit else '✗'}")

        case_results.append({
            "id":               cid,
            "expected_disease": expected,
            "predicted_top1":  top1,
            "predicted_top2":  top2,
            "predicted_top3":  top3,
            "top1_correct":    top1_hit,
            "top3_correct":    top3_hit,
        })

        time.sleep(0.5)

    n = len(TEST_CASES)
    overall = {
        "top1_accuracy": round(top1_correct / n * 100, 2),
        "top3_accuracy": round(top3_correct / n * 100, 2),
        "top1_correct":  top1_correct,
        "top3_correct":  top3_correct,
        "total_cases":   n,
    }

    print(f"\n  Top-1 Accuracy: {overall['top1_accuracy']}%")
    print(f"  Top-3 Accuracy: {overall['top3_accuracy']}%")

    return {
        "model":   model_name,
        "overall": overall,
    }


def main():
    print("\n" + "="*60)
    print("  DISEASE PREDICTION EVALUATION — 5 LLMs + LightGBM")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    # Get disease list from our trained model
    disease_list = classifier.diseases

    all_results = {
        "evaluation_type": "disease_prediction",
        "timestamp":       datetime.now().isoformat(),
        "num_test_cases":  len(TEST_CASES),
        "known_diseases":  len(disease_list),
        "models":          []
    }

    # 1. LightGBM baseline
    lgb_result = evaluate_lightgbm()
    all_results["models"].append(lgb_result)

    # 2. Each LLM
    for model_cfg in LLM_MODELS:
        result = evaluate_llm_model(model_cfg, disease_list)
        all_results["models"].append(result)

    # Save results
    output_path = ROOT / "evaluation" / "disease_prediction_eval_results.json"
    with open(output_path, "w") as f:
        json.dump(all_results, f, indent=2)

    print(f"\n✅ Results saved to: {output_path}")

    # Comparison summary
    print("\n" + "="*60)
    print("  MODEL COMPARISON — Disease Prediction")
    print("="*60)
    print(f"  {'Model':<35} {'Top-1%':>7}  {'Top-3%':>7}")
    print(f"  {'-'*35} {'-'*7}  {'-'*7}")
    for r in all_results["models"]:
        if "overall" in r:
            o = r["overall"]
            print(f"  {r['model']:<35} {o['top1_accuracy']:>6.1f}%  {o['top3_accuracy']:>6.1f}%")
        else:
            print(f"  {r['model']:<35}  SKIPPED ({r.get('error','')})")


if __name__ == "__main__":
    main()
