import numpy as np
import pandas as pd

# ============================================================
# QUICK COMMERCE SLA BREACH ANALYTICS
# Simulated Dataset Generator
# ============================================================

np.random.seed(42)

# ------------------------------------------------------------
# 1. BASIC SETTINGS
# ------------------------------------------------------------

N_ORDERS = 200_000

zones = [f"Zone_{i:02d}" for i in range(1, 21)]
stores = [f"Store_{i:02d}" for i in range(1, 41)]

# Zone classification
zone_types = {
    zone: np.random.choice(
        ["High-Density", "Medium-Density", "Low-Density"],
        p=[0.40, 0.40, 0.20]
    )
    for zone in zones
}

# ------------------------------------------------------------
# 2. ORDER DATETIME
# ------------------------------------------------------------

order_id = np.arange(1, N_ORDERS + 1)

start_date = pd.Timestamp("2026-01-01")
end_date = pd.Timestamp("2026-03-31 23:59:59")

random_seconds = np.random.randint(
    0,
    int((end_date - start_date).total_seconds()),
    N_ORDERS
)

order_datetime = (
    start_date +
    pd.to_timedelta(random_seconds, unit="s")
)

order_datetime = pd.to_datetime(order_datetime)

order_date = order_datetime.date
order_hour = order_datetime.hour
day_of_week = order_datetime.day_name()

# Weekend flag
is_weekend = np.where(
    order_datetime.dayofweek >= 5,
    1,
    0
)

# ------------------------------------------------------------
# 3. TIME BUCKET
# ------------------------------------------------------------

def get_time_bucket(hour):

    if 6 <= hour < 10:
        return "Morning"

    elif 10 <= hour < 13:
        return "Late Morning"

    elif 13 <= hour < 17:
        return "Afternoon"

    elif 17 <= hour < 22:
        return "Evening Peak"

    else:
        return "Night"


time_bucket = [
    get_time_bucket(hour)
    for hour in order_hour
]

# Peak lunch + evening hours
is_peak_hour = np.where(
    (
        ((order_hour >= 12) & (order_hour <= 14))
        |
        ((order_hour >= 18) & (order_hour <= 21))
    ),
    1,
    0
)

# ------------------------------------------------------------
# 4. ZONE + STORE
# ------------------------------------------------------------

zone = np.random.choice(
    zones,
    size=N_ORDERS
)

store_id = np.random.choice(
    stores,
    size=N_ORDERS
)

zone_type = np.array([
    zone_types[z]
    for z in zone
])

# ------------------------------------------------------------
# 5. ORDER VALUE
# ------------------------------------------------------------

order_value_inr = np.random.normal(
    loc=805,
    scale=250,
    size=N_ORDERS
)

order_value_inr = np.clip(
    order_value_inr,
    150,
    2000
)

# ------------------------------------------------------------
# 6. DELIVERY DISTANCE
# ------------------------------------------------------------

distance_km = np.random.gamma(
    shape=2.0,
    scale=1.2,
    size=N_ORDERS
)

distance_km = np.clip(
    distance_km,
    0.3,
    8
)

# ------------------------------------------------------------
# 7. STORE UTILIZATION
# ------------------------------------------------------------

base_utilization = np.random.normal(
    loc=0.58,
    scale=0.12,
    size=N_ORDERS
)

peak_effect = (
    is_peak_hour
    *
    np.random.normal(
        loc=0.12,
        scale=0.04,
        size=N_ORDERS
    )
)

weekend_effect = (
    is_weekend
    *
    np.random.normal(
        loc=0.03,
        scale=0.015,
        size=N_ORDERS
    )
)

store_utilization = (
    base_utilization
    + peak_effect
    + weekend_effect
)

store_utilization = np.clip(
    store_utilization,
    0.20,
    0.95
)

utilization_rate = store_utilization

# ------------------------------------------------------------
# 8. ACTIVE RIDERS
# ------------------------------------------------------------

riders_active = np.random.poisson(
    lam=np.where(
        is_peak_hour == 1,
        9,
        11
    )
)

