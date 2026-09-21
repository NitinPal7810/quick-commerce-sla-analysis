USE quick_commerce_sla;

-- ============================================================
-- 01. OVERALL SLA BREACH AUDIT
-- ============================================================

-- 1. Total orders
SELECT
    COUNT(*) AS total_orders
FROM deliveries;


-- 2. Total breached orders
SELECT
    SUM(sla_breached) AS breached_orders
FROM deliveries;


-- 3. Overall SLA breach rate
SELECT
    ROUND(
        100.0 * SUM(sla_breached) / COUNT(*),
        2
    ) AS sla_breach_rate_pct
FROM deliveries;


-- 4. Complete SLA audit
SELECT
    COUNT(*) AS total_orders,
    SUM(sla_breached) AS breached_orders,
    COUNT(*) - SUM(sla_breached) AS successful_orders,
    ROUND(
        100.0 * SUM(sla_breached) / COUNT(*),
        2
    ) AS breach_rate_pct,
    ROUND(AVG(order_value_inr), 2) AS avg_order_value_inr,
    ROUND(AVG(delivery_time_min), 2) AS avg_delivery_time_min,
    ROUND(AVG(dispatch_delay_min), 2) AS avg_dispatch_delay_min
FROM deliveries;

