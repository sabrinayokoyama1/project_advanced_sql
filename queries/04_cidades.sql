-- Comparação de cidades sem multiplicação de linhas por empréstimos e transações.
WITH clientes_cidade AS (
  SELECT cidade, COUNT(*) AS clientes, ROUND(AVG(renda_mensal), 2) AS renda_media
  FROM clientes GROUP BY cidade
), movimentos AS (
  SELECT c.cidade,
         SUM(CASE WHEN t.tipo = 'Crédito' THEN t.valor ELSE 0 END) AS entradas,
         SUM(CASE WHEN t.tipo = 'Débito' THEN t.valor ELSE 0 END) AS saidas
  FROM transacoes t JOIN contas a ON a.conta_id = t.conta_id
  JOIN clientes c ON c.cliente_id = a.cliente_id GROUP BY c.cidade
), dividas AS (
  SELECT c.cidade, SUM(e.saldo_devedor) AS saldo_devedor
  FROM emprestimos e JOIN clientes c ON c.cliente_id = e.cliente_id
  GROUP BY c.cidade
)
SELECT cc.cidade, cc.clientes, cc.renda_media,
       ROUND(m.entradas, 2) AS entradas, ROUND(m.saidas, 2) AS saidas,
       ROUND(m.entradas - m.saidas, 2) AS resultado,
       ROUND(COALESCE(d.saldo_devedor, 0), 2) AS saldo_devedor
FROM clientes_cidade cc JOIN movimentos m ON m.cidade = cc.cidade
LEFT JOIN dividas d ON d.cidade = cc.cidade
ORDER BY resultado DESC;
