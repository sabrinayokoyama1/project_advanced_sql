-- Fotografia em 31/10/2026. Saldo e dívida não variam com filtro de período.
WITH saldo AS (
  SELECT cliente_id, SUM(saldo) AS saldo_total FROM contas GROUP BY cliente_id
), divida AS (
  SELECT cliente_id, SUM(saldo_devedor) AS saldo_devedor
  FROM emprestimos GROUP BY cliente_id
), base AS (
  SELECT c.cliente_id, c.nome, c.cidade, c.renda_mensal,
         s.saldo_total, COALESCE(d.saldo_devedor, 0) AS saldo_devedor
  FROM clientes c JOIN saldo s ON s.cliente_id = c.cliente_id
  LEFT JOIN divida d ON d.cliente_id = c.cliente_id
)
SELECT *, ROUND(saldo_total / NULLIF(renda_mensal, 0), 2) AS saldo_renda,
       CASE WHEN saldo_total >= renda_mensal * 2 AND saldo_devedor = 0
              THEN 'Excelente'
            WHEN saldo_total >= renda_mensal AND saldo_devedor <= renda_mensal * 2
              THEN 'Boa'
            ELSE 'Atenção' END AS saude
FROM base ORDER BY saldo_renda DESC, cliente_id;
