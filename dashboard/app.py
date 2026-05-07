import streamlit as st

from components import (
    exibir_logo,
    grafico_budget,
    grafico_cliques,
    grafico_impressoes,
    grafico_tipo_midia,
    kpis,
    tabela_campanhas,
    tabela_resumo,
)
from data import carregar_campanhas

st.set_page_config(
    page_title="Publya — Campanhas",
    page_icon="📊",
    layout="wide",
)

# ── Cabeçalho ─────────────────────────────────────────────────────────────────

exibir_logo()
st.title("Campanhas Publya")

# ── Dados ─────────────────────────────────────────────────────────────────────

df = carregar_campanhas()

if df.empty:
    st.warning("Nenhuma campanha encontrada.")
    st.stop()

# ── Filtros ───────────────────────────────────────────────────────────────────

st.sidebar.header("Filtros")

tipos = ["Todos"] + sorted(df["Tipo_Midia"].dropna().unique().tolist())
tipo_sel = st.sidebar.selectbox("Tipo de mídia", tipos)

campanhas_opcoes = sorted(df["campaign_name"].dropna().unique().tolist())
campanhas_sel = st.sidebar.multiselect("Campanhas", campanhas_opcoes)

df_filtrado = df.copy()

if tipo_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Tipo_Midia"] == tipo_sel]

if campanhas_sel:
    df_filtrado = df_filtrado[df_filtrado["campaign_name"].isin(campanhas_sel)]

st.caption(f"{len(df_filtrado)} campanha(s) exibida(s)")

# ── KPIs ──────────────────────────────────────────────────────────────────────

kpis(df_filtrado)
st.divider()

# ── Abas ──────────────────────────────────────────────────────────────────────

aba_imp, aba_clk, aba_val, aba_tab = st.tabs([
    "📢 Impressões",
    "🖱️ Cliques",
    "💰 Valores",
    "📋 Tabela",
])

with aba_imp:
    col1, col2 = st.columns([2, 1])
    with col1:
        grafico_impressoes(df_filtrado)
    with col2:
        grafico_tipo_midia(df_filtrado, coluna="impressions")

with aba_clk:
    col1, col2 = st.columns([2, 1])
    with col1:
        grafico_cliques(df_filtrado)
    with col2:
        grafico_tipo_midia(df_filtrado, coluna="clicks")

with aba_val:
    col1, col2 = st.columns([2, 1])
    with col1:
        grafico_budget(df_filtrado)
    with col2:
        grafico_tipo_midia(df_filtrado, coluna="budget")

with aba_tab:
    st.subheader("Resumo por tipo de mídia")
    tabela_resumo(df_filtrado)

    st.divider()

    st.subheader("Detalhe por campanha")
    tabela_campanhas(df_filtrado)
