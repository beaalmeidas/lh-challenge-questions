-- verificando se ha valores nulos
SELECT
    COUNT(*) AS num_orders,
    SUM(CASE WHEN total IS NULL THEN 1 ELSE 0 END) AS total_null_values
FROM orders;


-- verificando se ha valores invalidos
SELECT
    SUM(CASE WHEN total = 0 THEN 1 ELSE 0 END) AS total_zero_value,
    SUM(CASE WHEN total < 0 THEN 1 ELSE 0 END) AS total_negative_value
FROM orders;


-- verificando se ha pedidos com valor total inconsistente
SELECT
    COUNT(*) AS inconsistent_orders
FROM orders
WHERE ABS(
    total - (subtotal - discount_amount)
) > 0.01;


-- verificacao de valores fora da curva
WITH quarters AS (
    SELECT
        PERCENTILE_CONT(0.25)
            WITHIN GROUP (ORDER BY total) AS q1,
        PERCENTILE_CONT(0.75)
            WITHIN GROUP (ORDER BY total) AS q3
    FROM orders
    WHERE total IS NOT NULL
),
limits AS (
    SELECT
        q1,
        q3,
        q3 - q1 AS iqr,
        q1 - 1.5 * (q3 - q1) AS lowerbound,
        q3 + 1.5 * (q3 - q1) AS upperbound
    FROM quarters
)
SELECT
    q1,
    q3,
    iqr,
    lowerbound,
    upperbound,
    COUNT(total) AS num_outliers
FROM orders
CROSS JOIN limits
WHERE
    total < lowerbound
    OR total > upperbound
GROUP BY
    q1,
    q3,
    iqr,
    lowerbound,
    upperbound;