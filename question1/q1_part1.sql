-- verificacao de numero de linhas e colunas
SELECT COUNT(*) AS total_lines
FROM orders;

SELECT COUNT(*) AS total_columns
FROM information_schema.columns
WHERE table_schema = DATABASE()
    AND table_name = 'orders';


-- analise do intervalo de datas 
SELECT created_at
FROM orders
LIMIT 10;

SELECT created_at
FROM orders
WHERE STR_TO_DATE(created_at, '%Y-%m-%d %H:%i:%s') IS NULL;

SELECT
    MIN(STR_TO_DATE(created_at, '%Y-%m-%d %H:%i:%s')) AS min_date,
    MAX(STR_TO_DATE(created_at, '%Y-%m-%d %H:%i:%s')) AS max_date
FROM orders;