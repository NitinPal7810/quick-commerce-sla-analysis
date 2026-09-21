# ============================================================
# 03. FEATURE ENGINEERING
# Quick Commerce SLA Breach Analysis
# ============================================================

import pandas as pd
import numpy as np
from pathlib import Path

# ============================================================
# 1. LOAD DATA
# ============================================================

DATA_PATH = "data/deliveries.csv"
OUTPUT_DIR = Path("outputs")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(
    DATA_PATH,
    parse_dates=["order_datetime", "order_date"]
)

print("=" * 60)
print("QUICK COMMERCE SLA - FEATURE ENGINEERING")
print("=" * 60)

print(f"\nOriginal dataset shape: {df.shape}")

# ============================================================
# 2. CREATE TIME FEATURES
# ============================================================

df["order_day"] = df["order_datetime"].dt.day

df["order_month"] = df["order_datetime"].dt.month

df["order_week"] = (
    df["order_datetime"]
    .dt.isocalendar()
    .week
    .astype(int)
)

# ============================================================
# 3. CREATE ORDER-PLACEMENT FEATURES
# ============================================================

# Orders per active rider
df["orders_per_rider"] = (
    df["orders_in_queue"]
    / df["riders_active"].replace(0, np.nan)
)

df["orders_per_rider"] = (
    df["orders_per_rider"]
    .fillna(0)
)

# Queue pressure relative to active riders
df["queue_per_rider"] = (
    df["orders_in_queue"]
    / df["riders_active"].replace(0, np.nan)
)

df["queue_per_rider"] = (
    df["queue_per_rider"]
    .fillna(0)
)

# Evening peak indicator
df["is_evening_peak"] = (
    df["time_bucket"] == "Evening Peak"
).astype(int)

# ============================================================
# 4. ML FEATURE SELECTION
# ============================================================
#
# IMPORTANT:
# Only features available at order placement are used.
#
# Excluded to prevent target leakage:
#
# delivery_time_min
# dispatch_delay_min
# dispatch_delay_ratio
# reorder_probability
# rider_idle_time_before_dispatch
#
# These variables are observed after or during the delivery
# process and should not be used to predict the SLA breach
# before dispatch.
# ============================================================

feature_columns = [
    "order_hour",
    "is_weekend",
    "is_peak_hour",
    "is_evening_peak",

    "zone",
    "zone_type",
    "store_id",

    "order_value_inr",
    "distance_km",
    "weather",

    "riders_active",
    "orders_in_queue",

    "store_utilization",
    "utilization_rate",
    "queue_pressure",
    "load_ratio",

    "orders_per_rider",
    "queue_per_rider"
]

target_column = "sla_breached"

ml_df = df[
    feature_columns + [target_column]
].copy()

# ============================================================
# 5. CATEGORICAL ENCODING
# ============================================================

categorical_columns = [
    "zone",
    "zone_type",
    "store_id",
    "weather"
]

ml_df = pd.get_dummies(
    ml_df,
    columns=categorical_columns,
    drop_first=False,
    dtype=int
)

# ============================================================
# 6. HANDLE MISSING / INFINITE VALUES
# ============================================================

ml_df = ml_df.replace(
    [np.inf, -np.inf],
    np.nan
)

ml_df = ml_df.fillna(0)

# ============================================================
# 7. VALIDATION
# ============================================================

print("\n--- Feature Engineering Summary ---")

print(
    f"Original rows       : {len(df):,}"
)

print(
    f"ML rows             : {len(ml_df):,}"
)

print(
    f"Original features   : {len(feature_columns)}"
)

print(
    f"Final ML features   : {ml_df.shape[1] - 1}"
)

print(
    f"Target column       : {target_column}"
)

print(
    f"Target breach rate  : "
    f"{ml_df[target_column].mean() * 100:.2f}%"
)

print(
    "\nMissing values:",
    ml_df.isnull().sum().sum()
)

print(
    "Infinite values:",
    np.isinf(
        ml_df.select_dtypes(include=np.number)
    ).sum().sum()
)

print(
    "Duplicate rows:",
    ml_df.duplicated().sum()
)

# ============================================================
# 8. TARGET DISTRIBUTION
# ============================================================

print("\n--- Target Distribution ---")

print(
    ml_df[target_column]
    .value_counts()
    .sort_index()
)

# ============================================================
# 9. SAVE ML DATASET
# ============================================================

output_path = (
    OUTPUT_DIR /
    "ml_ready_dataset.csv"
)

ml_df.to_csv(
    output_path,
    index=False
)

print(
    f"\nML dataset saved to:"
    f"\n{output_path}"
)

# ============================================================
# 10. FINAL STATUS
# ============================================================

print("\n" + "=" * 60)
print("FEATURE ENGINEERING COMPLETE")
print("=" * 60)