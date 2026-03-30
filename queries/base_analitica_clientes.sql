WITH resumo_transacoes AS (
    SELECT
        A.cliente_id,
        COUNT(C.transacao_id) AS qtd_transacoes,
        SUM(CASE WHEN C.tipo = 'Debito' THEN C.valor ELSE 0 END) AS total_debito,
        SUM(CASE WHEN C.tipo = 'Credito' THEN C.valor ELSE 0 END) AS total_credito,
        MAX(C.data_transacao) AS ultima_transacao
    FROM clientes AS A
    LEFT JOIN contas AS B
        ON A.cliente_id = B.cliente_id
    LEFT JOIN transacoes AS C
        ON B.conta_id = C.conta_id
    GROUP BY
        A.cliente_id
),

resumo_emprestimos AS (
    SELECT
        A.cliente_id,
        COUNT(A.emprestimo_id) AS qtd_emprestimos,
        SUM(A.valor) AS total_emprestimos,
        SUM(CASE WHEN A.status = 'Ativo' THEN 1 ELSE 0 END) AS emprestimos_ativos
    FROM emprestimos AS A
    GROUP BY
        A.cliente_id
)

SELECT
    A.cliente_id,
    A.idade,
    A.renda_mensal,
    A.score_credito,
    COUNT(DISTINCT B.conta_id) AS qtd_contas,
    SUM(B.saldo) AS saldo_total,
    C.qtd_transacoes,
    C.total_debito,
    C.total_credito,
    C.ultima_transacao,
    D.qtd_emprestimos,
    D.total_emprestimos,
    D.emprestimos_ativos,
    DATEDIFF(CURRENT_DATE, C.ultima_transacao) AS dias_sem_transacao,
    CASE
        WHEN DATEDIFF(CURRENT_DATE, C.ultima_transacao) > 30 THEN 1
        ELSE 0
    END AS churn_flag
FROM clientes AS A
LEFT JOIN contas AS B
    ON A.cliente_id = B.cliente_id
LEFT JOIN resumo_transacoes AS C
    ON A.cliente_id = C.cliente_id
LEFT JOIN resumo_emprestimos AS D
    ON A.cliente_id = D.cliente_id
GROUP BY
    A.cliente_id,
    A.idade,
    A.renda_mensal,
    A.score_credito,
    C.qtd_transacoes,
    C.total_debito,
    C.total_credito,
    C.ultima_transacao,
    D.qtd_emprestimos,
    D.total_emprestimos,
    D.emprestimos_ativos;
