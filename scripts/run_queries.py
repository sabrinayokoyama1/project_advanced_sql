"""Carrega os CSVs gerados e executa todas as consultas SQL."""
from pathlib import Path
import csv
import sqlite3

ROOT = Path(__file__).resolve().parents[1]
conn = sqlite3.connect(":memory:")
conn.execute("PRAGMA foreign_keys = ON")
conn.executescript((ROOT / "data/schema.sql").read_text())
for table in ("clientes", "contas", "transacoes", "emprestimos"):
    with (ROOT / f"data/{table}.csv").open(encoding="utf-8", newline="") as file:
        rows = csv.DictReader(file)
        fields = rows.fieldnames
        marks = ",".join("?" for _ in fields)
        conn.executemany(f"INSERT INTO {table} ({','.join(fields)}) VALUES ({marks})",
                         ([row[field] for field in fields] for row in rows))
for query in sorted((ROOT / "queries").glob("*.sql")):
    result = conn.execute(query.read_text(encoding="utf-8")).fetchall()
    print(f"{query.name}: {len(result)} linhas")
assert conn.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
assert not conn.execute("PRAGMA foreign_key_check").fetchall()
