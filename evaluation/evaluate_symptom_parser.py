"""
evaluate_symptom_parser.py
==========================================================
Evaluates symptom parsing accuracy for 5 Groq LLM models.

Each model is tested on all 25 test cases in test_cases.json.
For each test case, we check how many expected symptoms the model
correctly extracted from the patient's natural language input.

Metrics per model:
  - Per-case: precision, recall, F1 (symptom matching)
  - Overall:  macro-average precision, recall, F1
  - Overall:  exact match rate (all expected symptoms found)

Results saved to: evaluation/symptom_parser_eval_results.json

Run from project root:
    python evaluation/evaluate_symptom_parser.py
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

# ── Load official symptom list ────────────────────────────────────────
SYMPTOMS_TXT = ROOT / "data" / "symptom_list_clean.txt"
with open(SYMPTOMS_TXT, "r") as f:
    SYMPTOMS = [line.strip() for line in f if line.strip()]

# ── Load test cases ───────────────────────────────────────────────────
TEST_CASES_PATH = ROOT / "evaluation" / "test_cases.json"
with open(TEST_CASES_PATH, "r") as f:
    TEST_CASES = json.load(f)

# ── Model → API key mapping ───────────────────────────────────────────
# 5 models, 5 different API keys from .env
MODELS = [
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

# ── System prompt (same used in production) ───────────────────────────
SYSTEM_PROMPT_TEMPLATE = """\
You are a precise medical symptom extraction system.

Your task is to extract ONLY symptoms that are clearly present in the patient description,
and ONLY if they appear in the official symptom list provided.

OFFICIAL SYMPTOM LIST:
{symptoms_block}

STRICT EXTRACTION RULES:
1. Only return symptoms from the official list. Never invent or modify symptoms.
2. Remove any symptom that appears in a negated context (no, not, never, without, etc.).
3. Semantic matching allowed ONLY when meaning is clearly equivalent.
4. Do NOT infer symptoms from vague descriptions.
5. Do not include duplicates.
6. If no symptoms found, return [].

Return ONLY a valid JSON array of strings. No explanation. No markdown.
Each string must exactly match a symptom from the official list.

