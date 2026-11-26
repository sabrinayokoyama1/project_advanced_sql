# Projeto Indicadores Financeiros

Análise SQL e aplicação web para explorar uma carteira financeira **inteiramente fictícia**. O projeto recria a simulação original com uma base maior, consultas compatíveis com SQLite e um dashboard navegável.

## O que há na base

| Entidade | Registros | Campos principais |
| --- | ---: | --- |
| Clientes | 360 | cidade, idade, renda mensal, score fictício |
| Contas | 579 | tipo, saldo, abertura |
| Transações | 77.827 | data, tipo, categoria, valor |
| Empréstimos | 271 | principal, saldo devedor, taxa, status |

As transações cobrem **novembro de 2024 a outubro de 2026**. A fotografia de saldos, dívidas e classificações tem referência em **31/10/2026**. A geração usa a semente fixa `20261126`, por isso os arquivos podem ser reconstruídos de forma idêntica. Não há dados pessoais reais.

## Explorar o dashboard

A aplicação está em `web/`, usa HTML, CSS e JavaScript e lê o extrato agregado `web/data/dashboard.json`. Para rodar localmente:

```bash
python -m http.server 8000 -d web
```

Acesse `http://localhost:8000`. Os filtros de cidade e período atualizam os indicadores de entradas, saídas, resultado, transações, evolução, categorias e comparativo regional. A seção Clientes apresenta uma fotografia atual da carteira; o filtro de período não altera saldo, empréstimos nem as classificações. O botão **Exportar CSV** salva o resumo por cidade da seleção.

## Reproduzir os dados e as consultas

Requer apenas Python 3.10+ e sua biblioteca padrão.

```bash
python scripts/build_data.py
python scripts/run_queries.py
```

`build_data.py` gera quatro CSVs em `data/` e o JSON usado pelo dashboard. `run_queries.py` carrega os CSVs em SQLite na memória, executa as consultas em `queries/` e valida a integridade referencial. O esquema e os índices estão em `data/schema.sql`.

As consultas usam CTEs, agregações, `CASE`, `COALESCE`, `NULLIF`, `LAG`, `DENSE_RANK` e médias móveis. Cada métrica tem definição explícita:

- **Entradas/saídas:** soma de créditos/débitos registrados. A simulação não gera transferências internas.
- **Resultado:** entradas menos saídas, sem interpretação de lucro contábil.
- **Risco:** classificação demonstrativa baseada em score fictício, atraso, dívida/renda e gasto médio recente; não é modelo de crédito.
- **Saúde financeira:** regra ilustrativa entre saldo, renda mensal e saldo devedor na data de referência.

## Estrutura

```text
data/                  esquema SQL e CSVs sintéticos
queries/               análises SQL executáveis no SQLite
scripts/               geração e verificação dos dados
web/                   dashboard estático e extrato agregado
```

**Limites:** a distribuição dos registros é simulada para demonstração. Os saldos incluem valores de abertura fictícios, e os indicadores não devem ser usados para decisões financeiras reais.

## Publicar no Streamlit Community Cloud

O arquivo principal é [`streamlit_app.py`](streamlit_app.py). Na tela **Create app** do Streamlit, escolha este repositório, a branch com as alterações aprovadas e `streamlit_app.py` como caminho do arquivo. O `requirements.txt` instala Streamlit, pandas e Altair; `.streamlit/config.toml` define o tema escuro violeta. A aplicação carrega o mesmo JSON agregado da versão web.

Para testar localmente:

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

O dashboard web em `web/` também usa o tema escuro violeta.