riders_active = np.clip(
    riders_active,
    3,
    20
)

# ------------------------------------------------------------
# 9. ORDERS IN QUEUE
# ------------------------------------------------------------

queue_base = np.random.poisson(
    lam=np.where(
        is_peak_hour == 1,
        5,
        2
    )
)

orders_in_queue = (
    queue_base
    +
    (
        store_utilization > 0.78
    ).astype(int)
    *
    np.random.randint(
        1,
        5,
        N_ORDERS
    )
)

orders_in_queue = np.clip(
    orders_in_queue,
    0,
    25
)

# ------------------------------------------------------------
# 10. RIDER IDLE TIME
# ------------------------------------------------------------

rider_idle_time_before_dispatch = np.maximum(
    0,
    np.random.normal(
        loc=7,
        scale=2.5,
        size=N_ORDERS
    )
    -
    is_peak_hour
    *
    np.random.normal(
        loc=1.5,
        scale=0.8,
        size=N_ORDERS
    )
)

# ------------------------------------------------------------
# 11. WEATHER
# ------------------------------------------------------------

weather = np.random.choice(
    ["Clear", "Cloudy", "Rain"],
    size=N_ORDERS,
    p=[0.65, 0.25, 0.10]
)

rain_effect = np.where(
    weather == "Rain",
    np.random.uniform(
        0.8,
        2.5,
        N_ORDERS
    ),
    0
)

# ------------------------------------------------------------
# 12. QUEUE PRESSURE
# ------------------------------------------------------------

queue_pressure = (
    orders_in_queue
    /
    np.maximum(
        riders_active,
        1
    )
)

# ------------------------------------------------------------
# 13. LOAD RATIO
# ------------------------------------------------------------

load_ratio = (
    orders_in_queue
    /
    np.maximum(
        riders_active * 2,
        1
    )
)

# ------------------------------------------------------------
# 14. RAW DISPATCH DELAY
# ------------------------------------------------------------

raw_dispatch_delay = (

    0.8

    + store_utilization * 2.2

    + orders_in_queue * 0.18

    + np.maximum(
        10 - riders_active,
        0
    ) * 0.12

    + distance_km * 0.12

    + is_peak_hour * 0.55

    + rain_effect

    + np.random.normal(
        0,
        0.65,
        N_ORDERS
    )
)

raw_dispatch_delay = np.clip(
    raw_dispatch_delay,
    0.3,
    None
)

# ------------------------------------------------------------
# 15. RAW DELIVERY TIME
# ------------------------------------------------------------

raw_delivery_time = (

    4.2

    + raw_dispatch_delay

    + distance_km * 0.38

    + np.random.normal(
        0,
        0.75,
        N_ORDERS
    )
)

raw_delivery_time = np.clip(
    raw_delivery_time,
    3.5,
    None
)

# ------------------------------------------------------------
# 16. CALIBRATE DELIVERY TIME
# ------------------------------------------------------------
# We calibrate the simulated operation so approximately
# 10% of orders breach a 10-minute SLA.
#
# This keeps the dataset useful for operational analysis
# instead of making almost every order a breach.

sla_target_min = 10

target_breach_rate = 0.10

raw_90th_percentile = np.quantile(
    raw_delivery_time,
    1 - target_breach_rate
)

delivery_scale = (
    sla_target_min /
    raw_90th_percentile
)

delivery_time_min = (
    raw_delivery_time *
    delivery_scale
)

delivery_time_min = np.clip(
    delivery_time_min,
    3.5,
    25
)

# ------------------------------------------------------------
# 17. DISPATCH DELAY
# ------------------------------------------------------------

dispatch_delay_min = (
    raw_dispatch_delay *
    delivery_scale
)

dispatch_delay_min = np.clip(
    dispatch_delay_min,
    0.3,
    10
)

# ------------------------------------------------------------
# 18. SLA BREACH
# ------------------------------------------------------------

sla_breached = (
    delivery_time_min
    >
    sla_target_min
).astype(int)

