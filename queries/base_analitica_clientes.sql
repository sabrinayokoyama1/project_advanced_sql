WITH resumo_transacoes AS (
    SELECT
        c.cliente_id,
        COUNT(t.transacao_id) AS qtd_transacoes,
        SUM(CASE WHEN t.tipo = 'Debito' THEN t.valor ELSE 0 END) AS total_debito,
        SUM(CASE WHEN t.tipo = 'Credito' THEN t.valor ELSE 0 END) AS total_credito,
        MAX(t.data_transacao) AS ultima_transacao
    FROM clientes c
    LEFT JOIN contas co ON c.cliente_id = co.cliente_id
    LEFT JOIN transacoes t ON co.conta_id = t.conta_id
    GROUP BY c.cliente_id
),

resumo_emprestimos AS (
    SELECT
        cliente_id,
        COUNT(emprestimo_id) AS qtd_emprestimos,
        SUM(valor) AS total_emprestimos,
        SUM(CASE WHEN status = 'Ativo' THEN 1 ELSE 0 END) AS emprestimos_ativos
    FROM emprestimos
    GROUP BY cliente_id
)

SELECT
    c.cliente_id,
    c.idade,
    c.renda_mensal,
    c.score_credito,
    COUNT(DISTINCT co.conta_id) AS qtd_contas,
    SUM(co.saldo) AS saldo_total,
    rt.qtd_transacoes,
    rt.total_debito,
    rt.total_credito,
    rt.ultima_transacao,
    re.qtd_emprestimos,
    re.total_emprestimos,
    re.emprestimos_ativos,
    DATEDIFF(CURRENT_DATE, rt.ultima_transacao) AS dias_sem_transacao,
    CASE 
        WHEN DATEDIFF(CURRENT_DATE, rt.ul_
