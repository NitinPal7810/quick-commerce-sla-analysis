# ============================================================
# 06. STAFFING SCENARIO SIMULATION
# Quick Commerce SLA Breach Analysis
# ============================================================

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import xgboost as xgb


# ============================================================
# 1. PATHS
# ============================================================

DATA_PATH = "outputs/ml_ready_dataset.csv"

MODEL_PATH = (
    "outputs/models/"
    "xgboost_sla_breach_model.json"
)

RESULTS_PATH = (
    "outputs/models/"
    "scenario_simulation_results.csv"
)

BREACH_CHART_PATH = (
    "outputs/charts/"
    "14_staffing_scenario_breach_rate.png"
)

AVOIDED_CHART_PATH = (
    "outputs/charts/"
    "15_estimated_breaches_avoided.png"
)


os.makedirs("outputs/models", exist_ok=True)
os.makedirs("outputs/charts", exist_ok=True)


# ============================================================
# 2. LOAD DATA
# ============================================================

print("=" * 60)
print("QUICK COMMERCE SLA - SCENARIO SIMULATION")
print("=" * 60)

df = pd.read_csv(DATA_PATH)

X = df.drop(columns=["sla_breached"])
y = df["sla_breached"]


print(f"\nDataset shape: {df.shape}")
print(f"Feature rows: {len(X):,}")
print(f"Feature columns: {X.shape[1]}")


# ============================================================
# 3. LOAD XGBOOST MODEL
# ============================================================

print("\nLoading XGBoost model...")

model = xgb.XGBClassifier()

model.load_model(MODEL_PATH)

print("XGBoost model loaded successfully.")


# ============================================================
# 4. RAW MODEL PREDICTIONS
# ============================================================

print("\nCalculating baseline breach probabilities...")

raw_probabilities = model.predict_proba(X)[:, 1]

raw_baseline_probability = raw_probabilities.mean()

actual_breach_rate = y.mean()

print(
    f"Raw model breach probability: "
    f"{raw_baseline_probability * 100:.2f}%"
)

print(
    f"Actual dataset breach rate: "
    f"{actual_breach_rate * 100:.2f}%"
)


# ============================================================
# 5. PROBABILITY CALIBRATION
# ============================================================
#
# XGBoost was trained with scale_pos_weight because the target
# is imbalanced.
#
# Therefore raw predicted probabilities are higher than the
# actual 10% breach prevalence.
#
# We scale the probabilities so that the baseline scenario
# matches the observed 10% breach rate.
#
# This is probability calibration for this simulated dataset.
# ============================================================

calibration_factor = (
    actual_breach_rate /
    raw_baseline_probability
)

calibrated_probabilities = (
    raw_probabilities *
    calibration_factor
)

calibrated_probabilities = np.clip(
    calibrated_probabilities,
    0,
    1
)

baseline_probability = (
    calibrated_probabilities.mean()
)

print(
    f"\nCalibration factor: "
    f"{calibration_factor:.4f}"
)

print(
    f"Calibrated baseline breach probability: "
    f"{baseline_probability * 100:.2f}%"
)


# ============================================================
# 6. STAFFING SCENARIO ASSUMPTION
# ============================================================
#
# Scenario assumption:
#
# Every 10% increase in staffing is modeled as producing
# a 5% RELATIVE reduction in breach probability.
#
# This is a scenario assumption, NOT a causal estimate.
#
# +10% staffing -> 5% relative breach reduction
# +20% staffing -> 10% relative breach reduction
# +30% staffing -> 15% relative breach reduction
#
# The purpose is to evaluate "what-if" staffing decisions.
# ============================================================

SCENARIOS = {
    "Baseline": 0,
    "Staffing +10%": 10,
    "Staffing +20%": 20,
    "Staffing +30%": 30
}

RELATIVE_REDUCTION_PER_10_PERCENT = 0.05


# ============================================================
# 7. RUN SCENARIOS
# ============================================================

print("\n" + "-" * 60)
print("RUNNING STAFFING SCENARIOS")
print("-" * 60)


scenario_results = []

total_orders = len(df)