# ------------------------------------------------------------
# 19. REORDER PROBABILITY
# ------------------------------------------------------------
# A breached order receives a modeled 0.20 probability
# penalty relative to the normal base probability.

reorder_probability = (

    0.72

    - 0.20 * sla_breached

    - 0.012
    *
    np.maximum(
        delivery_time_min - 10,
        0
    )

    + np.random.normal(
        0,
        0.02,
        N_ORDERS
    )
)

reorder_probability = np.clip(
    reorder_probability,
    0.05,
    0.90
)

# ------------------------------------------------------------
# 20. CREATE DATAFRAME
# ------------------------------------------------------------

df = pd.DataFrame({

    "order_id": order_id,

    "order_datetime": order_datetime,

    "order_date": order_date,

    "day_of_week": day_of_week,

    "order_hour": order_hour,

    "time_bucket": time_bucket,

    "is_weekend": is_weekend,

    "is_peak_hour": is_peak_hour,

    "zone": zone,

    "zone_type": zone_type,

    "store_id": store_id,

    "order_value_inr": np.round(
        order_value_inr,
        2
    ),

    "distance_km": np.round(
        distance_km,
        2
    ),

    "weather": weather,

    "riders_active": riders_active,

    "orders_in_queue": orders_in_queue,

    "store_utilization": np.round(
        store_utilization,
        3
    ),

    "utilization_rate": np.round(
        utilization_rate,
        3
    ),

    "queue_pressure": np.round(
        queue_pressure,
        3
    ),

    "load_ratio": np.round(
        load_ratio,
        3
    ),

    "rider_idle_time_before_dispatch": np.round(
        rider_idle_time_before_dispatch,
        2
    ),

    "dispatch_delay_min": np.round(
        dispatch_delay_min,
        2
    ),

    "delivery_time_min": np.round(
        delivery_time_min,
        2
    ),

    "sla_target_min": sla_target_min,

    "sla_breached": sla_breached,

    "reorder_probability": np.round(
        reorder_probability,
        4
    )
})

# ------------------------------------------------------------
# 21. SORT DATA
# ------------------------------------------------------------

df = df.sort_values(
    "order_datetime"
).reset_index(
    drop=True
)

# ------------------------------------------------------------
# 22. REVENUE AT RISK
# ------------------------------------------------------------
# Modeled revenue at risk:
#
# Breached Orders
# × 0.20 reorder probability penalty
# × Average Order Value

breached_orders = df["sla_breached"].sum()

average_order_value = (
    df["order_value_inr"].mean()
)

revenue_at_risk = (
    breached_orders
    * 0.20
    * average_order_value
)

# ------------------------------------------------------------
# 23. SAVE DATASET
# ------------------------------------------------------------

output_path = "data/deliveries.csv"

df.to_csv(
    output_path,
    index=False
)

# ------------------------------------------------------------
# 24. SUMMARY
# ------------------------------------------------------------

print("=" * 65)

print(
    "QUICK COMMERCE SLA DATASET GENERATED"
)

print("=" * 65)

print(
    f"Total orders           : {len(df):,}"
)

print(
    f"Total zones            : {df['zone'].nunique()}"
)

print(
    f"Total stores           : {df['store_id'].nunique()}"
)

print(
    f"SLA breach orders      : {breached_orders:,}"
)

print(
    f"SLA breach rate        : "
    f"{df['sla_breached'].mean() * 100:.2f}%"
)

print(
    f"Average order value    : "
    f"₹{average_order_value:.2f}"
)

print(
    f"Average delivery time  : "
    f"{df['delivery_time_min'].mean():.2f} min"
)

print(
    f"Average dispatch delay : "
    f"{df['dispatch_delay_min'].mean():.2f} min"
)

print(
    f"Modeled revenue risk   : "
    f"₹{revenue_at_risk:,.2f}"
)

print()

print("Dataset columns:")

print(
    df.columns.tolist()
)

print()

print("First 5 rows:")

print(
    df.head()
)

print()

print(
    "Dataset saved to:"
)

print(
    output_path
)

print("=" * 65)




