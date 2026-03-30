SELECT
    A.cliente_id,
    A.nome,
    A.cidade,
    COUNT(C.transacao_id) AS qtd_creditos,
    SUM(C.valor) AS total_recebido,
    AVG(C.valor) AS valor_medio_credito,
    MAX(C.valor) AS maior_credito,
    MIN(C.valor) AS menor_credito
FROM clientes AS A
INNER JOIN contas AS B
    ON A.cliente_id = B.cliente_id
INNER JOIN transacoes AS C
    ON B.conta_id = C.conta_id
WHERE C.tipo = 'Credito'
GROUP BY
    A.cliente_id,
    A.nome,
    A.cidade
ORDER BY
    total_recebido DESC;
