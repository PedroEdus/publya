import streamlit as st


def aplicar_tema() -> None:
    """
    Injeta CSS com os tokens do design system Brasil Terrenos / Publya.
    Fontes: Manrope (sans) + JetBrains Mono (números).
    """
    st.markdown(
        """
        <style>
        /* ── Fontes ──────────────────────────────────────────────────── */
        @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

        html, body, [class*="css"], .stApp {
            font-family: 'Manrope', -apple-system, BlinkMacSystemFont, sans-serif !important;
        }

        /* ── KPI tiles ───────────────────────────────────────────────── */
        [data-testid="metric-container"] {
            background: #1c1c1c;
            border-radius: 8px;
            padding: 16px 18px !important;
        }
        [data-testid="stMetricLabel"] {
            font-family: 'Manrope', sans-serif !important;
            font-size: 14px !important;
            font-weight: 400 !important;
            color: rgba(255,255,255,0.72) !important;
        }
        [data-testid="stMetricValue"] {
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 28px !important;
            font-weight: 600 !important;
            letter-spacing: -0.01em !important;
            font-variant-numeric: tabular-nums !important;
            color: #ffffff !important;
        }
        [data-testid="stMetricDelta"] {
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 12px !important;
        }

        /* ── Sidebar ─────────────────────────────────────────────────── */
        [data-testid="stSidebar"] {
            background: #1c1c1c !important;
        }
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] .stSelectbox label,
        [data-testid="stSidebar"] .stMultiSelect label,
        [data-testid="stSidebar"] .stDateInput label {
            font-size: 13px !important;
            color: rgba(255,255,255,0.72) !important;
            font-weight: 400 !important;
        }
        [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"],
        [data-testid="stSidebar"] .stMultiSelect div[data-baseweb="select"],
        [data-testid="stSidebar"] .stDateInput input {
            background: #262626 !important;
            border: 1px solid #3a3a3a !important;
            border-radius: 8px !important;
            font-family: 'Manrope', sans-serif !important;
            font-size: 14px !important;
        }
        [data-testid="stSidebarHeader"] {
            font-size: 18px !important;
            font-weight: 600 !important;
        }

        /* ── Abas ────────────────────────────────────────────────────── */
        .stTabs [data-baseweb="tab-list"] {
            border-bottom: 1px solid #2a2a2a !important;
            gap: 24px !important;
        }
        .stTabs [data-baseweb="tab"] {
            font-family: 'Manrope', sans-serif !important;
            font-size: 14px !important;
            color: rgba(255,255,255,0.72) !important;
            padding: 10px 2px !important;
            border-bottom: 2px solid transparent !important;
        }
        .stTabs [data-baseweb="tab"]:hover {
            color: #ffffff !important;
        }
        .stTabs [aria-selected="true"] {
            color: #ffffff !important;
            border-bottom-color: #008140 !important;
            font-weight: 500 !important;
        }
        .stTabs [data-baseweb="tab-highlight"] {
            background: #008140 !important;
            height: 2px !important;
        }

        /* ── Títulos e textos ────────────────────────────────────────── */
        h1 {
            font-family: 'Manrope', sans-serif !important;
            font-size: 2rem !important;
            font-weight: 700 !important;
            letter-spacing: -0.005em !important;
        }
        h2, h3 {
            font-family: 'Manrope', sans-serif !important;
            font-weight: 600 !important;
        }
        [data-testid="stCaptionContainer"] {
            color: rgba(255,255,255,0.50) !important;
            font-size: 14px !important;
        }

        /* ── Tabelas (dataframes) ────────────────────────────────────── */
        [data-testid="stDataFrame"] table {
            font-family: 'Manrope', sans-serif !important;
            font-size: 13px !important;
        }
        [data-testid="stDataFrame"] th {
            color: rgba(255,255,255,0.50) !important;
            font-size: 12px !important;
            font-weight: 500 !important;
            background: transparent !important;
        }
        [data-testid="stDataFrame"] td {
            font-variant-numeric: tabular-nums;
        }
        /* números em mono nas colunas com valores */
        [data-testid="stDataFrame"] td[data-type="float"],
        [data-testid="stDataFrame"] td[data-type="int"] {
            font-family: 'JetBrains Mono', monospace !important;
        }

        /* ── Divider ─────────────────────────────────────────────────── */
        hr {
            border-color: #2a2a2a !important;
            margin: 24px 0 !important;
        }

        /* ── Inputs gerais ───────────────────────────────────────────── */
        input, select, textarea {
            font-family: 'Manrope', sans-serif !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
