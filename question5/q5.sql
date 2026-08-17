-- criando calendario com todas as datas do periodo
WITH calendario AS (
    SELECT
        data::date AS data,
        CASE EXTRACT(ISODOW FROM data)
            WHEN 1 THEN 'Segunda-feira'
            WHEN 2 THEN 'Terça-feira'
            WHEN 3 THEN 'Quarta-feira'
            WHEN 4 THEN 'Quinta-feira'
            WHEN 5 THEN 'Sexta-feira'
            WHEN 6 THEN 'Sábado'
            WHEN 7 THEN 'Domingo'
        END AS dia_semana
    FROM generate_series(
        (SELECT MIN(placed_at)::date
         FROM orders
         WHERE channel = 'pos'),
        CURRENT_DATE,
        INTERVAL '1 day'
    ) AS data
),

-- somando as vendas por dia
vendas_diarias AS (
    SELECT
        placed_at::date AS data,
        SUM(total) AS total_vendas
    FROM orders
    WHERE channel = 'pos'
    GROUP BY placed_at::date
),

-- cruzando datas do calendario com as vendas dos dias
calendario_vendas AS (
    SELECT
        c.data,
        c.dia_semana,
        COALESCE(v.total_vendas, 0) AS total_vendas
    FROM calendario c
    LEFT JOIN vendas_diarias v
        ON c.data = v.data
)

-- calcula a media de vendas por dia da semana
SELECT
    dia_semana,
    AVG(total_vendas) AS media_vendas
FROM calendario_vendas
GROUP BY
    dia_semana
ORDER BY
    CASE dia_semana
        WHEN 'Segunda-feira' THEN 1
        WHEN 'Terça-feira' THEN 2
        WHEN 'Quarta-feira' THEN 3
        WHEN 'Quinta-feira' THEN 4
        WHEN 'Sexta-feira' THEN 5
        WHEN 'Sábado' THEN 6
        WHEN 'Domingo' THEN 7
    END;