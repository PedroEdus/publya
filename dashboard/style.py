import streamlit as st


def aplicar_tema() -> None:
    # Link de fontes separado — mais confiável que @import dentro de style tag
    st.markdown(
        '<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800'
        '&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <style>
        /* ── Fonte global ───────────────────────────────────────────── */
        *, *::before, *::after {
            font-family: 'Manrope', -apple-system, BlinkMacSystemFont, sans-serif !important;
        }

        /* ── KPI tiles — cartão bg-1 ────────────────────────────────── */
        div[data-testid="stMetric"],
        div[data-testid="metric-container"] {
            background: #1c1c1c !important;
            border-radius: 8px !important;
            padding: 16px 18px !important;
            border: none !important;
        }
        div[data-testid="stMetricLabel"] > div,
        div[data-testid="stMetricLabel"] label,
        div[data-testid="stMetricLabel"] p {
            font-size: 13px !important;
            font-weight: 400 !important;
            color: rgba(255,255,255,0.72) !important;
        }
        div[data-testid="stMetricValue"],
        div[data-testid="stMetricValue"] > div {
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 26px !important;
            font-weight: 600 !important;
            letter-spacing: -0.01em !important;
            font-variant-numeric: tabular-nums !important;
            color: #ffffff !important;
        }

        /* ── Sidebar ────────────────────────────────────────────────── */
        section[data-testid="stSidebar"],
        section[data-testid="stSidebar"] > div {
            background-color: #1c1c1c !important;
        }
        section[data-testid="stSidebar"] label {
            font-size: 13px !important;
            color: rgba(255,255,255,0.72) !important;
            font-weight: 400 !important;
        }
        section[data-testid="stSidebar"] .stSelectbox > div,
        section[data-testid="stSidebar"] .stMultiSelect > div,
        section[data-testid="stSidebar"] input[type="text"],
        section[data-testid="stSidebar"] input[type="date"] {
            background: #262626 !important;
            border-color: #3a3a3a !important;
            border-radius: 8px !important;
            font-size: 14px !important;
        }

        /* ── Abas ───────────────────────────────────────────────────── */
        .stTabs [data-baseweb="tab-list"] {
            background: transparent !important;
            border-bottom: 1px solid #2a2a2a !important;
            gap: 20px !important;
        }
        .stTabs [data-baseweb="tab"] {
            font-size: 14px !important;
            color: rgba(255,255,255,0.60) !important;
            background: transparent !important;
            border: none !important;
            padding: 10px 4px !important;
        }
        .stTabs [data-baseweb="tab"]:hover {
            color: #ffffff !important;
            background: transparent !important;
        }
        .stTabs [aria-selected="true"],
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            color: #ffffff !important;
            font-weight: 600 !important;
            background: transparent !important;
        }
        .stTabs [data-baseweb="tab-highlight"],
        .stTabs [data-baseweb="tab-border"] {
            background-color: #008140 !important;
            height: 2px !important;
        }

        /* ── Títulos ────────────────────────────────────────────────── */
        h1, h2, h3, h4 {
            font-weight: 700 !important;
            letter-spacing: -0.005em !important;
        }

        /* ── Caption ────────────────────────────────────────────────── */
        div[data-testid="stCaptionContainer"] p {
            color: rgba(255,255,255,0.50) !important;
            font-size: 13px !important;
        }

        /* ── Divisor ────────────────────────────────────────────────── */
        hr {
            border-color: #2a2a2a !important;
        }

        /* ── Dataframe — cabeçalho e números ────────────────────────── */
        [data-testid="stDataFrameResizable"] th {
            color: rgba(255,255,255,0.50) !important;
            font-size: 12px !important;
            font-weight: 500 !important;
        }
        [data-testid="stDataFrameResizable"] td {
            font-size: 13px !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
