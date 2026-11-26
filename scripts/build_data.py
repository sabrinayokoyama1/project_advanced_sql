"""Gera uma base financeira sintética e o extrato agregado do dashboard.

Execução: python scripts/build_data.py
Todos os valores, nomes e eventos são fictícios. A semente fixa torna a saída reproduzível.
"""

from __future__ import annotations

import csv
import json
import random
import sqlite3
from collections import defaultdict
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
WEB_DATA = ROOT / "web" / "data"
SEED = 20261126
AS_OF = "2026-10-31"
MONTHS = [(y, m) for y in (2024, 2025, 2026) for m in range(1, 13)
          if (y, m) >= (2024, 11) and (y, m) <= (2026, 10)]
CITIES = ["Campinas", "São Paulo", "Sorocaba", "Jundiaí", "Itu", "Salto"]
FIRST = ["Ana", "Bruno", "Carla", "Diego", "Eduarda", "Felipe", "Gabriela",
         "Henrique", "Isabela", "João", "Karina", "Lucas", "Mariana", "Nicolas",
         "Olívia", "Paulo", "Renata", "Samuel", "Tatiane", "Victor", "Aline",
         "Camila", "Rafael", "Patrícia", "Letícia", "André", "Beatriz", "Caio"]
LAST = ["Souza", "Lima", "Mendes", "Alves", "Pinto", "Rocha", "Martins",
        "Costa", "Ribeiro", "Teixeira", "Duarte", "Ferreira", "Lopes", "Barros",
        "Freitas", "Nogueira", "Araújo", "Batista", "Mello", "Pacheco",
        "Castro", "Farias", "Prado", "Torres", "Ramos", "Cunha", "Dias"]
EXPENSE_CATEGORIES = ["Alimentação", "Moradia", "Transporte", "Compras",
                      "Saúde", "Lazer", "Educação"]
EXPENSE_WEIGHTS = [0.20, 0.29, 0.14, 0.13, 0.09, 0.09, 0.06]


def money(value: float) -> float:
    return round(value + 1e-9, 2)


def dated(year: int, month: int, day: int) -> str:
    return date(year, month, day).isoformat()