Output format: ["symptom_one", "symptom_two"]"""


def build_system_prompt() -> str:
    symptoms_block = "\n".join(f"- {s}" for s in SYMPTOMS)
    return SYSTEM_PROMPT_TEMPLATE.format(symptoms_block=symptoms_block)


def extract_symptoms_with_model(llm: ChatGroq, patient_text: str) -> list:
    """Call the LLM and parse the returned JSON symptom list."""
    system = SystemMessage(content=build_system_prompt())
    human  = HumanMessage(content=f"Patient description:\n{patient_text}")

    try:
        response = llm.invoke([system, human])
        raw = response.content.strip()

        # Extract JSON array
        start = raw.find("[")
        end   = raw.rfind("]")
        if start != -1 and end != -1:
            raw = raw[start : end + 1]
        else:
            return []

        parsed = json.loads(raw)
        if not isinstance(parsed, list):
            return []

        # Safety filter
        return [s for s in parsed if s in SYMPTOMS]

    except Exception as e:
        print(f"    [ERROR] {e}")
        return []


def compute_metrics(predicted: list, expected: list) -> dict:
    """Compute precision, recall, F1 for a single test case."""
    pred_set = set(predicted)
    exp_set  = set(expected)

    tp = len(pred_set & exp_set)
    fp = len(pred_set - exp_set)
    fn = len(exp_set - pred_set)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall    = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1        = (2 * precision * recall / (precision + recall)
                 if (precision + recall) > 0 else 0.0)

    return {
        "tp":        tp,
        "fp":        fp,
        "fn":        fn,
        "precision": round(precision, 4),
        "recall":    round(recall, 4),
        "f1":        round(f1, 4),
        "exact_match": pred_set >= exp_set,   # all expected found
    }


def evaluate_model(model_cfg: dict) -> dict:
    """Run all test cases through a single model and return results."""
    model_name = model_cfg["name"]
    api_key    = model_cfg["api_key"]

    print(f"\n{'='*60}")
    print(f"  Model: {model_name}")
    print(f"{'='*60}")

    if not api_key:
        print("  [SKIP] No API key found.")
        return {"model": model_name, "error": "No API key", "cases": []}

    try:
        llm = ChatGroq(model=model_name, groq_api_key=api_key, temperature=0.0)
    except Exception as e:
        print(f"  [SKIP] Failed to init model: {e}")
        return {"model": model_name, "error": str(e), "cases": []}

    case_results = []
    total_precision = total_recall = total_f1 = 0.0
    exact_count = 0

    for tc in TEST_CASES:
        cid   = tc["id"]
        text  = tc["text"]
        exp   = tc["expected_symptoms"]

        print(f"  Case {cid:2d}: ", end="", flush=True)
        predicted = extract_symptoms_with_model(llm, text)
        metrics   = compute_metrics(predicted, exp)

        total_precision += metrics["precision"]
        total_recall    += metrics["recall"]
        total_f1        += metrics["f1"]
        if metrics["exact_match"]:
            exact_count += 1

        print(f"P={metrics['precision']:.2f}  R={metrics['recall']:.2f}  "
              f"F1={metrics['f1']:.2f}  Exact={'✓' if metrics['exact_match'] else '✗'}")

        case_results.append({
            "id":               cid,
            "text":             text,
            "expected_symptoms": exp,
            "predicted_symptoms": predicted,
            **metrics,
        })

        time.sleep(0.5)   # avoid rate-limit

    n = len(TEST_CASES)
    overall = {
        "macro_precision": round(total_precision / n, 4),
        "macro_recall":    round(total_recall    / n, 4),
        "macro_f1":        round(total_f1        / n, 4),
        "exact_match_rate": round(exact_count / n * 100, 2),
        "total_cases":     n,
        "exact_matches":   exact_count,
    }

    print(f"\n  ── Overall ──")
    print(f"  Macro Precision : {overall['macro_precision']}")
    print(f"  Macro Recall    : {overall['macro_recall']}")
    print(f"  Macro F1        : {overall['macro_f1']}")
    print(f"  Exact Match Rate: {overall['exact_match_rate']}%")

    return {
        "model":   model_name,
        "overall": overall,
    }


def main():
    print("\n" + "="*60)
    print("  SYMPTOM PARSER EVALUATION — 5 Groq Models")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    all_results = {
        "evaluation_type": "symptom_parser",
        "timestamp":       datetime.now().isoformat(),
        "num_test_cases":  len(TEST_CASES),
        "total_symptoms":  len(SYMPTOMS),
        "models":          []
    }

    for model_cfg in MODELS:
        result = evaluate_model(model_cfg)
        all_results["models"].append(result)

    # Save results
    output_path = ROOT / "evaluation" / "symptom_parser_eval_results.json"
    with open(output_path, "w") as f:
        json.dump(all_results, f, indent=2)

    print(f"\n✅ Results saved to: {output_path}")

    # Print comparison summary
    print("\n" + "="*60)
    print("  MODEL COMPARISON SUMMARY — Symptom Parser")
    print("="*60)
    print(f"  {'Model':<30} {'Prec':>6}  {'Recall':>6}  {'F1':>6}  {'Exact%':>7}")
    print(f"  {'-'*30} {'-'*6}  {'-'*6}  {'-'*6}  {'-'*7}")
    for r in all_results["models"]:
        if "overall" in r:
            o = r["overall"]
            print(f"  {r['model']:<30} {o['macro_precision']:>6.4f}  "
                  f"{o['macro_recall']:>6.4f}  {o['macro_f1']:>6.4f}  "
                  f"{o['exact_match_rate']:>6.1f}%")
        else:
            print(f"  {r['model']:<30}  SKIPPED ({r.get('error','')})")


if __name__ == "__main__":
    main()
