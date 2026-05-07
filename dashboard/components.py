import base64
import os

import pandas as pd
import plotly.express as px
import streamlit as st

# ── Caminhos das logos ────────────────────────────────────────────────────────

_ASSETS = os.path.join(os.path.dirname(__file__), "assets")
LOGO_CLARA  = os.path.join(_ASSETS, "logo_preta.png")
LOGO_ESCURA = os.path.join(_ASSETS, "logo_branca.png")

COLOR_MAP = {"Vídeo": "#1F77B4", "Áudio": "#FF7F0E", "Display": "#2CA02C"}


# ── Logo ──────────────────────────────────────────────────────────────────────

def _imagem_base64(caminho: str) -> str:
    with open(caminho, "rb") as f:
        return base64.b64encode(f.read()).decode()


def exibir_logo() -> None:
    existe_clara  = os.path.exists(LOGO_CLARA)
    existe_escura = os.path.exists(LOGO_ESCURA)

    if not existe_clara and not existe_escura:
        return

    caminho_claro  = LOGO_CLARA  if existe_clara  else LOGO_ESCURA
    caminho_escuro = LOGO_ESCURA if existe_escura else LOGO_CLARA

    clara_b64  = _imagem_base64(caminho_claro)
    escura_b64 = _imagem_base64(caminho_escuro)

    st.markdown(
        f"""
        <style>
            .logo-container {{
                display: flex;
                justify-content: flex-start;
                margin-bottom: 0.75rem;
            }}
            .logo-container img {{
                width: min(260px, 60vw);
                height: auto;
            }}
            .logo-dark {{ display: none; }}
            @media (prefers-color-scheme: dark) {{
                .logo-light {{ display: none; }}
                .logo-dark  {{ display: block; }}
            }}
        </style>
        <div class="logo-container">
            <img class="logo-light" src="data:image/png;base64,{clara_b64}">
            <img class="logo-dark"  src="data:image/png;base64,{escura_b64}">
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Tema ──────────────────────────────────────────────────────────────────────

def _tema() -> str:
    return "plotly_dark" if st.get_option("theme.base") == "dark" else "plotly_white"


def _layout(fig, altura: int = 500):
    fig.update_layout(
        height=altura,
        template=_tema(),
        margin=dict(l=20, r=60, t=60, b=20),
    )
    return fig


# ── KPIs ──────────────────────────────────────────────────────────────────────

def kpis(df: pd.DataFrame) -> None:
    imp    = df["impressions"].sum()
    clk    = df["clicks"].sum()
    bud    = df["budget"].sum()
    conv   = df["conversions"].sum()
    ctr    = (clk / imp * 100) if imp else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Impressões",    f"{imp:,.0f}")
    c2.metric("Cliques",       f"{clk:,.0f}")
    c3.metric("CTR médio",     f"{ctr:.2f}%")
    c4.metric("Valor gasto",   f"R$ {bud:,.2f}")
    c5.metric("Conversões",    f"{conv:,.0f}")


# ── Gráficos de barra (helper interno) ───────────────────────────────────────

def _grafico_barras(
    df: pd.DataFrame,
    coluna: str,
    titulo: str,
    fmt_texto,
) -> None:
    df_plot = df.sort_values(coluna, ascending=False).copy()
    df_plot["_texto"] = df_plot[coluna].map(fmt_texto)

    fig = px.bar(
        df_plot,
        x=coluna,
        y="campaign_name",
        color="Tipo_Midia",
        orientation="h",
        text="_texto",
        title=titulo,
        labels={coluna: coluna, "campaign_name": "Campanha", "Tipo_Midia": "Tipo"},
        color_discrete_map=COLOR_MAP,
        height=max(420, len(df_plot) * 32),
    )
    fig.update_traces(textposition="outside", cliponaxis=False, textfont_size=11)
    fig.update_layout(
        yaxis={"categoryorder": "total ascending"},
        template=_tema(),
        margin=dict(l=20, r=80, t=60, b=20),
    )
    st.plotly_chart(fig, width="stretch")


def grafico_impressoes(df: pd.DataFrame) -> None:
    _grafico_barras(df, "impressions", "Impressões por campanha", lambda v: f"{v:,.0f}")


def grafico_cliques(df: pd.DataFrame) -> None:
    _grafico_barras(df, "clicks", "Cliques por campanha", lambda v: f"{v:,.0f}")


def grafico_budget(df: pd.DataFrame) -> None:
    _grafico_barras(df, "budget", "Valor gasto por campanha (R$)", lambda v: f"R$ {v:,.2f}")


# ── Gráfico de rosca (tipo de mídia) ─────────────────────────────────────────

def grafico_tipo_midia(df: pd.DataFrame, coluna: str = "impressions", titulo: str | None = None) -> None:
    label_map = {
        "impressions": "Impressões",
        "clicks":      "Cliques",
        "budget":      "Valor gasto (R$)",
    }
    titulo = titulo or f"Distribuição por tipo de mídia — {label_map.get(coluna, coluna)}"

    resumo = df.groupby("Tipo_Midia", as_index=False)[coluna].sum()

    fig = px.pie(
        resumo,
        names="Tipo_Midia",
        values=coluna,
        title=titulo,
        color="Tipo_Midia",
        color_discrete_map=COLOR_MAP,
        hole=0.4,
    )
    fig.update_traces(textinfo="label+percent+value")
    fig = _layout(fig, altura=420)
    st.plotly_chart(fig, width="stretch")


# ── Tabela resumo (métricas somáveis) ────────────────────────────────────────

def tabela_resumo(df: pd.DataFrame) -> None:
    resumo = (
        df.groupby("Tipo_Midia", as_index=False)
        .agg(
            Campanhas=("campaign_name", "count"),
            Impressões=("impressions", "sum"),
            Cliques=("clicks", "sum"),
            Valor_Gasto=("budget", "sum"),
            Conversões=("conversions", "sum"),
            Video_Starts=("videoStarts", "sum"),
            Video_Completions=("videoCompletions", "sum"),
            Audio_Starts=("audioStarts", "sum"),
            Audio_Completions=("audioCompletions", "sum"),
        )
    )

    total = resumo.select_dtypes("number").sum()
    total_row = pd.DataFrame([["TOTAL"] + total.tolist()], columns=resumo.columns)
    resumo = pd.concat([resumo, total_row], ignore_index=True)

    resumo["CTR (%)"]  = (resumo["Cliques"] / resumo["Impressões"].replace(0, pd.NA) * 100).round(2)
    resumo["VCR (%)"]  = (resumo["Video_Completions"] / resumo["Video_Starts"].replace(0, pd.NA) * 100).round(2)
    resumo["ACR (%)"]  = (resumo["Audio_Completions"] / resumo["Audio_Starts"].replace(0, pd.NA) * 100).round(2)
    resumo["CPM (R$)"] = (resumo["Valor_Gasto"] / resumo["Impressões"].replace(0, pd.NA) * 1000).round(2)
    resumo["CPC (R$)"] = (resumo["Valor_Gasto"] / resumo["Cliques"].replace(0, pd.NA)).round(2)

    resumo = resumo.rename(columns={"Tipo_Midia": "Tipo", "Valor_Gasto": "Valor Gasto (R$)"})

    st.dataframe(resumo, hide_index=True, width="stretch")


# ── Tabela detalhada ──────────────────────────────────────────────────────────

def tabela_campanhas(df: pd.DataFrame) -> None:
    colunas = [
        "campaign_name", "Tipo_Midia", "impressions", "clicks",
        "CTR (%)", "budget", "CPM (R$)", "CPC (R$)",
        "conversions", "VCR (%)", "ACR (%)",
    ]
    df_exibir = df[[c for c in colunas if c in df.columns]].copy()
    df_exibir = df_exibir.rename(columns={
        "campaign_name": "Campanha",
        "Tipo_Midia":    "Tipo",
        "impressions":   "Impressões",
        "clicks":        "Cliques",
        "budget":        "Valor Gasto (R$)",
        "conversions":   "Conversões",
    })
    st.dataframe(
        df_exibir.sort_values("Impressões", ascending=False),
        hide_index=True,
        width="stretch",
    )
