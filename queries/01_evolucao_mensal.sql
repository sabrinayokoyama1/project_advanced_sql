-- Entradas e saídas mensais, variação mensal e média móvel de três meses.
WITH movimento AS (
  SELECT substr(t.data_transacao, 1, 7) AS mes,
         ROUND(SUM(CASE WHEN t.tipo = 'Crédito' THEN t.valor ELSE 0 END), 2) AS entradas,
         ROUND(SUM(CASE WHEN t.tipo = 'Débito' THEN t.valor ELSE 0 END), 2) AS saidas,
         COUNT(*) AS transacoes
  FROM transacoes t
  GROUP BY substr(t.data_transacao, 1, 7)
), serie AS (
  SELECT *, ROUND(entradas - saidas, 2) AS resultado,
         LAG(entradas - saidas) OVER (ORDER BY mes) AS resultado_anterior,
         ROUND(AVG(entradas - saidas) OVER (
           ORDER BY mes ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 2) AS media_movel_3m
  FROM movimento
)
SELECT mes, entradas, saidas, resultado, transacoes,
       ROUND(resultado - resultado_anterior, 2) AS variacao_resultado,
       media_movel_3m
FROM serie ORDER BY mes;
