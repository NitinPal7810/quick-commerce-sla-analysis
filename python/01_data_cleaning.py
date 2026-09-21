# ============================================================
# 01. DATA CLEANING & QUALITY CHECKS
# Quick Commerce SLA Breach Analysis
# ============================================================

import pandas as pd
import numpy as np

# ============================================================
# 1. LOAD DATA
# ============================================================

DATA_PATH = "data/deliveries.csv"

dtype_map = {
    "order_id": "int32",
    "order_hour": "int8",
    "is_weekend": "int8",
    "is_peak_hour": "int8",
    "riders_active": "int16",
    "orders_in_queue": "int16",
    "sla_target_min": "int8",
    "sla_breached": "int8"
}

parse_dates = [
    "order_datetime",
    "order_date"
]

df = pd.read_csv(
    DATA_PATH,
    dtype=dtype_map,
    parse_dates=parse_dates
)

# ============================================================
# 2. BASIC DATASET INFORMATION
# ============================================================

print("=" * 60)
print("QUICK COMMERCE SLA - DATA QUALITY CHECK")
print("=" * 60)

print(f"\nShape: {df.shape}")

print(
    f"Memory Usage: "
    f"{df.memory_usage(deep=True).sum() / 1e6:.2f} MB"
)

print("\n--- Columns ---")
print(df.columns.tolist())

print("\n--- Data Types ---")
print(df.dtypes)

# ============================================================
# 3. NULL CHECK
# ============================================================

null_report = df.isnull().sum()

print("\n--- Null Report ---")
print(null_report[null_report > 0])
print("\nNo nulls:", null_report.sum() == 0)

# ============================================================
# 4. DUPLICATE CHECK
# ============================================================

duplicate_orders = df["order_id"].duplicated().sum()

print("\n--- Duplicate Check ---")
print("Duplicate order IDs:", duplicate_orders)

# ============================================================
# 5. SANITY CHECKS
# ============================================================

print("\n--- Sanity Checks ---")

print(
    "Negative delivery_time_min:",
    (df["delivery_time_min"] < 0).sum()
)

print(
    "Negative dispatch_delay_min:",
    (df["dispatch_delay_min"] < 0).sum()
)

print(
    "Invalid order_hour:",
    (
        (df["order_hour"] < 0) |
        (df["order_hour"] > 23)
    ).sum()
)

print(
    "Invalid sla_target_min:",
    (df["sla_target_min"] <= 0).sum()
)

print(
    "Invalid sla_breached values:",
    (~df["sla_breached"].isin([0, 1])).sum()
)

print(
    "Invalid is_weekend values:",
    (~df["is_weekend"].isin([0, 1])).sum()
)

print(
    "Invalid is_peak_hour values:",
    (~df["is_peak_hour"].isin([0, 1])).sum()
)

print(
    "Store utilization > 2.0:",
    (df["store_utilization"] > 2.0).sum()
)

# ============================================================
# 6. SLA LOGIC VALIDATION
# ============================================================

# The CSV stores delivery time rounded to 2 decimal places.
# Therefore, rows exactly at the SLA boundary can differ from
# the original unrounded calculation used during generation.
#
# We validate only rows clearly above or below the SLA target.

tolerance = 0.005

clearly_breached = (
    df["delivery_time_min"] >
    df["sla_target_min"] + tolerance
)

clearly_successful = (
    df["delivery_time_min"] <
    df["sla_target_min"] - tolerance
)

boundary_cases = ~(
    clearly_breached |
    clearly_successful
)

validation_mask = clearly_breached | clearly_successful

expected_breach = pd.Series(
    np.nan,
    index=df.index
)

expected_breach.loc[clearly_breached] = 1
expected_breach.loc[clearly_successful] = 0

sla_mismatch = (
    expected_breach.loc[validation_mask].astype(int)
    != df.loc[validation_mask, "sla_breached"]
).sum()

print("\n--- SLA Logic Validation ---")

print(
    "Clearly validated rows:",
    validation_mask.sum()
)

print(
    "Boundary cases excluded:",
    boundary_cases.sum()
)

print(
    "SLA breach flag mismatches:",
    sla_mismatch
)

# ============================================================
# 7. DATASET SUMMARY
# ============================================================

print("\n--- Dataset Summary ---")

print(f"Total orders          : {len(df):,}")
print(f"Total zones           : {df['zone'].nunique()}")
print(f"Total stores          : {df['store_id'].nunique()}")
print(f"SLA breach orders     : {df['sla_breached'].sum():,}")

print(
    f"SLA breach rate       : "
    f"{df['sla_breached'].mean() * 100:.2f}%"
)

print(
    f"Average order value   : "
    f"₹{df['order_value_inr'].mean():.2f}"
)

print(
    f"Average delivery time : "
    f"{df['delivery_time_min'].mean():.2f} min"
)

print(
    f"Average dispatch delay: "
    f"{df['dispatch_delay_min'].mean():.2f} min"
)

# ============================================================
# 8. DESCRIPTIVE STATISTICS
# ============================================================

print("\n--- Numerical Summary ---")

print(
    df[
        [
            "order_value_inr",
            "distance_km",
            "riders_active",
            "orders_in_queue",
            "store_utilization",
            "utilization_rate",
            "queue_pressure",
            "load_ratio",
            "rider_idle_time_before_dispatch",
            "dispatch_delay_min",
            "delivery_time_min",
            "reorder_probability"
        ]
    ].describe().round(2)
)

# ============================================================
# 9. FINAL STATUS
# ============================================================

print("\n" + "=" * 60)
print("DATA QUALITY CHECK COMPLETE")
print("=" * 60)
