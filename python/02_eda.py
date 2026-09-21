# ============================================================
# 02. EXPLORATORY DATA ANALYSIS
# Quick Commerce SLA Breach Analysis
# ============================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# ============================================================
# 1. LOAD DATA
# ============================================================

DATA_PATH = "data/deliveries.csv"
OUTPUT_DIR = Path("outputs/charts")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(
    DATA_PATH,
    parse_dates=["order_datetime", "order_date"]
)

print("=" * 60)
print("QUICK COMMERCE SLA - EXPLORATORY DATA ANALYSIS")
print("=" * 60)

print(f"\nDataset shape: {df.shape}")

# ============================================================
# 2. BASIC SLA SUMMARY
# ============================================================

total_orders = len(df)
breached_orders = df["sla_breached"].sum()
breach_rate = df["sla_breached"].mean() * 100

print("\n--- SLA Summary ---")

print(f"Total orders       : {total_orders:,}")
print(f"Breached orders    : {breached_orders:,}")
print(f"SLA breach rate    : {breach_rate:.2f}%")

print(
    f"Average delivery   : "
    f"{df['delivery_time_min'].mean():.2f} min"
)

print(
    f"Average dispatch   : "
    f"{df['dispatch_delay_min'].mean():.2f} min"
)

# ============================================================
# 3. SLA BREACH DISTRIBUTION
# ============================================================

breach_counts = (
    df["sla_breached"]
    .value_counts()
    .sort_index()
)

labels = ["SLA Met", "SLA Breached"]

plt.figure(figsize=(8, 5))

plt.bar(
    labels,
    [
        breach_counts.get(0, 0),
        breach_counts.get(1, 0)
    ]
)

plt.title("SLA Breach Distribution")
plt.xlabel("SLA Status")
plt.ylabel("Number of Orders")

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "01_sla_breach_distribution.png",
    dpi=150
)

plt.close()

# ============================================================
# 4. BREACH RATE BY TIME BUCKET
# ============================================================

# Actual categories present in the dataset
time_order = [
    "Morning",
    "Late Morning",
    "Afternoon",
    "Evening Peak",
    "Night"
]

time_analysis = (
    df.groupby(
        "time_bucket",
        observed=True
    )
    .agg(
        total_orders=("order_id", "count"),
        breached_orders=("sla_breached", "sum"),
        avg_dispatch_delay=("dispatch_delay_min", "mean")
    )
)

time_analysis["breach_rate_pct"] = (
    time_analysis["breached_orders"]
    / time_analysis["total_orders"]
    * 100
)

time_analysis = (
    time_analysis
    .reindex(time_order)
    .dropna()
)

print("\n--- Breach Rate by Time Bucket ---")

print(
    time_analysis[
        [
            "total_orders",
            "breached_orders",
            "breach_rate_pct",
            "avg_dispatch_delay"
        ]
    ].round(2)
)

plt.figure(figsize=(10, 5))

plt.bar(
    time_analysis.index,
    time_analysis["breach_rate_pct"]
)

plt.title("SLA Breach Rate by Time Bucket")
plt.xlabel("Time Bucket")
plt.ylabel("Breach Rate (%)")

plt.xticks(rotation=15)

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "02_breach_rate_by_time_bucket.png",
    dpi=150
)

plt.close()

# ============================================================
# 5. BREACH RATE BY ZONE
# ============================================================

zone_analysis = (
    df.groupby(
        ["zone", "zone_type"],
        observed=True
    )
    .agg(
        total_orders=("order_id", "count"),
        breached_orders=("sla_breached", "sum"),
        avg_utilization=("store_utilization", "mean"),
        avg_queue=("orders_in_queue", "mean"),
        avg_dispatch_delay=("dispatch_delay_min", "mean")
    )
)

zone_analysis["breach_rate_pct"] = (
    zone_analysis["breached_orders"]
    / zone_analysis["total_orders"]
    * 100
)

zone_analysis = zone_analysis.sort_values(
    "breach_rate_pct",
    ascending=False
)

print("\n--- Top 10 Zones by SLA Breach Rate ---")

print(
    zone_analysis[
        [
            "total_orders",
            "breached_orders",
            "breach_rate_pct",
            "avg_utilization",
            "avg_queue",
            "avg_dispatch_delay"
        ]
    ]
    .head(10)
    .round(2)
)

top_zones = zone_analysis.head(10)

plt.figure(figsize=(10, 6))

plt.barh(
    top_zones.index.get_level_values("zone")[::-1],
    top_zones["breach_rate_pct"][::-1]
)

plt.title("Top 10 Zones by SLA Breach Rate")
plt.xlabel("Breach Rate (%)")
plt.ylabel("Zone")

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "03_top_zones_breach_rate.png",
    dpi=150
)

plt.close()

# ============================================================
# 6. QUEUE PRESSURE VS SLA BREACH
# ============================================================

queue_band = pd.cut(
    df["queue_pressure"],
    bins=[-np.inf, 0.50, 0.80, np.inf],
    labels=[
        "Low Queue Pressure",
        "Medium Queue Pressure",
        "High Queue Pressure"
    ]
)

queue_analysis = (
    df.assign(queue_pressure_band=queue_band)
    .groupby(
        "queue_pressure_band",
        observed=True
    )
    .agg(
        total_orders=("order_id", "count"),
        breached_orders=("sla_breached", "sum"),
        avg_dispatch_delay=("dispatch_delay_min", "mean")
    )
)

