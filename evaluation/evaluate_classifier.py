"""
evaluate_classifier.py
Evaluates the trained LightGBM classifier on the held-out test set.

Run from project root:
    python evaluation/evaluate_classifier.py

Expects:
    - models/lightgbm_model.pkl
    - models/label_encoder.pkl
    - data/processed/test.csv
    - data/symptom_list.txt
"""

import pickle
import json
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    top_k_accuracy_score,
    confusion_matrix
)

# ── Paths ─────────────────────────────────────────────────────────────
ROOT         = Path(__file__).parent.parent
MODEL_PATH   = ROOT / "models" / "lightgbm_model.pkl"
ENCODER_PATH = ROOT / "models" / "label_encoder.pkl"
TEST_CSV     = ROOT / "data" / "processed" / "test.csv"
SYMPTOMS_TXT = ROOT / "data" / "symptom_list.txt"
OUTPUT_PATH  = Path(__file__).parent / "classifier_eval_results.json"


def load_artifacts():
    with open(MODEL_PATH,   "rb") as f: model = pickle.load(f)
    with open(ENCODER_PATH, "rb") as f: le    = pickle.load(f)
    with open(SYMPTOMS_TXT, "r")  as f:
        symptom_list = [line.strip() for line in f if line.strip()]
    return model, le, symptom_list


def load_test_data(symptom_list: list):
    df = pd.read_csv(TEST_CSV)

    # Rename columns to match symptom_list (strip, lowercase)
    df.columns = df.columns.str.strip().str.lower()

    feature_cols = [c for c in df.columns if c != "disease"]
    X = df[feature_cols].values.astype(np.float32)
    y_raw = df["disease"].values

    return X, y_raw, df


def run_evaluation():
    print("=" * 60)
    print("   CLASSIFIER EVALUATION")
    print("=" * 60)

    # Load
    model, le, symptom_list = load_artifacts()
    X_test, y_raw, df = load_test_data(symptom_list)

    print(f"  Test samples    : {len(df)}")
    print(f"  Disease classes : {len(le.classes_)}")
    print(f"  Feature count   : {X_test.shape[1]}")
    print("=" * 60)

    # Encode labels
    y_test = le.transform(y_raw)

    # Predictions
    y_pred      = model.predict(X_test)
    y_pred_prob = model.predict_proba(X_test)

    # ── Core Metrics ──────────────────────────────────────────────────
    top1 = accuracy_score(y_test, y_pred)
    top3 = top_k_accuracy_score(y_test, y_pred_prob, k=3)
    top5 = top_k_accuracy_score(y_test, y_pred_prob, k=5)

    print(f"\n  Top-1 Accuracy  : {top1:.4f}  ({top1*100:.2f}%)")
    print(f"  Top-3 Accuracy  : {top3:.4f}  ({top3*100:.2f}%)")
    print(f"  Top-5 Accuracy  : {top5:.4f}  ({top5*100:.2f}%)")

    # ── Per-class F1 ──────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("   PER-CLASS REPORT (Top 20 most frequent diseases)")
    print("=" * 60)

    # Find top 20 most frequent classes in test set
    top20_idx    = pd.Series(y_test).value_counts().head(20).index.tolist()
    top20_mask   = np.isin(y_test, top20_idx)
    top20_labels = le.inverse_transform(top20_idx)

    print(classification_report(
        y_test[top20_mask],
        y_pred[top20_mask],
        labels=top20_idx,
        target_names=top20_labels,
        zero_division=0
    ))

    # ── Worst Performing Classes ──────────────────────────────────────
    report_dict = classification_report(
        y_test, y_pred,
        labels=list(range(len(le.classes_))),
        target_names=le.classes_,
        output_dict=True,
        zero_division=0
    )

    class_f1 = {
        cls: report_dict[cls]["f1-score"]
        for cls in le.classes_
        if cls in report_dict
    }
    worst5 = sorted(class_f1.items(), key=lambda x: x[1])[:5]
    best5  = sorted(class_f1.items(), key=lambda x: x[1], reverse=True)[:5]

    print("\n  Worst 5 diseases (by F1):")
    for disease, f1 in worst5:
        print(f"    {disease:45s}  F1: {f1:.3f}")

    print("\n  Best 5 diseases (by F1):")
    for disease, f1 in best5:
        print(f"    {disease:45s}  F1: {f1:.3f}")

    # ── Per-sample Top-3 Check ────────────────────────────────────────
    correct_in_top3 = 0
    for i in range(len(y_test)):
        top3_preds = np.argsort(y_pred_prob[i])[::-1][:3]
        if y_test[i] in top3_preds:
            correct_in_top3 += 1

    print(f"\n  Samples where true disease is in top-3: {correct_in_top3}/{len(y_test)}")

    # ── Save Results ──────────────────────────────────────────────────
    results = {
        "top1_accuracy":  round(top1, 4),
        "top3_accuracy":  round(top3, 4),
        "top5_accuracy":  round(top5, 4),
        "num_classes":    len(le.classes_),
        "num_test_rows":  len(df),
        "worst_5_classes": [{"disease": d, "f1": round(f, 3)} for d, f in worst5],
        "best_5_classes":  [{"disease": d, "f1": round(f, 3)} for d, f in best5],
    }

    with open(OUTPUT_PATH, "w") as f:
        json.dump(results, f, indent=2)

    print("\n" + "=" * 60)
    print("   SUMMARY")
    print("=" * 60)
    print(f"  Top-1 : {top1*100:.2f}%")
    print(f"  Top-3 : {top3*100:.2f}%")
    print(f"  Top-5 : {top5*100:.2f}%")
    print(f"\n  Results saved to: {OUTPUT_PATH}")
    print("=" * 60)


if __name__ == "__main__":
    run_evaluation()