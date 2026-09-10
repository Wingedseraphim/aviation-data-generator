"""
S3RAPHIM QDA Evaluation
Trains Quadratic Discriminant Analysis on thesis-bridge features
and reports metrics in the same style as the B.Sc project.

Requires:
    pip install scikit-learn pandas matplotlib

Usage:
    python s3raphim_qda_eval.py
"""

from pathlib import Path
import sys

CSV_FILE = "adsb_thesis_features.csv"
FEATURE_COLS = [
    "altitude",
    "velocity",
    "heading",
    "latitude",
    "longitude",
    "altitude_rate",
    "heading_change",
    "acceleration",
]
TARGET_COL = "abnormal"


def main():
    try:
        import pandas as pd
        from sklearn.model_selection import train_test_split, cross_val_score
        from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
        from sklearn.metrics import (
            accuracy_score,
            roc_auc_score,
            precision_score,
            recall_score,
            f1_score,
            roc_curve,
            auc,
        )
    except ImportError:
        print("Missing packages. Install with:")
        print("  pip install scikit-learn pandas matplotlib")
        sys.exit(1)

    path = Path(CSV_FILE)
    if not path.exists():
        print(f"File not found: {CSV_FILE}")
        print("Run s3raphim_to_thesis.py first.")
        sys.exit(1)

    print("=" * 55)
    print("     S3RAPHIM QDA EVALUATION (Thesis pipeline)")
    print("=" * 55)

    df = pd.read_csv(CSV_FILE)
    print(f"Loaded {len(df):,} rows from {CSV_FILE}")

    missing = [c for c in FEATURE_COLS + [TARGET_COL] if c not in df.columns]
    if missing:
        print(f"Missing columns: {missing}")
        sys.exit(1)

    X = df[FEATURE_COLS].fillna(0)
    y = df[TARGET_COL].astype(int)

    print(f"Class balance → normal: {(y == 0).sum():,} | abnormal: {(y == 1).sum():,}")

    # Need both classes for QDA / ROC
    if y.nunique() < 2:
        print("Only one class present. Generate data with more anomalies/variation.")
        sys.exit(1)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, stratify=y, random_state=42
    )

    qda = QuadraticDiscriminantAnalysis()
    qda.fit(X_train, y_train)

    y_pred = qda.predict(X_test)
    y_prob = qda.predict_proba(X_test)[:, 1]

    acc = accuracy_score(y_test, y_pred)
    roc = roc_auc_score(y_test, y_prob)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)

    print("\n--- Test metrics ---")
    print(f"Accuracy : {acc:.4f}")
    print(f"ROC-AUC  : {roc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall   : {rec:.4f}")
    print(f"F1-Score : {f1:.4f}")

    cv = cross_val_score(qda, X, y, cv=5, scoring="accuracy")
    print(f"\n5-fold CV accuracy: {cv.mean():.4f} ± {cv.std():.4f}")

    # Optional ROC plot
    try:
        import matplotlib.pyplot as plt

        fpr, tpr, _ = roc_curve(y_test, y_prob)
        roc_auc = auc(fpr, tpr)

        plt.figure(figsize=(6, 5))
        plt.plot(fpr, tpr, label=f"QDA (AUC = {roc_auc:.3f})")
        plt.plot([0, 1], [0, 1], "k--", label="Random")
        plt.xlabel("False Positive Rate")
        plt.ylabel("True Positive Rate")
        plt.title("ROC Curve — S3RAPHIM QDA")
        plt.legend(loc="lower right")
        plt.tight_layout()
        plt.savefig("s3raphim_qda_roc.png", dpi=150)
        print("\nSaved ROC curve → s3raphim_qda_roc.png")
    except Exception as e:
        print(f"\nROC plot skipped: {e}")

    print("\nDone.")
    print("=" * 55)


if __name__ == "__main__":
    main()