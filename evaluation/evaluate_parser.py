"""
evaluate_parser.py
Evaluates how accurately the symptom parser extracts symptoms from patient text.

Run from project root:
    python evaluation/evaluate_parser.py

Expects:
    - evaluation/test_cases.json
    - data/symptom_list.txt
    - backend/symptom_parser.py (with parse_symptoms function)
    - .env with GROQ_API_KEY
"""

import json
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Add backend to path so we can import symptom_parser
sys.path.append(str(Path(__file__).parent.parent / "backend"))
from symptom_parser import parse_symptoms

# ── Paths ─────────────────────────────────────────────────────────────
TEST_CASES_PATH  = Path(__file__).parent / "test_cases.json"
SYMPTOM_LIST_PATH = Path(__file__).parent.parent / "data" / "symptom_list_clean.txt"


def load_test_cases() -> list:
    with open(TEST_CASES_PATH, "r") as f:
        return json.load(f)


def load_symptom_list() -> list:
    with open(SYMPTOM_LIST_PATH, "r") as f:
        return [line.strip() for line in f if line.strip()]


def evaluate_single_case(case: dict, predicted_symptoms: list) -> dict:
    """
    Evaluates one test case.
    Returns precision, recall, f1 and negation check result.
    """
    expected = set(case["expected_symptoms"])
    predicted = set(predicted_symptoms)
    negations = set(case.get("negation_check", []))

    # True positives — correctly identified
    tp = expected & predicted

    # False negatives — expected but missed
    fn = expected - predicted

    # False positives — predicted but not expected
    fp = predicted - expected

    # Negation violations — symptoms that should NOT be included but were
    negation_violations = negations & predicted

    precision = len(tp) / len(predicted) if predicted else 0.0
    recall    = len(tp) / len(expected)  if expected  else 0.0
    f1        = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

    return {
        "id":                   case["id"],
        "patient_input":        case["patient_input"][:80] + "...",
        "expected_disease":     case.get("expected_disease", "unknown"),
        "expected_symptoms":    list(expected),
        "predicted_symptoms":   list(predicted),
        "true_positives":       list(tp),
        "false_negatives":      list(fn),
        "false_positives":      list(fp),
        "negation_violations":  list(negation_violations),
        "precision":            round(precision, 3),
        "recall":               round(recall, 3),
        "f1":                   round(f1, 3),
        "passed_negation":      len(negation_violations) == 0,
    }


def run_evaluation():
    test_cases    = load_test_cases()
    symptom_list  = load_symptom_list()

    print("=" * 60)
    print("   SYMPTOM PARSER EVALUATION")
    print("=" * 60)
    print(f"Total test cases : {len(test_cases)}")
    print(f"Symptom list size: {len(symptom_list)}")
    print("=" * 60)

    results        = []
    total_precision = 0
    total_recall    = 0
    total_f1        = 0
    negation_passed = 0
    negation_total  = 0

    for i, case in enumerate(test_cases, 1):
        print(f"\n[{i}/{len(test_cases)}] Case ID {case['id']}")
        print(f"  Input   : {case['patient_input'][:70]}...")

        # Run parser
        result       = parse_symptoms(case["patient_input"])
        predicted    = result["matched_symptoms"]

        # Evaluate
        eval_result  = evaluate_single_case(case, predicted)
        results.append(eval_result)

        # Print per-case result
        print(f"  Expected disease : {eval_result['expected_disease']}")
        print(f"  Expected symptoms: {eval_result['expected_symptoms']}")
        print(f"  Predicted        : {eval_result['predicted_symptoms']}")
        print(f"  TP: {eval_result['true_positives']}")
        print(f"  FN: {eval_result['false_negatives']}")
        print(f"  FP: {eval_result['false_positives']}")
        print(f"  Precision: {eval_result['precision']}  Recall: {eval_result['recall']}  F1: {eval_result['f1']}")

        if case.get("negation_check"):
            negation_total += 1
            status = "✓ PASSED" if eval_result["passed_negation"] else f"✗ FAILED — wrongly included: {eval_result['negation_violations']}"
            print(f"  Negation check   : {status}")
            if eval_result["passed_negation"]:
                negation_passed += 1

        total_precision += eval_result["precision"]
        total_recall    += eval_result["recall"]
        total_f1        += eval_result["f1"]

    # ── Summary ───────────────────────────────────────────────────────
    n = len(test_cases)
    avg_precision = round(total_precision / n, 3)
    avg_recall    = round(total_recall    / n, 3)
    avg_f1        = round(total_f1        / n, 3)

    print("\n" + "=" * 60)
    print("   OVERALL RESULTS")
    print("=" * 60)
    print(f"  Average Precision     : {avg_precision}")
    print(f"  Average Recall        : {avg_recall}")
    print(f"  Average F1 Score      : {avg_f1}")
    if negation_total > 0:
        neg_acc = round(negation_passed / negation_total * 100, 1)
        print(f"  Negation Accuracy     : {negation_passed}/{negation_total} ({neg_acc}%)")
    print("=" * 60)

    # Save detailed results
    output_path = Path(__file__).parent / "parser_eval_results.json"
    with open(output_path, "w") as f:
        json.dump({
            "summary": {
                "total_cases":     n,
                "avg_precision":   avg_precision,
                "avg_recall":      avg_recall,
                "avg_f1":          avg_f1,
                "negation_passed": negation_passed,
                "negation_total":  negation_total,
            },
            "cases": results
        }, f, indent=2)

    print(f"\nDetailed results saved to: {output_path}")


if __name__ == "__main__":
    run_evaluation()