def write_csv(conn: sqlite3.Connection, table: str) -> None:
    rows = conn.execute(f"SELECT * FROM {table} ORDER BY 1")
    with (DATA / f"{table}.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([c[0] for c in rows.description])
        writer.writerows(rows)


def main() -> None:
    rng = random.Random(SEED)
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.executescript((DATA / "schema.sql").read_text(encoding="utf-8"))
    DATA.mkdir(exist_ok=True)
    WEB_DATA.mkdir(parents=True, exist_ok=True)

    trans_id = 1
    loan_id = 1
    balances: dict[int, float] = {}
    for customer_id in range(1, 361):
        city = CITIES[(customer_id - 1) % len(CITIES)]
        name = f"{FIRST[(customer_id - 1) % len(FIRST)]} {LAST[(customer_id * 7) % len(LAST)]}"
        age = rng.randint(21, 67)
        income = money(rng.triangular(2200, 18500, 5600))
        score = max(410, min(840, round(rng.gauss(692, 88))))
        conn.execute("INSERT INTO clientes VALUES (?, ?, ?, ?, ?, ?)",
                     (customer_id, name, age, income, city, score))

        primary = 1000 + customer_id * 2
        opening = dated(rng.randint(2020, 2024), rng.randint(1, 12), rng.randint(1, 27))
        balances[primary] = money(income * rng.uniform(0.35, 1.7))
        conn.execute("INSERT INTO contas VALUES (?, ?, ?, ?, ?)",
                     (primary, customer_id, "Corrente", 0, opening))
        if rng.random() < 0.61:
            savings = primary + 1
            balances[savings] = money(income * rng.uniform(0.2, 2.7))
            conn.execute("INSERT INTO contas VALUES (?, ?, ?, ?, ?)",
                         (savings, customer_id, "Poupança", 0, opening))

        # Empréstimos são uma fotografia na data de referência; há clientes sem crédito.
        if rng.random() < 0.63:
            for _ in range(1 + (rng.random() < 0.10)):
                principal = money(income * rng.uniform(0.65, 5.0))
                status = rng.choices(["Ativo", "Quitado", "Atrasado"], [0.55, 0.31, 0.14])[0]
                pending = 0 if status == "Quitado" else money(principal * rng.uniform(0.28, 0.96))
                rate = money(rng.uniform(12, 39))
                issued = dated(rng.randint(2023, 2026), rng.randint(1, 9), rng.randint(1, 27))
                conn.execute("INSERT INTO emprestimos VALUES (?, ?, ?, ?, ?, ?, ?)",
                             (loan_id, customer_id, principal, pending, rate, status, issued))
                loan_id += 1

        for year, month in MONTHS:
            salary = money(income * rng.uniform(0.96, 1.05))
            entries = [("Crédito", "Salário", salary, rng.randint(1, 5))]
            if rng.random() < 0.31:
                entries.append(("Crédito", "Renda extra", money(income * rng.uniform(0.04, 0.25)), rng.randint(6, 26)))
            if rng.random() < 0.21:
                entries.append(("Crédito", "Rendimentos", money(income * rng.uniform(0.005, 0.05)), rng.randint(6, 26)))

            expense_factor = rng.uniform(0.55, 0.96) if score >= 620 else rng.uniform(0.78, 1.20)
            budget = money(income * expense_factor)
            count = rng.randint(5, 10)
            weights = [rng.uniform(0.45, 1.7) for _ in range(count)]
            shares = [money(budget * w / sum(weights)) for w in weights[:-1]]
            shares.append(money(budget - sum(shares)))
            for amount in shares:
                category = rng.choices(EXPENSE_CATEGORIES, EXPENSE_WEIGHTS)[0]
                entries.append(("Débito", category, amount, rng.randint(3, 28)))

            for tx_type, category, amount, day in entries:
                conn.execute("INSERT INTO transacoes VALUES (?, ?, ?, ?, ?, ?)",
                             (trans_id, primary, tx_type, amount, dated(year, month, day), category))
                balances[primary] = money(balances[primary] + (amount if tx_type == "Crédito" else -amount))
                trans_id += 1

    conn.executemany("UPDATE contas SET saldo = ? WHERE conta_id = ?",
                     [(balance, account_id) for account_id, balance in balances.items()])
    conn.commit()
    for table in ("clientes", "contas", "transacoes", "emprestimos"):
        write_csv(conn, table)

    tx = [dict(row) for row in conn.execute("""
        SELECT substr(t.data_transacao, 1, 7) AS mes, c.cidade, t.tipo, t.categoria,
               COUNT(*) AS quantidade, ROUND(SUM(t.valor), 2) AS valor
        FROM transacoes t
        JOIN contas a ON a.conta_id = t.conta_id
        JOIN clientes c ON c.cliente_id = a.cliente_id
        GROUP BY mes, c.cidade, t.tipo, t.categoria
        ORDER BY mes, c.cidade, t.tipo, t.categoria
    """)]

    clients = [dict(row) for row in conn.execute("""
        WITH saldo AS (
          SELECT cliente_id, ROUND(SUM(saldo), 2) AS saldo_total
          FROM contas GROUP BY cliente_id
        ), divida AS (
          SELECT cliente_id,
                 ROUND(SUM(saldo_devedor), 2) AS saldo_devedor,
                 SUM(CASE WHEN status = 'Atrasado' THEN 1 ELSE 0 END) AS atrasados
          FROM emprestimos GROUP BY cliente_id
        ), gastos AS (
          SELECT a.cliente_id, ROUND(SUM(t.valor) / 3.0, 2) AS gasto_mensal_3m
          FROM transacoes t JOIN contas a ON a.conta_id = t.conta_id
          WHERE t.tipo = 'Débito' AND t.data_transacao >= '2026-08-01'
          GROUP BY a.cliente_id
        )
        SELECT c.cliente_id, c.nome, c.cidade, c.idade, c.renda_mensal,
               c.score_credito, s.saldo_total,
               COALESCE(d.saldo_devedor, 0) AS saldo_devedor,
               COALESCE(d.atrasados, 0) AS atrasados,
               COALESCE(g.gasto_mensal_3m, 0) AS gasto_mensal_3m,
               CASE
                 WHEN COALESCE(d.atrasados, 0) > 0 OR c.score_credito < 580
                   OR COALESCE(d.saldo_devedor, 0) > c.renda_mensal * 4 THEN 'Alto'
                 WHEN c.score_credito < 690 OR COALESCE(d.saldo_devedor, 0) > c.renda_mensal * 2
                   OR COALESCE(g.gasto_mensal_3m, 0) > c.renda_mensal THEN 'Moderado'
                 ELSE 'Baixo'
               END AS risco,
               CASE
                 WHEN s.saldo_total >= c.renda_mensal * 2 AND COALESCE(d.saldo_devedor, 0) = 0
                   THEN 'Excelente'
                 WHEN s.saldo_total >= c.renda_mensal AND COALESCE(d.saldo_devedor, 0) <= c.renda_mensal * 2
                   THEN 'Boa'
                 ELSE 'Atenção'
               END AS saude
        FROM clientes c
        JOIN saldo s ON s.cliente_id = c.cliente_id
        LEFT JOIN divida d ON d.cliente_id = c.cliente_id
        LEFT JOIN gastos g ON g.cliente_id = c.cliente_id
        ORDER BY c.cliente_id
    """)]
    loans = [dict(row) for row in conn.execute("""
        SELECT c.cidade, e.status, COUNT(*) AS quantidade,
               ROUND(SUM(e.valor_original), 2) AS valor_original,
               ROUND(SUM(e.saldo_devedor), 2) AS saldo_devedor
        FROM emprestimos e JOIN clientes c ON c.cliente_id = e.cliente_id
        GROUP BY c.cidade, e.status ORDER BY c.cidade, e.status
    """)]
    payload = {
        "meta": {"title": "Projeto Indicadores Financeiros", "synthetic": True,
                 "seed": SEED, "as_of": AS_OF, "first_month": "2024-11",
                 "last_month": "2026-10", "clients": len(clients),
                 "accounts": conn.execute("SELECT COUNT(*) FROM contas").fetchone()[0],
                 "transactions": trans_id - 1,
                 "loans": loan_id - 1},
        "transactions": tx, "clients": clients, "loans": loans,
    }
    (WEB_DATA / "dashboard.json").write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8")
    print(json.dumps(payload["meta"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