queue_analysis["breach_rate_pct"] = (
    queue_analysis["breached_orders"]
    / queue_analysis["total_orders"]
    * 100
)

print("\n--- Queue Pressure Analysis ---")

print(
    queue_analysis.round(2)
)

plt.figure(figsize=(9, 5))

plt.bar(
    queue_analysis.index.astype(str),
    queue_analysis["breach_rate_pct"]
)

plt.title("SLA Breach Rate by Queue Pressure")
plt.xlabel("Queue Pressure")
plt.ylabel("Breach Rate (%)")

plt.xticks(rotation=15)

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "04_queue_pressure_vs_breach.png",
    dpi=150
)

plt.close()

# ============================================================
# 7. STORE UTILIZATION VS SLA BREACH
# ============================================================

utilization_band = pd.cut(
    df["utilization_rate"],
    bins=[-np.inf, 0.60, 0.80, np.inf],
    labels=[
        "Low Utilization",
        "Medium Utilization",
        "High Utilization"
    ]
)

utilization_analysis = (
    df.assign(utilization_band=utilization_band)
    .groupby(
        "utilization_band",
        observed=True
    )
    .agg(
        total_orders=("order_id", "count"),
        breached_orders=("sla_breached", "sum"),
        avg_dispatch_delay=("dispatch_delay_min", "mean")
    )
)

utilization_analysis["breach_rate_pct"] = (
    utilization_analysis["breached_orders"]
    / utilization_analysis["total_orders"]
    * 100
)

print("\n--- Store Utilization Analysis ---")

print(
    utilization_analysis.round(2)
)

plt.figure(figsize=(9, 5))

plt.bar(
    utilization_analysis.index.astype(str),
    utilization_analysis["breach_rate_pct"]
)

plt.title("SLA Breach Rate by Store Utilization")
plt.xlabel("Utilization Band")
plt.ylabel("Breach Rate (%)")

plt.xticks(rotation=15)

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "05_store_utilization_vs_breach.png",
    dpi=150
)

plt.close()

# ============================================================
# 8. RIDER IDLE TIME VS DISPATCH DELAY
# ============================================================

sample_df = df.sample(
    min(10000, len(df)),
    random_state=42
)

plt.figure(figsize=(9, 6))

plt.scatter(
    sample_df["rider_idle_time_before_dispatch"],
    sample_df["dispatch_delay_min"],
    alpha=0.25,
    s=12
)

plt.title(
    "Rider Idle Time Before Dispatch vs Dispatch Delay"
)

plt.xlabel(
    "Rider Idle Time Before Dispatch (min)"
)

plt.ylabel(
    "Dispatch Delay (min)"
)

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "06_rider_idle_vs_dispatch_delay.png",
    dpi=150
)

plt.close()

# ============================================================
# 9. DISPATCH DELAY VS DELIVERY TIME
# ============================================================

plt.figure(figsize=(9, 6))

plt.scatter(
    sample_df["dispatch_delay_min"],
    sample_df["delivery_time_min"],
    alpha=0.25,
    s=12
)

plt.axhline(
    df["sla_target_min"].iloc[0],
    linestyle="--",
    label="SLA Target"
)

plt.title(
    "Dispatch Delay vs Delivery Time"
)

plt.xlabel(
    "Dispatch Delay (min)"
)

plt.ylabel(
    "Delivery Time (min)"
)

plt.legend()

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "07_dispatch_delay_vs_delivery_time.png",
    dpi=150
)

plt.close()

# ============================================================
# 10. CORRELATION ANALYSIS
# ============================================================

numeric_columns = [
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
    "sla_breached",
    "reorder_probability"
]

correlation_matrix = (
    df[numeric_columns]
    .corr()
)

print("\n--- Correlation with SLA Breach ---")

sla_correlation = (
    correlation_matrix["sla_breached"]
    .sort_values(ascending=False)
)

print(
    sla_correlation.round(3)
)

plt.figure(figsize=(11, 9))

plt.imshow(
    correlation_matrix,
    aspect="auto"
)

plt.colorbar(
    label="Correlation"
)

plt.xticks(
    range(len(numeric_columns)),
    numeric_columns,
    rotation=90
)

plt.yticks(
    range(len(numeric_columns)),
    numeric_columns
)

plt.title("Correlation Matrix - Operational SLA Drivers")

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "08_correlation_matrix.png",
    dpi=150
)

plt.close()

# ============================================================
# 11. SAVE ANALYSIS TABLES
# ============================================================

zone_analysis.reset_index().to_csv(
    OUTPUT_DIR / "zone_analysis.csv",
    index=False
)

time_analysis.reset_index().to_csv(
    OUTPUT_DIR / "time_bucket_analysis.csv",
    index=False
)

queue_analysis.reset_index().to_csv(
    OUTPUT_DIR / "queue_pressure_analysis.csv",
    index=False
)

utilization_analysis.reset_index().to_csv(
    OUTPUT_DIR / "utilization_analysis.csv",
    index=False
)

# ============================================================
# 12. FINAL STATUS
# ============================================================

print("\n" + "=" * 60)
print("EDA COMPLETE")
print("=" * 60)

print("\nCharts saved to:")
print("outputs/charts/")

print("\nGenerated files:")

for file in sorted(OUTPUT_DIR.iterdir()):
    print(f"  - {file.name}")

print("\n" + "=" * 60)