-- Risco descritivo, não é score de crédito nem recomendação de concessão.
WITH divida AS (
  SELECT cliente_id, SUM(saldo_devedor) AS saldo_devedor,
         SUM(CASE WHEN status = 'Atrasado' THEN 1 ELSE 0 END) AS atrasados
  FROM emprestimos GROUP BY cliente_id
), gastos AS (
  SELECT a.cliente_id, SUM(t.valor) / 3.0 AS gasto_mensal_3m
  FROM transacoes t JOIN contas a ON a.conta_id = t.conta_id
  WHERE t.tipo = 'Débito' AND t.data_transacao >= '2026-08-01'
  GROUP BY a.cliente_id
), base AS (
  SELECT c.cliente_id, c.nome, c.cidade, c.renda_mensal, c.score_credito,
         COALESCE(d.saldo_devedor, 0) AS saldo_devedor,
         COALESCE(d.atrasados, 0) AS atrasados,
         COALESCE(g.gasto_mensal_3m, 0) AS gasto_mensal_3m
  FROM clientes c LEFT JOIN divida d ON d.cliente_id = c.cliente_id
  LEFT JOIN gastos g ON g.cliente_id = c.cliente_id
)
SELECT *, ROUND(saldo_devedor / NULLIF(renda_mensal, 0), 2) AS divida_renda,
       CASE WHEN atrasados > 0 OR score_credito < 580 OR saldo_devedor > renda_mensal * 4
              THEN 'Alto'
            WHEN score_credito < 690 OR saldo_devedor > renda_mensal * 2
                 OR gasto_mensal_3m > renda_mensal THEN 'Moderado'
            ELSE 'Baixo' END AS risco
FROM base ORDER BY divida_renda DESC, cliente_id;
