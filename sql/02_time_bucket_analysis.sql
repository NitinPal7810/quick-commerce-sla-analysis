USE quick_commerce_sla;

-- ============================================================
-- 02. TIME BUCKET ANALYSIS
-- ============================================================

-- 1. SLA performance by time bucket
SELECT
    time_bucket,
    COUNT(*) AS total_orders,
    SUM(sla_breached) AS breached_orders,
    ROUND(
        100.0 * SUM(sla_breached) / COUNT(*),
        2
    ) AS breach_rate_pct,
    ROUND(AVG(dispatch_delay_min), 2) AS avg_dispatch_delay_min,
    ROUND(AVG(delivery_time_min), 2) AS avg_delivery_time_min
FROM deliveries
GROUP BY time_bucket
ORDER BY breach_rate_pct DESC;


-- 2. Hour-wise SLA performance
SELECT
    order_hour,
    COUNT(*) AS total_orders,
    SUM(sla_breached) AS breached_orders,
    ROUND(
        100.0 * SUM(sla_breached) / COUNT(*),
        2
    ) AS breach_rate_pct,
    ROUND(AVG(dispatch_delay_min), 2) AS avg_dispatch_delay_min
FROM deliveries
GROUP BY order_hour
ORDER BY order_hour;


-- 3. Peak vs non-peak performance
SELECT
    CASE
        WHEN is_peak_hour = 1 THEN 'Peak Hour'
        ELSE 'Non-Peak Hour'
    END AS period_type,
    COUNT(*) AS total_orders,
    SUM(sla_breached) AS breached_orders,
    ROUND(
        100.0 * SUM(sla_breached) / COUNT(*),
        2
    ) AS breach_rate_pct,
    ROUND(AVG(dispatch_delay_min), 2) AS avg_dispatch_delay_min
FROM deliveries
GROUP BY is_peak_hour
ORDER BY breach_rate_pct DESC;


-- 4. Weekday vs weekend performance
SELECT
    CASE
        WHEN is_weekend = 1 THEN 'Weekend'
        ELSE 'Weekday'
    END AS day_type,
    COUNT(*) AS total_orders,
    SUM(sla_breached) AS breached_orders,
    ROUND(
        100.0 * SUM(sla_breached) / COUNT(*),
        2
    ) AS breach_rate_pct,
    ROUND(AVG(delivery_time_min), 2) AS avg_delivery_time_min
FROM deliveries
GROUP BY is_weekend
ORDER BY breach_rate_pct DESC;

