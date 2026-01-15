--- Classificação de perfil financeiro
	WITH resumo_financeiro AS (
	  SELECT 
		c.cliente_id,
		c.nome,
		c.renda_mensal,
		ct.saldo,
		COUNT(t.transacao_id) AS qtd_transacoes,
		SUM(CASE WHEN t.tipo = 'Débito' THEN t.valor ELSE 0 END) AS total_gasto,
		COALESCE(SUM(e.valor), 0) AS total_emprestimos
	  FROM clientes c
	  
	  LEFT JOIN contas ct ON 
	  c.cliente_id = ct.cliente_id
	  
	  LEFT JOIN transacoes t ON 
		ct.conta_id = t.conta_id
		
	  LEFT JOIN emprestimos e ON 
		c.cliente_id = e.cliente_id
		
	  GROUP BY c.cliente_id, c.nome, c.renda_mensal, ct.saldo
	)

	SELECT 
	  nome,
	  renda_mensal,
	  total_gasto,
	  total_emprestimos,
	  qtd_transacoes,
	  saldo,
	  CASE
		WHEN total_gasto > renda_mensal THEN 'Gastador' -- Gasta mais do que ganha
		WHEN qtd_transacoes <= 2 AND saldo > renda_mensal THEN 'Conservador' -- Poucas transações e saldo alto
		WHEN total_emprestimos >= renda_mensal THEN 'Gastador' -- Empréstimos altos em relação à renda
		ELSE 'Equilibrado' -- Comportamento equilibrado
	  END AS perfil_financeiro
	FROM resumo_financeiro
	ORDER BY perfil_financeiro;
