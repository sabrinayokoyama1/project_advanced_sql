WITH gastos AS (
    SELECT
        A.cliente_id,
        SUM(B.valor) AS total_gastos
    FROM contas AS A
    INNER JOIN transacoes AS B
        ON A.conta_id = B.conta_id
    WHERE B.tipo = 'Debito'
    GROUP BY
        A.cliente_id
),

emprestimos_ativos AS (
    SELECT
        A.cliente_id,
        SUM(A.valor) AS total_emprestimos
    FROM emprestimos AS A
    WHERE A.status = 'Ativo'
    GROUP BY
        A.cliente_id
)

SELECT
    A.cliente_id,
    A.nome,
    A.renda_mensal,
    COALESCE(C.total_gastos, 0) AS total_gastos,
    B.saldo,
    COALESCE(D.total_emprestimos, 0) AS total_emprestimos,

    (B.saldo / A.renda_mensal) AS proporcao_saldo_renda,
    (COALESCE(C.total_gastos, 0) / A.renda_mensal) AS proporcao_gastos_renda,

    CASE
        WHEN B.saldo >= A.renda_mensal
             AND COALESCE(D.total_emprestimos, 0) = 0
            THEN 'Excelente' -- saldo alto e sem dívidas

        WHEN B.saldo >= A.renda_mensal * 0.5
             AND COALESCE(D.total_emprestimos, 0) <= A.renda_mensal * 2
            THEN 'Boa' -- saldo razoável e dívidas controladas

        WHEN COALESCE(C.total_gastos, 0) > A.renda_mensal
            THEN 'Risco' -- gasta mais do que ganha

        ELSE 'Atencao' -- situação intermediária
    END AS score_saude_financeira

FROM clientes AS A
INNER JOIN contas AS B
    ON A.cliente_id = B.cliente_id
LEFT JOIN gastos AS C
    ON A.cliente_id = C.cliente_id
LEFT JOIN emprestimos_ativos AS D
    ON A.cliente_id = D.cliente_id
ORDER BY
    score_saude_financeira;
