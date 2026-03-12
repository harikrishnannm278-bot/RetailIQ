SELECT 
    c.product_category_name_english     AS category,
    COUNT(DISTINCT o.order_id)          AS total_orders,
    ROUND(SUM(p.payment_value), 2)      AS total_revenue,
    ROUND(AVG(r.review_score), 2)       AS avg_review
FROM orders o
JOIN order_items oi  ON o.order_id    = oi.order_id
JOIN products pr     ON oi.product_id = pr.product_id
JOIN categories c    ON pr.product_category_name = c.product_category_name
JOIN payments p      ON o.order_id    = p.order_id
JOIN reviews r       ON o.order_id    = r.order_id
WHERE o.order_status = 'delivered'
GROUP BY category
ORDER BY total_revenue DESC
LIMIT 15;

SELECT
    SUBSTR(o.order_purchase_timestamp, 1, 7) AS year_month,
    COUNT(DISTINCT o.order_id)               AS total_orders,
    ROUND(SUM(p.payment_value), 2)           AS monthly_revenue
FROM orders o
JOIN payments p ON o.order_id = p.order_id
WHERE o.order_status = 'delivered'
GROUP BY year_month
ORDER BY year_month;

SELECT
    c.customer_state                    AS state,
    COUNT(DISTINCT o.order_id)          AS total_orders,
    COUNT(DISTINCT c.customer_id)       AS total_customers,
    ROUND(SUM(p.payment_value), 2)      AS total_revenue,
    ROUND(AVG(r.review_score), 2)       AS avg_review
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN payments p  ON o.order_id    = p.order_id
JOIN reviews r   ON o.order_id    = r.order_id
WHERE o.order_status = 'delivered'
GROUP BY state
ORDER BY total_revenue DESC;

SELECT
    order_status,
    COUNT(*)                                           AS total,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) AS percentage
FROM orders
GROUP BY order_status
ORDER BY total DESC;

SELECT
    oi.seller_id,
    s.seller_state,
    COUNT(DISTINCT oi.order_id)    AS total_orders,
    ROUND(SUM(p.payment_value), 2) AS total_revenue
FROM order_items oi
JOIN payments p ON oi.order_id  = p.order_id
JOIN sellers s  ON oi.seller_id = s.seller_id
GROUP BY oi.seller_id, s.seller_state
ORDER BY total_revenue DESC
LIMIT 10;

SELECT
    c.customer_state,
    COUNT(*)                                     AS total_orders,
    SUM(CASE WHEN o.order_delivered_customer_date
             > o.order_estimated_delivery_date
             THEN 1 ELSE 0 END)                  AS late_deliveries,
    ROUND(SUM(CASE WHEN o.order_delivered_customer_date
                   > o.order_estimated_delivery_date
                   THEN 1 ELSE 0 END) * 100.0 
              / COUNT(*), 2)                     AS late_rate_pct
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_status = 'delivered'
AND o.order_delivered_customer_date IS NOT NULL
GROUP BY c.customer_state
ORDER BY late_rate_pct DESC;