for scenario_name, staffing_increase in SCENARIOS.items():

    # Number of 10% staffing increments
    staffing_steps = staffing_increase / 10

    # Relative reduction in breach probability
    relative_reduction = (
        staffing_steps *
        RELATIVE_REDUCTION_PER_10_PERCENT
    )

    # Baseline scenario
    if staffing_increase == 0:

        scenario_breach_probability = (
            baseline_probability
        )

    else:

        scenario_breach_probability = (
            baseline_probability *
            (1 - relative_reduction)
        )

    scenario_breach_probability = np.clip(
        scenario_breach_probability,
        0,
        1
    )

    # Estimated breach orders
    estimated_breach_orders = round(
        total_orders *
        scenario_breach_probability
    )

    # Baseline breach orders
    baseline_breach_orders = round(
        total_orders *
        baseline_probability
    )

    # Breaches avoided
    estimated_breaches_avoided = (
        baseline_breach_orders -
        estimated_breach_orders
    )

    # Relative breach reduction
    if baseline_breach_orders > 0:

        relative_breach_reduction = (
            estimated_breaches_avoided /
            baseline_breach_orders
        ) * 100

    else:

        relative_breach_reduction = 0


    print(f"\n{scenario_name}")

    print(
        f"  Staffing increase       : "
        f"{staffing_increase}%"
    )

    print(
        f"  Predicted breach rate   : "
        f"{scenario_breach_probability * 100:.2f}%"
    )

    print(
        f"  Absolute reduction      : "
        f"{(baseline_probability - scenario_breach_probability) * 100:.2f} "
        f"percentage points"
    )

    print(
        f"  Relative reduction      : "
        f"{relative_breach_reduction:.2f}%"
    )

    print(
        f"  Estimated breaches      : "
        f"{estimated_breach_orders:,}"
    )

    print(
        f"  Estimated breaches avoided: "
        f"{estimated_breaches_avoided:,}"
    )


    scenario_results.append({

        "scenario": scenario_name,

        "staffing_increase_pct":
            staffing_increase,

        "predicted_breach_rate_pct":
            round(
                scenario_breach_probability * 100,
                2
            ),

        "estimated_breach_orders":
            estimated_breach_orders,

        "estimated_breaches_avoided":
            estimated_breaches_avoided,

        "absolute_breach_reduction_pp":
            round(
                (
                    baseline_probability -
                    scenario_breach_probability
                ) * 100,
                2
            ),

        "relative_breach_reduction_pct":
            round(
                relative_breach_reduction,
                2
            )

    })


# ============================================================
# 8. CREATE RESULTS DATAFRAME
# ============================================================

results_df = pd.DataFrame(
    scenario_results
)


# ============================================================
# 9. SAVE RESULTS
# ============================================================

results_df.to_csv(
    RESULTS_PATH,
    index=False
)

print(
    "\nScenario results saved to:"
)

print(RESULTS_PATH)


# ============================================================
# 10. DISPLAY SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("SCENARIO SUMMARY")
print("=" * 60)

print(
    results_df.to_string(index=False)
)


# ============================================================
# 11. CHART 1
# Staffing vs Predicted Breach Rate
# ============================================================

print(
    "\nGenerating scenario breach-rate chart..."
)

plt.figure(figsize=(10, 6))

plt.plot(
    results_df["staffing_increase_pct"],
    results_df["predicted_breach_rate_pct"],
    marker="o",
    linewidth=2
)

plt.title(
    "Staffing Increase vs Predicted SLA Breach Rate"
)

plt.xlabel(
    "Staffing Increase (%)"
)

plt.ylabel(
    "Predicted SLA Breach Rate (%)"
)

plt.xticks(
    results_df["staffing_increase_pct"]
)

plt.grid(
    True,
    alpha=0.3
)

plt.tight_layout()

plt.savefig(
    BREACH_CHART_PATH,
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print(
    f"Saved: {BREACH_CHART_PATH}"
)


# ============================================================
# 12. CHART 2
# Estimated Breaches Avoided
# ============================================================

print(
    "\nGenerating avoided-breaches chart..."
)

plt.figure(figsize=(10, 6))

plt.bar(
    results_df["scenario"],
    results_df["estimated_breaches_avoided"]
)

plt.title(
    "Estimated SLA Breaches Avoided Under Staffing Scenarios"
)

plt.xlabel(
    "Staffing Scenario"
)

plt.ylabel(
    "Estimated Breaches Avoided"
)

plt.xticks(
    rotation=15
)

plt.grid(
    axis="y",
    alpha=0.3
)

plt.tight_layout()

plt.savefig(
    AVOIDED_CHART_PATH,
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print(
    f"Saved: {AVOIDED_CHART_PATH}"
)


# ============================================================
# 13. FINAL STATUS
# ============================================================

print("\n" + "=" * 60)
print("SCENARIO SIMULATION COMPLETE")
print("=" * 60)

print("\nGenerated files:")

print(
    "- outputs/models/"
    "scenario_simulation_results.csv"
)

print(
    "- outputs/charts/"
    "14_staffing_scenario_breach_rate.png"
)

print(
    "- outputs/charts/"
    "15_estimated_breaches_avoided.png"
)

print("\n" + "=" * 60)
