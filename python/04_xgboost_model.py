# ============================================================
# 04. XGBOOST SLA BREACH PREDICTION MODEL
# Quick Commerce SLA Breach Analysis
# ============================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    roc_auc_score,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
    roc_curve
)

from xgboost import XGBClassifier

# ============================================================
# 1. PATHS
# ============================================================

DATA_PATH = "outputs/ml_ready_dataset.csv"

MODEL_DIR = Path("outputs/models")
CHART_DIR = Path("outputs/charts")

MODEL_DIR.mkdir(parents=True, exist_ok=True)
CHART_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# 2. LOAD DATA
# ============================================================

df = pd.read_csv(DATA_PATH)

print("=" * 60)
print("QUICK COMMERCE SLA - XGBOOST MODEL")
print("=" * 60)

print(f"\nDataset shape: {df.shape}")

# ============================================================
# 3. SEPARATE FEATURES AND TARGET
# ============================================================

target_column = "sla_breached"

X = df.drop(columns=[target_column])
y = df[target_column]

print("\n--- Target Distribution ---")

print(
    y.value_counts()
    .sort_index()
)

print(
    f"\nOverall breach rate: "
    f"{y.mean() * 100:.2f}%"
)

# ============================================================
# 4. TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("\n--- Train/Test Split ---")

print(f"Training rows : {len(X_train):,}")
print(f"Testing rows  : {len(X_test):,}")

print(
    f"Training breach rate: "
    f"{y_train.mean() * 100:.2f}%"
)

print(
    f"Testing breach rate : "
    f"{y_test.mean() * 100:.2f}%"
)

# ============================================================
# 5. HANDLE CLASS IMBALANCE
# ============================================================

negative_count = (y_train == 0).sum()
positive_count = (y_train == 1).sum()

scale_pos_weight = (
    negative_count / positive_count
)

print("\n--- Class Balance ---")

print(f"Non-breach orders : {negative_count:,}")
print(f"Breach orders     : {positive_count:,}")
print(
    f"Scale positive weight: "
    f"{scale_pos_weight:.2f}"
)

# ============================================================
# 6. TRAIN XGBOOST MODEL
# ============================================================

model = XGBClassifier(
    n_estimators=300,
    max_depth=5,
    learning_rate=0.05,
    subsample=0.80,
    colsample_bytree=0.80,
    objective="binary:logistic",
    eval_metric="logloss",
    scale_pos_weight=scale_pos_weight,
    random_state=42,
    n_jobs=-1
)

print("\n--- Training XGBoost ---")

model.fit(
    X_train,
    y_train
)

print("Model training complete.")

# ============================================================
# 7. PREDICTIONS
# ============================================================

y_pred = model.predict(X_test)

y_pred_probability = model.predict_proba(
    X_test
)[:, 1]

# ============================================================
# 8. MODEL EVALUATION
# ============================================================

accuracy = accuracy_score(
    y_test,
    y_pred
)

precision = precision_score(
    y_test,
    y_pred,
    zero_division=0
)

recall = recall_score(
    y_test,
    y_pred,
    zero_division=0
)

f1 = f1_score(
    y_test,
    y_pred,
    zero_division=0
)

roc_auc = roc_auc_score(
    y_test,
    y_pred_probability
)

print("\n" + "=" * 60)
print("MODEL PERFORMANCE")
print("=" * 60)

print(f"\nAccuracy  : {accuracy:.4f}")
print(f"Precision : {precision:.4f}")
print(f"Recall    : {recall:.4f}")
print(f"F1 Score  : {f1:.4f}")
print(f"ROC-AUC   : {roc_auc:.4f}")

# ============================================================
# 9. CLASSIFICATION REPORT
# ============================================================

print("\n--- Classification Report ---")

print(
    classification_report(
        y_test,
        y_pred,
        target_names=[
            "SLA Met",
            "SLA Breached"
        ],
        zero_division=0
    )
)

# ============================================================
# 10. CONFUSION MATRIX
# ============================================================

