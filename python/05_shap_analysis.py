# ============================================================
# 05. SHAP ANALYSIS
# Quick Commerce SLA Breach Analysis
# ============================================================

import os
import pandas as pd
import numpy as np
import shap
import matplotlib.pyplot as plt
import xgboost as xgb

from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split


# ------------------------------------------------------------
# 1. PATHS
# ------------------------------------------------------------

DATA_PATH = "outputs/ml_ready_dataset.csv"
MODEL_PATH = "outputs/models/xgboost_sla_breach_model.json"
CHART_PATH = "outputs/charts"

os.makedirs(CHART_PATH, exist_ok=True)


# ------------------------------------------------------------
# 2. LOAD DATA
# ------------------------------------------------------------

print("=" * 60)
print("QUICK COMMERCE SLA - SHAP ANALYSIS")
print("=" * 60)

df = pd.read_csv(DATA_PATH)

print(f"\nDataset shape: {df.shape}")


# ------------------------------------------------------------
# 3. SEPARATE FEATURES AND TARGET
# ------------------------------------------------------------

target_column = "sla_breached"

X = df.drop(columns=[target_column])
y = df[target_column]

print(f"Feature rows: {len(X):,}")
print(f"Feature columns: {X.shape[1]}")
print(f"Target column: {target_column}")


# ------------------------------------------------------------
# 4. SAME TRAIN / TEST SPLIT AS XGBOOST MODEL
# ------------------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    stratify=y,
    random_state=42
)

print("\n--- Test Dataset ---")
print(f"Test rows: {len(X_test):,}")


# ------------------------------------------------------------
# 5. LOAD TRAINED XGBOOST MODEL
# ------------------------------------------------------------

model = XGBClassifier()

model.load_model(MODEL_PATH)

print("\nXGBoost model loaded successfully.")


# ------------------------------------------------------------
# 6. CALCULATE SHAP VALUES
# USING XGBOOST NATIVE CONTRIBUTIONS
# ------------------------------------------------------------

print(
    "\nCalculating SHAP values "
    "using XGBoost native contributions..."
)

# Convert test data to XGBoost DMatrix
dtest = xgb.DMatrix(X_test)

# pred_contribs=True returns feature contribution values.
#
# The final column represents the bias / base-value
# contribution, so it is removed below.

shap_values_with_bias = model.get_booster().predict(
    dtest,
    pred_contribs=True
)

# Remove the final bias column
shap_values = shap_values_with_bias[:, :-1]

print("SHAP calculation complete.")

print(
    f"SHAP matrix shape: {shap_values.shape}"
)


# ------------------------------------------------------------
# 7. SHAP SUMMARY BAR PLOT
# ------------------------------------------------------------

print("\nGenerating SHAP feature importance chart...")

plt.figure(figsize=(10, 7))

shap.summary_plot(
    shap_values,
    X_test,
    plot_type="bar",
    show=False,
    max_display=15
)

plt.title(
    "SHAP Feature Importance - SLA Breach Prediction",
    fontsize=14
)

plt.tight_layout()

summary_path = os.path.join(
    CHART_PATH,
    "12_shap_feature_importance.png"
)

plt.savefig(
    summary_path,
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print(
    f"Saved: {summary_path}"
)


# ------------------------------------------------------------
# 8. SHAP BEESWARM PLOT
# ------------------------------------------------------------

print("\nGenerating SHAP beeswarm plot...")

plt.figure(figsize=(10, 8))

shap.summary_plot(
    shap_values,
    X_test,
    show=False,
    max_display=15
)

plt.title(
    "SHAP Impact on SLA Breach Prediction",
    fontsize=14
)

plt.tight_layout()

beeswarm_path = os.path.join(
    CHART_PATH,
    "13_shap_beeswarm.png"
)

plt.savefig(
    beeswarm_path,
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print(
    f"Saved: {beeswarm_path}"
)


# ------------------------------------------------------------
# 9. CALCULATE MEAN ABSOLUTE SHAP VALUES
# ------------------------------------------------------------

mean_abs_shap = np.abs(shap_values).mean(axis=0)

shap_importance = pd.DataFrame({
    "feature": X_test.columns,
    "mean_abs_shap": mean_abs_shap
})

shap_importance = shap_importance.sort_values(
    "mean_abs_shap",
    ascending=False
)

shap_importance["rank"] = range(
    1,
    len(shap_importance) + 1
)


# ------------------------------------------------------------
# 10. SAVE SHAP IMPORTANCE CSV
# ------------------------------------------------------------

shap_csv_path = os.path.join(
    CHART_PATH,
    "shap_feature_importance.csv"
)

shap_importance.to_csv(
    shap_csv_path,
    index=False
)

print(
    f"Saved: {shap_csv_path}"
)


# ------------------------------------------------------------
# 11. DISPLAY TOP 15 FEATURES
# ------------------------------------------------------------

print("\n--- TOP 15 SHAP FEATURES ---")

print(
    shap_importance[
        [
            "rank",
            "feature",
            "mean_abs_shap"
        ]
    ]
    .head(15)
    .to_string(index=False)
)


# ------------------------------------------------------------
# 12. FINAL SUMMARY
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("SHAP ANALYSIS COMPLETE")
print("=" * 60)

print("\nGenerated files:")

print("- 12_shap_feature_importance.png")
print("- 13_shap_beeswarm.png")
print("- shap_feature_importance.csv")

print("\n" + "=" * 60)
