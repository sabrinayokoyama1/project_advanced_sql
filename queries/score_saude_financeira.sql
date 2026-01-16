WITH gastos AS (
    SELECT 
        co.cliente_id,
        SUM(t.valor) AS total_gastos
    FROM contas co
    JOIN transacoes t 
        ON co.conta_id = t.conta_id
    WHERE t.tipo = 'Débito'
    GROUP BY co.cliente_id
),

emprestimos_ativos AS (
    SELECT 
        cliente_id,
        SUM(valor) AS total_emprestimos
    FROM emprestimos
    WHERE status = 'Ativo'
    GROUP BY cliente_id
)

SELECT 
    c.cliente_id,
    c.nome,
    c.renda_mensal,
    COALESCE(g.total_gastos, 0) AS total_gastos,
    co.saldo,
    COALESCE(e.total_emprestimos, 0) AS total_emprestimos,

    -- Indicadores
    (co.saldo / c.renda_mensal) AS proporcao_saldo_renda,
    (COALESCE(g.total_gastos, 0) / c.renda_mensal) AS proporcao_gastos_renda,

    -- Score de saude financeira
    CASE
        WHEN co.saldo >= c.renda_mensal 
             AND COALESCE(e.total_emprestimos, 0) = 0
            THEN 'Excelente'

        WHEN co.saldo >= c.renda_mensal * 0.5 
             AND COALESCE(e.total_emprestimos, 0) <= c.renda_mensal * 2
            THEN 'Boa'

        WHEN COALESCE(g.total_gastos, 0) > c.renda_mensal
            THEN 'Risco'

        ELSE 'Atenção'
    END AS score_saude_financeira

FROM clientes c
JOIN contas co 
    ON c.cliente_id = co.cliente_id
LEFT JOIN gastos g 
    ON c.cliente_id = g.cliente_id
LEFT JOIN emprestimos_ativos e 
    ON c.cliente_id = e.cliente_id
ORDER BY score_saude_financeira;
