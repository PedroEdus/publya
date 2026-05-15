import base64
import os
from datetime import datetime

import numpy as np
import pandas as pd
import requests
from dotenv import load_dotenv
from google.api_core.exceptions import BadRequest
from google.cloud import bigquery

load_dotenv()

PROJECT_ID     = os.getenv("GCP_PROJECT_ID")
DATASET_SILVER = os.getenv("BQ_DATASET_SILVER", "buriti_marketing_silver")
TABELA_SILVER  = "publya_campanhas"

if not PROJECT_ID:
    raise ValueError("GCP_PROJECT_ID não encontrado no .env ou nas variáveis de ambiente")

CONTAS = [
    {
        "client_id": os.getenv("PUBLYA_CLIENT_ID_1"),
        "token":     os.getenv("PUBLYA_TOKEN_1"),
        "email":     os.getenv("PUBLYA_EMAIL_1"),
    },
    {
        "client_id": os.getenv("PUBLYA_CLIENT_ID_2"),
        "token":     os.getenv("PUBLYA_TOKEN_2"),
        "email":     os.getenv("PUBLYA_EMAIL_2"),
    },
]

METRIC_COLS = [
    "budget", "impressions", "clicks", "ctr", "cpc", "cpm",
    "reach", "cpma", "frequency", "viewability", "conversions",
    "vcr", "cpv", "videoStarts", "video25Completions", "video50Completions",
    "video75Completions", "videoCompletions", "trueViews", "trueViewsRate",
    "audioStarts", "audio25Completions", "audio50Completions",
    "audio75Completions", "audioCompletions", "acr", "ecpcl", "cpa",
]

COLUNAS_REMOVER = [
    "video25Completions", "video50Completions", "video75Completions",
    "audio25Completions", "audio50Completions", "audio75Completions",
    "trueViews", "trueViewsRate",
    "ctr", "cpc", "cpm", "cpma",
    "viewability", "cpv", "vcr", "ecpcl", "cpa",
    "platform", "acr", "client_id",
]

# Schema explícito da tabela silver — garante que colunas de data são
# preservadas como TIMESTAMP mesmo quando todos os valores são nulos
# (autodetect=True descarta colunas all-null, perdendo data_inicio/data_fim).
SCHEMA_SILVER = [
    bigquery.SchemaField("campaign_id",       "STRING"),
    bigquery.SchemaField("campaign_name",     "STRING"),
    bigquery.SchemaField("Tipo_Midia",        "STRING"),
    bigquery.SchemaField("budget",            "FLOAT64"),
    bigquery.SchemaField("impressions",       "FLOAT64"),
    bigquery.SchemaField("clicks",            "FLOAT64"),
    bigquery.SchemaField("reach",             "FLOAT64"),
    bigquery.SchemaField("frequency",         "FLOAT64"),
    bigquery.SchemaField("conversions",       "FLOAT64"),
    bigquery.SchemaField("videoStarts",       "FLOAT64"),
    bigquery.SchemaField("videoCompletions",  "FLOAT64"),
    bigquery.SchemaField("audioStarts",       "FLOAT64"),
    bigquery.SchemaField("audioCompletions",  "FLOAT64"),
    bigquery.SchemaField("data_inicio",       "TIMESTAMP"),
    bigquery.SchemaField("data_fim",          "TIMESTAMP"),
    bigquery.SchemaField("data_carga",        "TIMESTAMP"),
    bigquery.SchemaField("origem_fonte",      "STRING"),
]

client = bigquery.Client(project=PROJECT_ID)


# ── Autenticação ──────────────────────────────────────────────────────────────

def criar_headers(token: str, client_id: str, email: str) -> dict:
    user_data_b64 = base64.b64encode(f"{client_id}:{email}".encode()).decode()
    return {
        "Authorization": f"Bearer {token}",
        "User-Data":     user_data_b64,
        "Content-Type":  "application/json",
    }


# ── Extração ──────────────────────────────────────────────────────────────────

ITENS_POR_PAGINA = 20


def extrair_todas_campanhas(headers: dict) -> list:
    """
    Percorre todas as páginas usando o campo `pages` da resposta.
    A API retorna: total, page, itensPerPage, pages, items.
    """
    url   = "https://api.publya.com/kermit/leap/reports/external/campaigns"
    todas = []
    pagina = 1

    while True:
        print(f"  Buscando página {pagina}...")
        resp = requests.get(url, headers=headers, params={"page": pagina, "itemsPerPage": ITENS_POR_PAGINA})

        if resp.status_code == 401:
            print("  Erro 401: verifique token ou User-Data")
            break
        elif resp.status_code != 200:
            print(f"  Erro {resp.status_code} ao listar campanhas")
            break

        dados       = resp.json()
        items       = dados.get("items", [])
        total_pages = dados.get("pages", 1)

        todas.extend(items)
        print(f"  {len(items)} campanhas na página {pagina}/{total_pages} (total: {len(todas)})")

        if pagina >= total_pages:
            break

        pagina += 1

    print(f"  Total de campanhas listadas: {len(todas)}")
    return todas


