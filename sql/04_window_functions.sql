USE quick_commerce_sla;

-- ============================================================
-- 04. WINDOW FUNCTIONS
-- ============================================================

-- 1. Rank stores by SLA breach rate within each zone
SELECT
    store_id,
    zone,
    COUNT(*) AS total_orders,
    SUM(sla_breached) AS breached_orders,
    ROUND(
        100.0 * SUM(sla_breached) / COUNT(*),
        2
    ) AS breach_rate_pct,
    RANK() OVER (
        PARTITION BY zone
        ORDER BY
            100.0 * SUM(sla_breached) / COUNT(*) DESC
    ) AS zone_breach_rank
FROM deliveries
GROUP BY store_id, zone
ORDER BY zone, zone_breach_rank;


-- 2. Rank zones by overall SLA breach rate
WITH zone_metrics AS (
    SELECT
        zone,
        COUNT(*) AS total_orders,
        SUM(sla_breached) AS breached_orders,
        100.0 * SUM(sla_breached) / COUNT(*) AS breach_rate
    FROM deliveries
    GROUP BY zone
)
SELECT
    zone,
    total_orders,
    breached_orders,
    ROUND(breach_rate, 2) AS breach_rate_pct,
    RANK() OVER (
        ORDER BY breach_rate DESC
    ) AS zone_rank
FROM zone_metrics
ORDER BY zone_rank;


-- 3. Compare each store's breach rate with its zone average
WITH store_metrics AS (
    SELECT
        store_id,
        zone,
        COUNT(*) AS total_orders,
        SUM(sla_breached) AS breached_orders,
        100.0 * SUM(sla_breached) / COUNT(*) AS breach_rate
    FROM deliveries
    GROUP BY store_id, zone
)
SELECT
    store_id,
    zone,
    total_orders,
    breached_orders,
    ROUND(breach_rate, 2) AS breach_rate_pct,
    ROUND(
        AVG(breach_rate) OVER (PARTITION BY zone),
        2
    ) AS zone_avg_breach_rate_pct,
    ROUND(
        breach_rate -
        AVG(breach_rate) OVER (PARTITION BY zone),
        2
    ) AS variance_vs_zone_avg_pct
FROM store_metrics
ORDER BY variance_vs_zone_avg_pct DESC;


-- 4. Hourly breach rate with previous-hour comparison
WITH hourly_metrics AS (
    SELECT
        order_hour,
        COUNT(*) AS total_orders,
        SUM(sla_breached) AS breached_orders,
        100.0 * SUM(sla_breached) / COUNT(*) AS breach_rate
    FROM deliveries
    GROUP BY order_hour
)
SELECT
    order_hour,
    total_orders,
    breached_orders,
    ROUND(breach_rate, 2) AS breach_rate_pct,
    ROUND(
        LAG(breach_rate) OVER (ORDER BY order_hour),
        2
    ) AS previous_hour_breach_rate_pct,
    ROUND(
        breach_rate -
        LAG(breach_rate) OVER (ORDER BY order_hour),
        2
    ) AS change_vs_previous_hour_pct
FROM hourly_metrics
ORDER BY order_hour;
