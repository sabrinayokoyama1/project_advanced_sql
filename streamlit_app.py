"""Dashboard Streamlit do Projeto Indicadores Financeiros.

Deploy no Streamlit Community Cloud: arquivo principal streamlit_app.py.
Compatível com Python 3.14 e Altair 6.3.
"""
from __future__ import annotations

import json
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st


DATA = Path(__file__).parent / "web" / "data" / "dashboard.json"
PURPLE = "#AD84FF"
LILAC = "#D5A3FA"
PLUM = "#7447B8"
BG = "#100C1C"
PANEL = "#1C162E"
TEXT = "#F2ECFF"
MUTED = "#B8A9CF"

st.set_page_config(
    page_title="Projeto Indicadores Financeiros",
    page_icon="💜",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown("""
<style>
.block-container{padding-top:2.2rem;max-width:1450px}
[data-testid="stSidebar"]{background:#150F25;border-right:1px solid #332745}
[data-testid="stMetric"]{background:#1C162E;border:1px solid #362A49;border-radius:14px;padding:1.15rem 1.3rem}
[data-testid="stMetricLabel"]{color:#B8A9CF}
[data-testid="stMetricValue"]{color:#F2ECFF}
[data-testid="stVerticalBlockBorderWrapper"]{border-color:#362A49!important}
h1,h2,h3{letter-spacing:-.04em}
a{color:#C7A5FF!important}
.stButton button,.stDownloadButton button{border-radius:9px;border-color:#6D4A9A;color:#E8D8FF}
.stButton button:hover,.stDownloadButton button:hover{border-color:#B993FF;color:white}
.brand-title{font-size:1.5rem;font-weight:800;line-height:1.12;color:#F7F1FF;margin:.2rem 0 .5rem}
.brand-subtitle{font-size:.7rem;letter-spacing:.16em;font-weight:800;color:#B892F5;margin-bottom:2rem}
.eyebrow{color:#BC97FF;font-size:.75rem;font-weight:800;letter-spacing:.16em;margin-bottom:.2rem}
.subtitle{color:#B8A9CF;margin-top:-.4rem;margin-bottom:1.8rem}
.note{background:#2C2044;border-left:3px solid #AD84FF;border-radius:8px;padding:1rem 1.2rem;color:#D9CDEB}
.small-muted{color:#A99ABC;font-size:.85rem}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data() -> tuple[dict, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    raw = json.loads(DATA.read_text(encoding="utf-8"))
    return raw["meta"], pd.DataFrame(raw["transactions"]), pd.DataFrame(raw["clients"]), pd.DataFrame(raw["loans"])


def brl(value: float, compact: bool = False) -> str:
    value = float(value)
    if compact and abs(value) >= 1_000_000:
        return f"R$ {value / 1_000_000:,.1f} mi".replace(",", "X").replace(".", ",").replace("X", ".")
    if compact and abs(value) >= 1_000:
        return f"R$ {value / 1_000:,.1f} mil".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def show_overview(tx: pd.DataFrame, clients: pd.DataFrame, months: list[str], meta: dict) -> None:
    st.markdown('<div class="eyebrow">INTELIGÊNCIA FINANCEIRA</div>', unsafe_allow_html=True)
    st.title("Visão geral")
    st.markdown('<p class="subtitle">Uma leitura clara do comportamento financeiro da carteira.</p>', unsafe_allow_html=True)
    income = tx.loc[tx.tipo == "Crédito", "valor"].sum()
    expense = tx.loc[tx.tipo == "Débito", "valor"].sum()
    cols = st.columns(4)
    cols[0].metric("Entradas", brl(income, True), help="Soma dos créditos no período filtrado")
    cols[1].metric("Saídas", brl(expense, True), help="Soma dos débitos no período filtrado")
    cols[2].metric("Resultado", brl(income - expense, True), help="Entradas menos saídas")
    cols[3].metric("Transações", f"{int(tx.quantidade.sum()):,}".replace(",", "."))

    left, right = st.columns([1.55, 1], gap="large")
    with left:
        st.subheader("Evolução mensal")
        st.caption("Entradas e saídas da carteira")
        monthly = tx.groupby(["mes", "tipo"], as_index=False)["valor"].sum()
        monthly["tipo"] = monthly.tipo.map({"Crédito": "Entradas", "Débito": "Saídas"})
        chart = alt.Chart(monthly).mark_line(point=True, strokeWidth=3).encode(
            x=alt.X("mes:N", title=None, sort=months, axis=alt.Axis(labelAngle=-35)),
            y=alt.Y("valor:Q", title="R$", axis=alt.Axis(format="~s")),
            color=alt.Color("tipo:N", title=None, scale=alt.Scale(domain=["Entradas", "Saídas"], range=[PURPLE, LILAC])),
            tooltip=[alt.Tooltip("mes:N", title="Mês"), alt.Tooltip("tipo:N", title="Tipo"), alt.Tooltip("valor:Q", format=",.2f", title="Valor")],
        ).properties(height=310)
        st.altair_chart(chart, width="stretch")
    with right:
        st.subheader("Despesas por categoria")
        st.caption("Distribuição dos débitos")
        categories = tx[tx.tipo == "Débito"].groupby("categoria", as_index=False)["valor"].sum().sort_values("valor", ascending=False)
        chart = alt.Chart(categories).mark_bar(color=PURPLE, cornerRadiusEnd=5).encode(
            y=alt.Y("categoria:N", sort="-x", title=None),
            x=alt.X("valor:Q", title=None, axis=alt.Axis(format="~s")),
            tooltip=["categoria:N", alt.Tooltip("valor:Q", format=",.2f", title="Valor")],
        ).properties(height=310)
        st.altair_chart(chart, width="stretch")

    left, right = st.columns([1, 1.55], gap="large")
    with left:
        st.subheader("Saúde financeira")
        st.caption("Fotografia da seleção em 31 out 2026")
        health = pd.DataFrame({"saude": ["Excelente", "Boa", "Atenção"]})
        counts = clients.saude.value_counts().rename_axis("saude").reset_index(name="clientes")
        health = health.merge(counts, how="left", on="saude").fillna(0)
        chart = alt.Chart(health).mark_arc(innerRadius=72, outerRadius=105).encode(
            theta="clientes:Q",
            color=alt.Color("saude:N", title=None, scale=alt.Scale(domain=["Excelente", "Boa", "Atenção"], range=[PURPLE, LILAC, PLUM])),
            tooltip=["saude:N", "clientes:Q"],
        ).properties(height=260)
        st.altair_chart(chart, width="stretch")
    with right:
        st.subheader("Resultado por cidade")
        st.caption("Entradas menos saídas no período filtrado")
        city = tx.pivot_table(index="cidade", columns="tipo", values="valor", aggfunc="sum", fill_value=0).reset_index()
        city["resultado"] = city.get("Crédito", 0) - city.get("Débito", 0)
        city["clientes"] = city.cidade.map(clients.cidade.value_counts()).fillna(0).astype(int)
        city = city.sort_values("resultado", ascending=False)
        st.dataframe(city[["cidade", "clientes", "resultado"]], hide_index=True, width="stretch",
                     column_config={"cidade": "Cidade", "clientes": "Clientes", "resultado": st.column_config.NumberColumn("Resultado (R$)", format="R$ %.2f")})
        csv = city[["cidade", "clientes", "Crédito", "Débito", "resultado"]].rename(columns={"Crédito": "entradas", "Débito": "saidas"}).to_csv(index=False, sep=";").encode("utf-8-sig")
        st.download_button("Exportar resumo em CSV", csv, "indicadores-financeiros.csv", "text/csv")

    st.markdown(f'<div class="note"><strong>Base sintética.</strong> {meta["clients"]} clientes, {meta["accounts"]} contas, {meta["transactions"]:,} transações e {meta["loans"]} empréstimos. Resultado é entradas menos saídas; não representa lucro contábil.</div>'.replace(f'{meta["transactions"]:,}', f'{meta["transactions"]:,}'.replace(',', '.')), unsafe_allow_html=True)


def show_clients(clients: pd.DataFrame, loans: pd.DataFrame) -> None:
    st.markdown('<div class="eyebrow">PERFIL DA CARTEIRA</div>', unsafe_allow_html=True)
    st.title("Clientes e risco")
    st.markdown('<p class="subtitle">Saldos, dívidas e classificações na fotografia de 31 out 2026.</p>', unsafe_allow_html=True)
    cols = st.columns(4)
    cols[0].metric("Clientes", len(clients))
    cols[1].metric("Renda média mensal", brl(clients.renda_mensal.mean() if len(clients) else 0, True))
    cols[2].metric("Saldo devedor", brl(clients.saldo_devedor.sum(), True))
    cols[3].metric("Risco alto", int((clients.risco == "Alto").sum()))
    left, right = st.columns(2, gap="large")
    with left:
        st.subheader("Faixas de risco")
        risks = pd.DataFrame({"risco": ["Baixo", "Moderado", "Alto"]})
        risks = risks.merge(clients.risco.value_counts().rename_axis("risco").reset_index(name="clientes"), how="left", on="risco").fillna(0)
        st.altair_chart(alt.Chart(risks).mark_bar(color=PURPLE, cornerRadiusEnd=5).encode(
            x=alt.X("clientes:Q", title="Clientes"), y=alt.Y("risco:N", sort=["Baixo", "Moderado", "Alto"], title=None), tooltip=["risco:N", "clientes:Q"]
        ).properties(height=230), width="stretch")
    with right:
        st.subheader("Empréstimos por status")
        loan = loans.groupby("status", as_index=False)["quantidade"].sum()
        st.altair_chart(alt.Chart(loan).mark_bar(color=LILAC, cornerRadiusEnd=5).encode(
            x=alt.X("quantidade:Q", title="Empréstimos"), y=alt.Y("status:N", title=None), tooltip=["status:N", "quantidade:Q"]
        ).properties(height=230), width="stretch")
    st.subheader("Base de clientes")
    query = st.text_input("Buscar cliente ou cidade", placeholder="Digite um nome ou cidade")
    filtered = clients.copy()
    if query:
        filtered = filtered[filtered.nome.str.contains(query, case=False, regex=False) | filtered.cidade.str.contains(query, case=False, regex=False)]
    filtered["prioridade"] = filtered.risco.map({"Alto": 0, "Moderado": 1, "Baixo": 2})
    filtered = filtered.sort_values(["prioridade", "saldo_devedor"], ascending=[True, False])
    st.dataframe(filtered[["nome", "cidade", "renda_mensal", "saldo_total", "saldo_devedor", "risco"]],
                 hide_index=True, width="stretch", height=480,
                 column_config={"nome": "Cliente", "cidade": "Cidade", "renda_mensal": st.column_config.NumberColumn("Renda mensal", format="R$ %.2f"), "saldo_total": st.column_config.NumberColumn("Saldo", format="R$ %.2f"), "saldo_devedor": st.column_config.NumberColumn("Dívida", format="R$ %.2f"), "risco": "Risco"})
    st.caption("Risco é uma regra descritiva para demonstração; não é um modelo de concessão de crédito.")


def show_method(meta: dict) -> None:
    st.markdown('<div class="eyebrow">TRANSPARÊNCIA</div>', unsafe_allow_html=True)
    st.title("Metodologia")
    st.markdown('<p class="subtitle">Como a base sintética, as consultas SQL e o dashboard se conectam.</p>', unsafe_allow_html=True)
    st.markdown("""<div class="note"><strong>Dados 100% fictícios.</strong> A geração usa semente fixa, permite reprodução e não representa pessoas, contas ou movimentações reais.</div>""", unsafe_allow_html=True)
    st.write("")
    st.subheader("Definições")
    st.markdown("""
- **Entradas e saídas:** soma dos créditos e débitos registrados. A simulação não gera transferências internas.
- **Resultado:** entradas menos saídas no período filtrado. Não é lucro contábil.
- **Risco:** classificação demonstrativa a partir de score fictício, atraso, dívida/renda e gasto médio recente.
- **Saúde financeira:** comparação ilustrativa entre saldo, renda mensal e saldo devedor.
""")
    st.subheader("Período e fotografia")
    st.write(f"As transações cobrem {meta['first_month']} a {meta['last_month']}. Saldo, dívida e classificações são uma fotografia de {meta['as_of']}; o filtro de período altera apenas os indicadores de movimentação.")
    st.subheader("Reproduzir")
    st.code("python scripts/build_data.py\npython scripts/run_queries.py", language="bash")
    st.link_button("Ver código e dados no GitHub", "https://github.com/sabrinayokoyama1/project_advanced_sql")


def main() -> None:
    meta, transactions, clients, loans = load_data()
    with st.sidebar:
        st.markdown('<div class="brand-title">◈ Indicadores<br>Financeiros</div><div class="brand-subtitle">PROJETO DE ANÁLISE</div>', unsafe_allow_html=True)
        page = st.radio("Explorar", ["Visão geral", "Clientes", "Metodologia"], label_visibility="collapsed")
        st.divider()
        period = st.selectbox("Período", ["Últimos 12 meses", "Ano de 2026", "Ano de 2025", "Todo o período"], disabled=page == "Metodologia")
        city = st.selectbox("Cidade", ["Todas as cidades"] + sorted(clients.cidade.unique().tolist()), disabled=page == "Metodologia")
        st.caption("Dados fictícios · Referência em 31 out 2026")
    all_months = sorted(transactions.mes.unique().tolist())
    months = {"Últimos 12 meses": all_months[-12:], "Ano de 2026": [m for m in all_months if m.startswith("2026")], "Ano de 2025": [m for m in all_months if m.startswith("2025")], "Todo o período": all_months}[period]
    selected_clients = clients if city == "Todas as cidades" else clients[clients.cidade == city]
    selected_tx = transactions[transactions.mes.isin(months)]
    selected_loans = loans
    if city != "Todas as cidades":
        selected_tx = selected_tx[selected_tx.cidade == city]
        selected_loans = loans[loans.cidade == city]
    if page == "Visão geral":
        show_overview(selected_tx, selected_clients, months, meta)
    elif page == "Clientes":
        show_clients(selected_clients, selected_loans)
    else:
        show_method(meta)


if __name__ == "__main__":
    main()
