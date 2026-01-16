SELECT 
    t.categoria,
    COUNT(*) AS qtd_transacoes,
    SUM(t.valor) AS total_receita,
    AVG(t.valor) AS ticket_medio
FROM transacoes t
WHERE t.tipo = 'Crédito'
GROUP BY t.categoria
ORDER BY total_receita DESC;
