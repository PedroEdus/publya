# Publya — Dashboard de Campanhas

Pipeline de dados e dashboard para monitoramento de campanhas da plataforma [Publya](https://publya.com).

## Visão geral

```
Publya API → ETL (Python) → BigQuery → Streamlit Dashboard
```

O ETL roda automaticamente toda sexta-feira via GitHub Actions e atualiza a tabela no BigQuery. O dashboard consome esses dados e exibe métricas, gráficos e tabelas por campanha e tipo de mídia.

---

## Estrutura do projeto

```
publya/
├── .github/
│   └── workflows/
│       └── etl_publya.yml       # Agendamento e execução do ETL
├── app.py                       # Entrada do Streamlit
├── components.py                # Gráficos, KPIs e tabelas
├── data.py                      # Conexão e consulta ao BigQuery
├── publya_campanhas_bq.py       # ETL: extração, transformação e carga
└── requirements.txt
```

---

## ETL

O script `publya_campanhas_bq.py` realiza:

1. **Extração** — consulta a API da Publya para todas as contas configuradas
2. **Transformação** — classifica campanhas por tipo de mídia (Vídeo, Áudio, Display) e limpa as métricas
3. **Carga** — envia o resultado para a tabela `buriti_marketing_silver.publya_campanhas` no BigQuery

**Agendamento:** toda sexta-feira às 08:00 UTC via GitHub Actions.  
Também pode ser disparado manualmente em **Actions → Run workflow**.

---

## Dashboard

Métricas exibidas:

- Impressões, Cliques, CTR, Valor Gasto, Conversões
- CPM, CPC, VCR (Video Completion Rate), ACR (Audio Completion Rate)

Filtros disponíveis por tipo de mídia e por campanha.

---

## Configuração local

**1. Clone o repositório e instale as dependências:**
```bash
git clone https://github.com/PedroEdus/publya.git
cd publya
pip install -r requirements.txt
```

**2. Crie um arquivo `.env` na raiz:**
```env
GCP_PROJECT_ID=buriti-marketing-analytics
BQ_DATASET_SILVER=buriti_marketing_silver

PUBLYA_CLIENT_ID_1=
PUBLYA_TOKEN_1=
PUBLYA_EMAIL_1=

PUBLYA_CLIENT_ID_2=
PUBLYA_TOKEN_2=
PUBLYA_EMAIL_2=
```

**3. Configure as credenciais do GCP:**
```bash
export GOOGLE_APPLICATION_CREDENTIALS=/caminho/para/sa_key.json
```

**4. Rode o ETL:**
```bash
python publya_campanhas_bq.py
```

**5. Rode o dashboard:**
```bash
streamlit run app.py
```

---

## Configuração em produção

### GitHub Actions (ETL)

Cadastre os seguintes secrets em **Settings → Secrets and variables → Actions**:

| Secret | Descrição |
|---|---|
| `GCP_PROJECT_ID` | ID do projeto no GCP |
| `GCP_SA_KEY` | JSON completo da service account |
| `PUBLYA_CLIENT_ID_1` | Client ID da conta 1 |
| `PUBLYA_TOKEN_1` | Token da conta 1 |
| `PUBLYA_EMAIL_1` | E-mail da conta 1 |
| `PUBLYA_CLIENT_ID_2` | Client ID da conta 2 |
| `PUBLYA_TOKEN_2` | Token da conta 2 |
| `PUBLYA_EMAIL_2` | E-mail da conta 2 |

### Streamlit Cloud (Dashboard)

Em **Settings → Secrets**, adicione:

```toml
[gcp_service_account]
type                        = "service_account"
project_id                  = "buriti-marketing-analytics"
private_key_id              = "..."
private_key                 = "-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----\n"
client_email                = "...@buriti-marketing-analytics.iam.gserviceaccount.com"
client_id                   = "..."
auth_uri                    = "https://accounts.google.com/o/oauth2/auth"
token_uri                   = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url        = "..."
```

---

## Permissões necessárias na service account

- `BigQuery Data Editor`
- `BigQuery Job User`
