USE quick_commerce_sla;

-- ============================================================
-- 07. RETENTION & REVENUE IMPACT
-- ============================================================

-- 1. Reorder probability by SLA breach status
SELECT
    sla_breached,
    COUNT(*) AS order_count,

    ROUND(
        AVG(reorder_probability),
        4
    ) AS avg_reorder_probability,

    ROUND(
        AVG(order_value_inr),
        2
    ) AS avg_order_value_inr,

    ROUND(
        AVG(reorder_probability) * AVG(order_value_inr),
        2
    ) AS estimated_future_value_per_order

FROM deliveries

GROUP BY
    sla_breached

ORDER BY
    sla_breached;


-- 2. Reorder probability penalty caused by SLA breach
SELECT
    ROUND(
        AVG(
            CASE
                WHEN sla_breached = 0
                THEN reorder_probability
            END
        )
        -
        AVG(
            CASE
                WHEN sla_breached = 1
                THEN reorder_probability
            END
        ),
        4
    ) AS observed_reorder_probability_penalty,

    -- Business model uses a fixed 0.20 penalty
    -- for the resume / scenario analysis
    0.20 AS modeled_reorder_probability_penalty,

    ROUND(
        AVG(order_value_inr),
        2
    ) AS avg_order_value_inr

FROM deliveries;


-- 3. Modeled revenue at risk
-- Formula:
-- Breached Orders × 0.20 Reorder Probability Penalty
-- × Average Order Value

SELECT
    SUM(sla_breached) AS breached_orders,

    0.20 AS modeled_reorder_probability_penalty,

    ROUND(
        AVG(order_value_inr),
        2
    ) AS avg_order_value_inr,

    ROUND(
        SUM(sla_breached)
        * 0.20
        * AVG(order_value_inr),
        2
    ) AS modeled_revenue_at_risk_inr,

    ROUND(
        SUM(sla_breached)
        * 0.20
        * AVG(order_value_inr)
        / 100000,
        2
    ) AS modeled_revenue_at_risk_lakh

FROM deliveries;
