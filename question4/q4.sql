-- calcula gasto total, num de pedidos e ticket medio de cada cliente
WITH customer_revenue AS (
    SELECT
        customer_id,
        SUM(total) AS total_revenue,
        COUNT(id) AS transaction_count,
        SUM(total) / COUNT(id) AS average_ticket
    FROM orders
    GROUP BY
        customer_id
),

-- calcula num de categorias diferentes que o cliente ja comprou
customer_categories AS (
    SELECT
        o.customer_id,
        COUNT(DISTINCT p.category_id) AS category_diversity
    FROM orders o
    JOIN order_items oi
        ON oi.order_id = o.id
    JOIN product_variants pv
        ON pv.id = oi.product_variant_id
    JOIN products p
        ON p.id = pv.product_id
    GROUP BY
        o.customer_id
),

-- identifica os 10 clientes com maior ticket medio em 13 categorias ou mais
elite_customers AS (
    SELECT
        cr.customer_id,
        cr.total_revenue,
        cr.transaction_count,
        cr.average_ticket,
        cc.category_diversity
    FROM customer_revenue cr
    JOIN customer_categories cc
        ON cc.customer_id = cr.customer_id
    WHERE cc.category_diversity >= 13
    ORDER BY
        cr.average_ticket DESC,
        cr.customer_id ASC
    LIMIT 10
)

-- calcula a categoria mais vendida para os clientes de elite
SELECT
    p.category_id,
    SUM(oi.quantity) AS total_quantity
FROM elite_customers ec
JOIN orders o
    ON o.customer_id = ec.customer_id
JOIN order_items oi
    ON oi.order_id = o.id
JOIN product_variants pv
    ON pv.id = oi.product_variant_id
JOIN products p
    ON p.id = pv.product_id
GROUP BY
    p.category_id
ORDER BY
    total_quantity DESC
LIMIT 1;