def consultar_detalhe(campanha_id: str, headers: dict) -> dict | None:
    url  = f"https://api.publya.com/kermit/leap/reports/external/campaigns/{campanha_id}"
    resp = requests.get(url, headers=headers)

    if resp.status_code == 200:
        return resp.json()
    elif resp.status_code in (404, 501):
        print(f"  ID {campanha_id}: rota não implementada")
    else:
        print(f"  ID {campanha_id}: erro {resp.status_code}")
    return None


def coletar_dados_conta(conta: dict) -> list[dict]:
    headers   = criar_headers(conta["token"], conta["client_id"], conta["email"])
    campanhas = extrair_todas_campanhas(headers)
    resultado = []

    for camp in campanhas:
        cid   = camp["id"]
        cname = camp.get("name", f"Campanha {cid}")
        plat  = camp.get("platform", {})
        cplat = plat.get("name", "") if isinstance(plat, dict) else str(plat)

        print(f"  -> [{cid}] {cname}")
        detalhe = consultar_detalhe(cid, headers)
        if detalhe is None:
            continue

        resultado.append({
            "client_id":     conta["client_id"],
            "campaign_id":   cid,
            "campaign_name": cname,
            "platform":      cplat,
            **(detalhe if isinstance(detalhe, dict) else {}),
        })

    print(f"  {len(resultado)} campanhas coletadas (client_id={conta['client_id']})")
    return resultado


# ── Transformação ─────────────────────────────────────────────────────────────

def extrair_datas_daily(item: dict) -> tuple[str | None, str | None]:
    """Extrai data_min e data_max a partir do campo 'daily' do detalhe da campanha."""
    daily = item.get("daily", {})
    if not daily:
        return None, None

    todas_as_datas = [
        entrada["date"]
        for entries in daily.values()
        for entrada in entries
        if isinstance(entrada, dict) and "date" in entrada
    ]

    if not todas_as_datas:
        return None, None

    return min(todas_as_datas), max(todas_as_datas)


def tabular_metricas(data: list[dict]) -> pd.DataFrame:
    rows = []
    for item in data:
        metrics             = item.get("metrics", {})
        data_min, data_max  = extrair_datas_daily(item)
        rows.append({
            "client_id":     item.get("client_id", ""),
            "campaign_id":   item["campaign_id"],
            "campaign_name": item["campaign_name"],
            "platform":      item.get("platform", ""),
            "data_inicio":   data_min,
            "data_fim":      data_max,
            **{col: metrics.get(col, 0) for col in METRIC_COLS},
        })
    return pd.DataFrame(rows)


def preparar_silver(data: list[dict]) -> pd.DataFrame:
    df = tabular_metricas(data)

    for col in METRIC_COLS:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df["Tipo_Midia"] = np.where(
        df["videoStarts"] != 0, "Vídeo",
        np.where(df["audioStarts"] != 0, "Áudio", "Display")
    )

    df["campaign_id"]   = df["campaign_id"].astype(str)
    df["campaign_name"] = df["campaign_name"].astype(str)
    df["data_inicio"]   = pd.to_datetime(df["data_inicio"], errors="coerce")
    df["data_fim"]      = pd.to_datetime(df["data_fim"], errors="coerce")
    df["data_carga"]    = datetime.now()
    df["origem_fonte"]  = "PUBLYA_API"

    df = df.drop(columns=[c for c in COLUNAS_REMOVER if c in df.columns])

    return df


# ── Carga ─────────────────────────────────────────────────────────────────────

def garantir_dataset(dataset_id: str, location: str = "US") -> None:
    dataset_ref = bigquery.Dataset(f"{PROJECT_ID}.{dataset_id}")
    dataset_ref.location = location
    client.create_dataset(dataset_ref, exists_ok=True)
    print(f"  Dataset pronto: {dataset_id}")


def carregar_bigquery(
    df: pd.DataFrame,
    dataset_id: str,
    table_id: str,
    modo: str = "WRITE_TRUNCATE",
    schema: list | None = None,
) -> None:
    table_full = f"{PROJECT_ID}.{dataset_id}.{table_id}"
    job_config = bigquery.LoadJobConfig(
        write_disposition=modo,
        schema=schema if schema else None,
        autodetect=schema is None,   # autodetect só quando schema não é fornecido
    )
    job = client.load_table_from_dataframe(df, table_full, job_config=job_config)
    job.result()
    print(f"  Carga concluída: {table_full} ({len(df)} linhas)")


