-- Ranking de despesas por categoria e participação no total.
WITH categorias AS (
  SELECT t.categoria, COUNT(*) AS transacoes, ROUND(SUM(t.valor), 2) AS total,
         ROUND(AVG(t.valor), 2) AS ticket_medio
  FROM transacoes t WHERE t.tipo = 'Débito'
  GROUP BY t.categoria
)
SELECT categoria, transacoes, total, ticket_medio,
       ROUND(100.0 * total / SUM(total) OVER (), 2) AS participacao_pct,
       DENSE_RANK() OVER (ORDER BY total DESC) AS posicao
FROM categorias ORDER BY posicao;
