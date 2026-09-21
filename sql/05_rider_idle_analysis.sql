USE quick_commerce_sla;

-- ============================================================
-- 05. RIDER IDLE / PRE-DEPLOYMENT ANALYSIS
-- ============================================================

-- 1. Rider idle time and SLA performance by zone and hour
SELECT
    zone,
    zone_type,
    order_hour,
    COUNT(*) AS order_count,
    ROUND(
        AVG(rider_idle_time_before_dispatch),
        3
    ) AS avg_idle_time,
    ROUND(
        AVG(riders_active),
        1
    ) AS avg_riders_active,
    ROUND(
        100.0 * SUM(sla_breached) / COUNT(*),
        2
    ) AS breach_rate_pct,
    CASE
        WHEN order_hour BETWEEN 15 AND 17
             AND AVG(rider_idle_time_before_dispatch) > 2.5
        THEN 'PRE-DEPLOY SIGNAL'
        ELSE 'Normal'
    END AS deployment_flag
FROM deliveries
GROUP BY
    zone,
    zone_type,
    order_hour
ORDER BY
    zone,
    order_hour;


-- 2. Identify zones with high pre-peak rider idle time
SELECT
    zone,
    zone_type,
    ROUND(
        AVG(
            CASE
                WHEN order_hour BETWEEN 15 AND 17
                THEN rider_idle_time_before_dispatch
            END
        ),
        3
    ) AS pre_peak_idle,
    ROUND(
        AVG(
            CASE
                WHEN order_hour BETWEEN 19 AND 21
                THEN sla_breached * 100.0
            END
        ),
        2
    ) AS peak_breach_pct
FROM deliveries
GROUP BY
    zone,
    zone_type
HAVING pre_peak_idle > 2.0
ORDER BY
    peak_breach_pct DESC;


-- 3. Rank zones by peak-hour SLA breach rate
--    while also showing pre-peak rider idle time
SELECT
    zone,
    zone_type,
    ROUND(
        AVG(
            CASE
                WHEN order_hour BETWEEN 15 AND 17
                THEN rider_idle_time_before_dispatch
            END
        ),
        3
    ) AS pre_peak_idle,
    ROUND(
        100.0 *
        SUM(
            CASE
                WHEN order_hour BETWEEN 19 AND 21
                     AND sla_breached = 1
                THEN 1
                ELSE 0
            END
        )
        /
        NULLIF(
            SUM(
                CASE
                    WHEN order_hour BETWEEN 19 AND 21
                    THEN 1
                    ELSE 0
                END
            ),
            0
        ),
        2
    ) AS peak_breach_pct
FROM deliveries
GROUP BY
    zone,
    zone_type
ORDER BY
    peak_breach_pct DESC,
    pre_peak_idle DESC;
    