cm = confusion_matrix(
    y_test,
    y_pred
)

print("\n--- Confusion Matrix ---")

print(cm)

plt.figure(figsize=(7, 6))

plt.imshow(
    cm,
    interpolation="nearest"
)

plt.title("XGBoost Confusion Matrix")

plt.xlabel("Predicted Label")
plt.ylabel("Actual Label")

plt.xticks(
    [0, 1],
    ["SLA Met", "SLA Breached"]
)

plt.yticks(
    [0, 1],
    ["SLA Met", "SLA Breached"]
)

for i in range(2):
    for j in range(2):
        plt.text(
            j,
            i,
            cm[i, j],
            ha="center",
            va="center"
        )

plt.colorbar()

plt.tight_layout()

plt.savefig(
    CHART_DIR / "09_xgboost_confusion_matrix.png",
    dpi=150
)

plt.close()

# ============================================================
# 11. ROC CURVE
# ============================================================

fpr, tpr, thresholds = roc_curve(
    y_test,
    y_pred_probability
)

plt.figure(figsize=(8, 6))

plt.plot(
    fpr,
    tpr,
    label=f"XGBoost AUC = {roc_auc:.3f}"
)

plt.plot(
    [0, 1],
    [0, 1],
    linestyle="--",
    label="Random Classifier"
)

plt.title("XGBoost ROC Curve")

plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")

plt.legend()

plt.tight_layout()

plt.savefig(
    CHART_DIR / "10_xgboost_roc_curve.png",
    dpi=150
)

plt.close()

# ============================================================
# 12. FEATURE IMPORTANCE
# ============================================================

feature_importance = pd.DataFrame({
    "feature": X.columns,
    "importance": model.feature_importances_
})

feature_importance = (
    feature_importance
    .sort_values(
        "importance",
        ascending=False
    )
)

print("\n--- Top 15 Feature Importances ---")

print(
    feature_importance
    .head(15)
    .to_string(index=False)
)

# ============================================================
# 13. FEATURE IMPORTANCE CHART
# ============================================================

top_features = (
    feature_importance
    .head(15)
    .sort_values(
        "importance",
        ascending=True
    )
)

plt.figure(figsize=(10, 7))

plt.barh(
    top_features["feature"],
    top_features["importance"]
)

plt.title(
    "Top 15 XGBoost Feature Importances"
)

plt.xlabel("Importance")
plt.ylabel("Feature")

plt.tight_layout()

plt.savefig(
    CHART_DIR / "11_xgboost_feature_importance.png",
    dpi=150
)

plt.close()

# ============================================================
# 14. SAVE FEATURE IMPORTANCE
# ============================================================

feature_importance.to_csv(
    CHART_DIR / "xgboost_feature_importance.csv",
    index=False
)

# ============================================================
# 15. SAVE MODEL
# ============================================================

model_path = (
    MODEL_DIR /
    "xgboost_sla_breach_model.json"
)

model.save_model(
    model_path
)

print(
    f"\nModel saved to:"
    f"\n{model_path}"
)

# ============================================================
# 16. SAVE MODEL METRICS
# ============================================================

metrics = pd.DataFrame({
    "metric": [
        "accuracy",
        "precision",
        "recall",
        "f1_score",
        "roc_auc"
    ],
    "value": [
        accuracy,
        precision,
        recall,
        f1,
        roc_auc
    ]
})

metrics.to_csv(
    MODEL_DIR / "xgboost_model_metrics.csv",
    index=False
)

# ============================================================
# 17. FINAL STATUS
# ============================================================

print("\n" + "=" * 60)
print("XGBOOST MODEL COMPLETE")
print("=" * 60)

print("\nGenerated model files:")
print("  - xgboost_sla_breach_model.json")
print("  - xgboost_model_metrics.csv")

print("\nGenerated charts:")
print("  - 09_xgboost_confusion_matrix.png")
print("  - 10_xgboost_roc_curve.png")
print("  - 11_xgboost_feature_importance.png")

print("\n" + "=" * 60)