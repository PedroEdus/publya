import os
import re

import pandas as pd
import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account

_UF_BR = {
    "AC","AL","AP","AM","BA","CE","DF","ES","GO","MA",
    "MT","MS","MG","PA","PB","PR","PE","PI","RJ","RN",
    "RS","RO","RR","SC","SP","SE","TO",
}


def _tipo_lancamento(nome: str) -> str:
    n = str(nome)
    if re.search(r"estoque", n, re.IGNORECASE):
        return "Estoque"
    if re.search(r"lan[cç]amento", n, re.IGNORECASE):
        return "Lançamento"
    return "Outros"


def _extrair_cidade_uf(nome: str) -> tuple:
    """Extrai cidade e UF do padrão NomeCidade/UF no nome da campanha."""
    nome = str(nome)
    m = re.search(r"/\s*([A-Z]{2})\b", nome)
    if not m or m.group(1) not in _UF_BR:
        return None, None
    uf = m.group(1)
    before = nome[: m.start()].strip()
    # Pega o último segmento após separadores (-, –, |, :)
    partes = re.split(r"\s*[-–|:]\s*", before)
    cidade = partes[-1].strip()
    return cidade if cidade else None, uf

PROJECT_ID = "buriti-marketing-analytics"
DATASET    = "buriti_marketing_silver"
TABELA     = "publya_campanhas"


def _criar_client() -> bigquery.Client:
    """
    Localmente usa as credenciais do ambiente (GOOGLE_APPLICATION_CREDENTIALS).
    No Streamlit Cloud usa st.secrets["gcp_service_account"].
    """
    if "gcp_service_account" in st.secrets:
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"]
        )
        return bigquery.Client(credentials=credentials, project=PROJECT_ID)

    return bigquery.Client(project=PROJECT_ID)


@st.cache_data(ttl=3600)
def carregar_campanhas() -> pd.DataFrame:
    client = _criar_client()
    query  = f"SELECT * FROM `{PROJECT_ID}.{DATASET}.{TABELA}`"
    df     = client.query(query).to_dataframe()

    # Agrega linhas onde campaign_name E Tipo_Midia são iguais
    cols_soma = [
        "impressions", "clicks", "budget", "reach", "conversions",
        "videoStarts", "videoCompletions", "audioStarts", "audioCompletions", "frequency",
    ]
    cols_soma = [c for c in cols_soma if c in df.columns]

    agg = {col: "sum" for col in cols_soma}

    if "data_inicio" in df.columns:
        df["data_inicio"] = pd.to_datetime(df["data_inicio"], errors="coerce")
        agg["data_inicio"] = "min"

    if "data_fim" in df.columns:
        df["data_fim"] = pd.to_datetime(df["data_fim"], errors="coerce")
        agg["data_fim"] = "max"

    df = df.groupby(["campaign_name", "Tipo_Midia"], as_index=False).agg(agg)

    # Métricas derivadas
    imp = df["impressions"].replace(0, pd.NA)
    clk = df["clicks"].replace(0, pd.NA)
    vs  = df["videoStarts"].replace(0, pd.NA)
    as_ = df["audioStarts"].replace(0, pd.NA)

    df["CTR (%)"]  = (df["clicks"] / imp * 100).round(2)
    df["CPM (R$)"] = (df["budget"] / imp * 1000).round(2)
    df["CPC (R$)"] = (df["budget"] / clk).round(2)
    df["VCR (%)"]  = (df["videoCompletions"] / vs * 100).round(2)
    df["ACR (%)"]  = (df["audioCompletions"] / as_ * 100).round(2)

    # Estoque vs Lançamento
    df["Tipo_Lancamento"] = df["campaign_name"].map(_tipo_lancamento)

    # Cidade e UF extraídas do padrão "Nome/UF" no nome da campanha
    cidade_uf = df["campaign_name"].map(_extrair_cidade_uf)
    df["Cidade"] = cidade_uf.map(lambda x: x[0])
    df["UF"]     = cidade_uf.map(lambda x: x[1])

    return df
