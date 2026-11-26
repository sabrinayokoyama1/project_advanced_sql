PRAGMA foreign_keys = ON;

CREATE TABLE clientes (
  cliente_id INTEGER PRIMARY KEY,
  nome TEXT NOT NULL,
  idade INTEGER NOT NULL CHECK (idade BETWEEN 18 AND 100),
  renda_mensal NUMERIC NOT NULL CHECK (renda_mensal > 0),
  cidade TEXT NOT NULL,
  score_credito INTEGER NOT NULL CHECK (score_credito BETWEEN 300 AND 850)
);

CREATE TABLE contas (
  conta_id INTEGER PRIMARY KEY,
  cliente_id INTEGER NOT NULL REFERENCES clientes(cliente_id),
  tipo_conta TEXT NOT NULL CHECK (tipo_conta IN ('Corrente', 'Poupança')),
  saldo NUMERIC NOT NULL,
  data_abertura TEXT NOT NULL
);

CREATE TABLE transacoes (
  transacao_id INTEGER PRIMARY KEY,
  conta_id INTEGER NOT NULL REFERENCES contas(conta_id),
  tipo TEXT NOT NULL CHECK (tipo IN ('Crédito', 'Débito')),
  valor NUMERIC NOT NULL CHECK (valor > 0),
  data_transacao TEXT NOT NULL,
  categoria TEXT NOT NULL
);

CREATE TABLE emprestimos (
  emprestimo_id INTEGER PRIMARY KEY,
  cliente_id INTEGER NOT NULL REFERENCES clientes(cliente_id),
  valor_original NUMERIC NOT NULL CHECK (valor_original > 0),
  saldo_devedor NUMERIC NOT NULL CHECK (saldo_devedor >= 0),
  taxa_juros_anual NUMERIC NOT NULL CHECK (taxa_juros_anual >= 0),
  status TEXT NOT NULL CHECK (status IN ('Ativo', 'Quitado', 'Atrasado')),
  data_concessao TEXT NOT NULL
);

CREATE INDEX idx_contas_cliente ON contas(cliente_id);
CREATE INDEX idx_transacoes_conta_data ON transacoes(conta_id, data_transacao);
CREATE INDEX idx_emprestimos_cliente_status ON emprestimos(cliente_id, status);
