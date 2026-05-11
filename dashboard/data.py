import os

import pandas as pd
import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account

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

    return df
