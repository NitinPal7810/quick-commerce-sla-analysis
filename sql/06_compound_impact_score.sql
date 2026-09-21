USE quick_commerce_sla;

-- ============================================================
-- 06. COMPOUND IMPACT SCORE
-- Zone × Time Bucket × SLA Breach
-- ============================================================

-- Purpose:
-- Identify the highest-impact zone × time combinations
-- by balancing breach rate with order volume.

SELECT
    zone,
    zone_type,
    time_bucket,

    COUNT(*) AS total_orders,

    SUM(sla_breached) AS total_breached,

    ROUND(
        100.0 * SUM(sla_breached) / COUNT(*),
        2
    ) AS breach_pct,

    ROUND(
        AVG(store_utilization),
        3
    ) AS avg_utilization,

    ROUND(
        AVG(dispatch_delay_min),
        2
    ) AS avg_dispatch_delay_min,

    ROUND(
        AVG(rider_idle_time_before_dispatch),
        3
    ) AS avg_rider_idle_time,

    -- Impact score:
    -- Breach rate × LOG10(order volume)
    -- LOG10 reduces the dominance of very high-volume groups
    ROUND(
        (SUM(sla_breached) / COUNT(*))
        * LOG10(COUNT(*)),
        4
    ) AS breach_impact_score

FROM deliveries

GROUP BY
    zone,
    zone_type,
    time_bucket

-- Minimum volume threshold
HAVING COUNT(*) > 300

ORDER BY
    breach_impact_score DESC

LIMIT 10;
