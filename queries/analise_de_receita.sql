SELECT 
    c.cliente_id,
    c.nome,
    c.cidade,
    COUNT(t.transacao_id) AS qtd_creditos,
    SUM(t.valor) AS total_recebido,
    AVG(t.valor) AS valor_medio_credito,
    MAX(t.valor) AS maior_credito,
    MIN(t.valor) AS menor_credito
FROM clientes c
JOIN contas co 
    ON c.cliente_id = co.cliente_id
JOIN transacoes t 
    ON co.conta_id = t.conta_id
WHERE t.tipo = 'Crédito'
GROUP BY c.cliente_id, c.nome, c.cidade
ORDER BY total_recebido DESC;