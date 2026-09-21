USE quick_commerce_sla;

-- ============================================================
-- 03. STORE OVERLOAD ANALYSIS
-- ============================================================

-- 1. Store-level SLA performance
SELECT
    store_id,
    zone,
    COUNT(*) AS total_orders,
    SUM(sla_breached) AS breached_orders,
    ROUND(
        100.0 * SUM(sla_breached) / COUNT(*),
        2
    ) AS breach_rate_pct,
    ROUND(AVG(store_utilization), 2) AS avg_store_utilization,
    ROUND(AVG(orders_in_queue), 2) AS avg_orders_in_queue,
    ROUND(AVG(dispatch_delay_min), 2) AS avg_dispatch_delay_min
FROM deliveries
GROUP BY store_id, zone
ORDER BY breach_rate_pct DESC;


-- 2. Identify overloaded stores
SELECT
    store_id,
    zone,
    COUNT(*) AS total_orders,
    ROUND(AVG(store_utilization), 2) AS avg_store_utilization,
    ROUND(AVG(orders_in_queue), 2) AS avg_queue_size,
    ROUND(
        100.0 * SUM(sla_breached) / COUNT(*),
        2
    ) AS breach_rate_pct
FROM deliveries
GROUP BY store_id, zone
HAVING AVG(store_utilization) >= 0.80
ORDER BY breach_rate_pct DESC;


-- 3. Store utilization bands
SELECT
    CASE
        WHEN utilization_rate < 0.60 THEN 'Low Utilization'
        WHEN utilization_rate < 0.80 THEN 'Medium Utilization'
        ELSE 'High Utilization'
    END AS utilization_band,
    COUNT(*) AS total_orders,
    SUM(sla_breached) AS breached_orders,
    ROUND(
        100.0 * SUM(sla_breached) / COUNT(*),
        2
    ) AS breach_rate_pct,
    ROUND(AVG(dispatch_delay_min), 2) AS avg_dispatch_delay_min
FROM deliveries
GROUP BY
    CASE
        WHEN utilization_rate < 0.60 THEN 'Low Utilization'
        WHEN utilization_rate < 0.80 THEN 'Medium Utilization'
        ELSE 'High Utilization'
    END
ORDER BY breach_rate_pct DESC;


-- 4. Queue pressure vs SLA breach
SELECT
    CASE
        WHEN queue_pressure < 0.50 THEN 'Low Queue Pressure'
        WHEN queue_pressure < 0.80 THEN 'Medium Queue Pressure'
        ELSE 'High Queue Pressure'
    END AS queue_pressure_band,
    COUNT(*) AS total_orders,
    SUM(sla_breached) AS breached_orders,
    ROUND(
        100.0 * SUM(sla_breached) / COUNT(*),
        2
    ) AS breach_rate_pct,
    ROUND(AVG(dispatch_delay_min), 2) AS avg_dispatch_delay_min
FROM deliveries
GROUP BY
    CASE
        WHEN queue_pressure < 0.50 THEN 'Low Queue Pressure'
        WHEN queue_pressure < 0.80 THEN 'Medium Queue Pressure'
        ELSE 'High Queue Pressure'
    END
ORDER BY breach_rate_pct DESC;