def carregar_com_staging(df: pd.DataFrame, dataset_id: str, table_id: str) -> None:
    """
    Carrega via staging + MERGE para proteger a tabela final.

    Fluxo:
      1. Sobe os dados em uma tabela staging (WRITE_TRUNCATE).
         Se falhar aqui, a tabela final não é tocada.
      2. Executa MERGE: atualiza campanhas existentes, insere novas.
      3. Apaga a tabela staging.
    """
    staging_id = f"{table_id}_staging"

    print(f"  Carregando staging ({staging_id})...")
    carregar_bigquery(df, dataset_id, staging_id, modo="WRITE_TRUNCATE", schema=SCHEMA_SILVER)

    # Colunas fixas do schema silver — INSERT explícito evita falhas por
    # divergência de contagem entre staging e tabela final.
    _COLS = [
        "campaign_id", "campaign_name", "Tipo_Midia",
        "budget", "impressions", "clicks", "reach", "frequency", "conversions",
        "videoStarts", "videoCompletions", "audioStarts", "audioCompletions",
        "data_inicio", "data_fim", "data_carga", "origem_fonte",
    ]
    _cols_sql    = ", ".join(_COLS)
    _s_cols_sql  = ", ".join(f"S.{c}" for c in _COLS)

    merge_sql = f"""
        MERGE `{PROJECT_ID}.{dataset_id}.{table_id}` T
        USING `{PROJECT_ID}.{dataset_id}.{staging_id}` S
        ON T.campaign_id = S.campaign_id AND T.Tipo_Midia = S.Tipo_Midia
        WHEN MATCHED THEN UPDATE SET
            campaign_name    = S.campaign_name,
            impressions      = S.impressions,
            clicks           = S.clicks,
            budget           = S.budget,
            reach            = S.reach,
            frequency        = S.frequency,
            conversions      = S.conversions,
            videoStarts      = S.videoStarts,
            videoCompletions = S.videoCompletions,
            audioStarts      = S.audioStarts,
            audioCompletions = S.audioCompletions,
            data_inicio      = S.data_inicio,
            data_fim         = S.data_fim,
            data_carga       = S.data_carga,
            origem_fonte     = S.origem_fonte
        WHEN NOT MATCHED THEN INSERT ({_cols_sql})
        VALUES ({_s_cols_sql})
    """

    print("  Executando MERGE na tabela final...")
    try:
        client.query(merge_sql).result()
        print(f"  MERGE concluído: {table_id}")
    except BadRequest as e:
        err = str(e)
        schema_mismatch = any(k in err for k in (
            "Unrecognized name",
            "wrong column count",
            "not found in table",
        )) or "not found" in err.lower()
        if schema_mismatch:
            print(f"  Schema divergente ({err[:120]}) — recriando tabela com WRITE_TRUNCATE...")
            carregar_bigquery(df, dataset_id, table_id, modo="WRITE_TRUNCATE", schema=SCHEMA_SILVER)
            print(f"  Tabela recriada com novo schema: {table_id}")
        else:
            raise

    client.delete_table(f"{PROJECT_ID}.{dataset_id}.{staging_id}", not_found_ok=True)
    print(f"  Staging removido: {staging_id}")


# ── Execução ──────────────────────────────────────────────────────────────────

def main():
    todos_os_dados: list[dict] = []

    for conta in CONTAS:
        if not all([conta["client_id"], conta["token"], conta["email"]]):
            print(f"  Conta ignorada — variáveis de ambiente incompletas")
            continue

        print(f"\n{'='*55}")
        print(f"Coletando client_id={conta['client_id']}")
        print(f"{'='*55}")
        todos_os_dados.extend(coletar_dados_conta(conta))

    if not todos_os_dados:
        print("Nenhum dado coletado. Verifique autenticação.")
        raise SystemExit(1)

    print(f"\n{len(todos_os_dados)} campanhas no total. Preparando carga...")
    df_silver = preparar_silver(todos_os_dados)

    print(f"\nPrévia ({len(df_silver)} linhas):")
    print(df_silver[["campaign_name", "Tipo_Midia", "impressions", "clicks"]].to_string(index=False))

    print("\nGarantindo dataset no BigQuery...")
    garantir_dataset(DATASET_SILVER)

    print("Carregando SILVER via staging...")
    carregar_com_staging(df_silver, DATASET_SILVER, TABELA_SILVER)

    print("\nProcesso finalizado.")


if __name__ == "__main__":
    main()
