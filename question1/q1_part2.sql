-- analise de valores dos pedidos
SELECT
    MIN(total) AS min_value,
    MAX(total) AS max_value,
    AVG(total) AS mean_value
FROM orders;