"""
S3RAPHIM v2 — Anomaly detection pipeline

Requires: adsb_thesis_features.csv (from s3raphim_to_thesis.py)
Optional deps: pip install scikit-learn pandas joblib

Usage:
    python s3raphim_ml_pipeline.py
"""

from pathlib import Path
import sys
import json

CSV_FILE = "adsb_thesis_features.csv"
MODEL_FILE = "s3raphim_model.joblib"
METRICS_FILE = "s3raphim_metrics.json"

FEATURE_COLS = [
    "altitude", "velocity", "heading", "latitude", "longitude",
    "altitude_rate", "heading_change", "acceleration",
]
TARGET_COL = "abnormal"
TEST_SIZE = 0.3
RANDOM_STATE = 42
ALTITUDE_RATE_THRESHOLD = 100


def main():
    try:
        import pandas as pd
        from sklearn.model_selection import train_test_split, cross_val_score
        from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.metrics import (
            accuracy_score, roc_auc_score, precision_score,
            recall_score, f1_score, confusion_matrix, classification_report,
        )
        import joblib
    except ImportError:
        print("pip install scikit-learn pandas joblib")
        sys.exit(1)

    if not Path(CSV_FILE).exists():
        print(f"Missing {CSV_FILE}. Run: python s3raphim_to_thesis.py")
        sys.exit(1)

    print("=" * 60)
    print("        S3RAPHIM v2 — ML DETECTION PIPELINE")
    print("=" * 60)

    df = pd.read_csv(CSV_FILE)
    X = df[FEATURE_COLS].fillna(0)
    y = df[TARGET_COL].astype(int)

    print(f"Rows: {len(df):,} | normal={(y==0).sum():,} | abnormal={(y==1).sum():,}")
    if y.nunique() < 2:
        print("Need both classes. Generate WITH anomalies, then bridge.")
        sys.exit(1)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, stratify=y, random_state=RANDOM_STATE
    )
    print(f"Train: {len(X_train):,} | Test: {len(X_test):,}")

    def metrics(y_true, y_pred, y_prob=None):
        m = {
            "accuracy": float(accuracy_score(y_true, y_pred)),
            "precision": float(precision_score(y_true, y_pred, zero_division=0)),
            "recall": float(recall_score(y_true, y_pred, zero_division=0)),
            "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        }
        if y_prob is not None:
            try:
                m["roc_auc"] = float(roc_auc_score(y_true, y_prob))
            except ValueError:
                m["roc_auc"] = None
        return m

    def show(name, m):
        print(f"\n--- {name} ---")
        for k, v in m.items():
            print(f"  {k:10}: {'n/a' if v is None else f'{v:.4f}'}")

    results = {}

    # Rule baseline
    y_rule = (X_test["altitude_rate"].abs() > ALTITUDE_RATE_THRESHOLD).astype(int)
    results["rule"] = metrics(y_test, y_rule)
    show("Rule baseline", results["rule"])

    # QDA
    qda = QuadraticDiscriminantAnalysis()
    qda.fit(X_train, y_train)
    y_qda = qda.predict(X_test)
    y_qda_p = qda.predict_proba(X_test)[:, 1]
    results["qda"] = metrics(y_test, y_qda, y_qda_p)
    show("QDA", results["qda"])
    cv = cross_val_score(qda, X, y, cv=5, scoring="accuracy")
    print(f"  CV acc   : {cv.mean():.4f} ± {cv.std():.4f}")

    # Random Forest
    rf = RandomForestClassifier(
        n_estimators=100, max_depth=12, random_state=RANDOM_STATE, n_jobs=-1
    )
    rf.fit(X_train, y_train)
    y_rf = rf.predict(X_test)
    y_rf_p = rf.predict_proba(X_test)[:, 1]
    results["random_forest"] = metrics(y_test, y_rf, y_rf_p)
    show("Random Forest", results["random_forest"])
    cv = cross_val_score(rf, X, y, cv=5, scoring="accuracy")
    print(f"  CV acc   : {cv.mean():.4f} ± {cv.std():.4f}")

    print("\n--- QDA error analysis ---")
    print(confusion_matrix(y_test, y_qda))
    print(classification_report(y_test, y_qda, target_names=["normal", "abnormal"]))

    def key(item):
        m = item[1]
        return (m.get("f1") or 0, m.get("roc_auc") or 0)

    best_name, best_m = max(
        [("qda", results["qda"]), ("random_forest", results["random_forest"])],
        key=key,
    )
    best_model = qda if best_name == "qda" else rf
    print(f"\nBest model: {best_name}")

    meta = {
        "model_name": best_name,
        "feature_cols": FEATURE_COLS,
        "metrics": results,
        "best_metrics": best_m,
        "version": "v2",
    }
    joblib.dump({"model": best_model, "meta": meta}, MODEL_FILE)
    with open(METRICS_FILE, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    print(f"Saved → {MODEL_FILE}")
    print(f"Saved → {METRICS_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    main()