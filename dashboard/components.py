import base64
import os

import pandas as pd
import plotly.express as px
import streamlit as st

# ── Caminhos das logos ────────────────────────────────────────────────────────

_ASSETS = os.path.join(os.path.dirname(__file__), "assets")
LOGO_CLARA  = os.path.join(_ASSETS, "logo_preta.png")
LOGO_ESCURA = os.path.join(_ASSETS, "logo_branca.png")

COLOR_MAP = {
    "Display": "#008140",   # verde escuro
    "Vídeo":   "#00b359",   # verde claro
    "Áudio":   "#ffffff",   # branco
    "Misto":   "#aaaaaa",   # cinza (fallback)
}

POR_PAGINA = 20

# ── CSS compartilhado ─────────────────────────────────────────────────────────

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

.pub-card {
    background: #1c1c1c;
    border-radius: 8px;
    padding: 18px 20px 14px;
    margin-bottom: 4px;
}
.pub-card-title {
    font-family: 'Manrope', sans-serif;
    font-size: 15px;
    font-weight: 600;
    color: #ffffff;
    margin-bottom: 16px;
}

/* ── Barras ── */
.pub-bar-list { display: flex; flex-direction: column; gap: 9px; }
.pub-bar-row {
    display: grid;
    grid-template-columns: 220px 1fr 120px;
    align-items: center;
    gap: 12px;
}
.pub-bar-name {
    font-family: 'Manrope', sans-serif;
    font-size: 12px;
    color: #ffffff;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.pub-bar-track {
    height: 16px;
    background: #262626;
    border-radius: 3px;
    overflow: hidden;
}
.pub-bar-fill {
    height: 100%;
    border-radius: 3px;
    transition: width 0.3s ease;
}
.pub-bar-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: rgba(255,255,255,0.72);
    text-align: right;
    font-variant-numeric: tabular-nums;
}
.pub-bar-legend {
    display: flex;
    gap: 14px;
    margin-top: 14px;
    padding-top: 12px;
    border-top: 1px solid #2a2a2a;
    flex-wrap: wrap;
}
.pub-legend-item {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-family: 'Manrope', sans-serif;
    font-size: 12px;
    color: rgba(255,255,255,0.72);
}
.pub-legend-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    display: inline-block;
    flex-shrink: 0;
}

/* ── Tabelas ── */
.pub-table-wrap { overflow-x: auto; }
.pub-table {
    width: 100%;
    border-collapse: collapse;
    font-family: 'Manrope', sans-serif;
    font-size: 13px;
}
.pub-table th {
    padding: 9px 12px;
    text-align: left;
    border-bottom: 1px solid #2a2a2a;
    color: rgba(255,255,255,0.50);
    font-size: 12px;
    font-weight: 500;
    white-space: nowrap;
}
.pub-table td {
    padding: 9px 12px;
    border-bottom: 1px solid #1f1f1f;
    color: #ffffff;
    white-space: nowrap;
}
.pub-table th.num, .pub-table td.num {
    text-align: right;
    font-family: 'JetBrains Mono', monospace;
    font-variant-numeric: tabular-nums;
    font-size: 12px;
}
.pub-table tbody tr:hover td { background: rgba(255,255,255,0.025); }
.pub-table tr.total td {
    border-top: 1px solid #3a3a3a;
    border-bottom: none;
    font-weight: 700;
    background: rgba(0,129,64,0.07);
}

/* ── Badge tipo ── */
.pub-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    border-radius: 9999px;
    padding: 2px 9px;
    font-size: 11px;
    font-weight: 500;
    white-space: nowrap;
}
.pub-badge-dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    display: inline-block;
    flex-shrink: 0;
}
</style>
"""


# ── Helpers de renderização ───────────────────────────────────────────────────

def _html(content: str) -> None:
    """Renderiza HTML puro. Usa st.html (>=1.31) com fallback para st.markdown."""
    if hasattr(st, "html"):
        st.html(_CSS + content)
    else:
        st.markdown(_CSS + content, unsafe_allow_html=True)


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
            .logo-container {{ display:flex; justify-content:flex-start; margin-bottom:0.75rem; }}
            .logo-container img {{ width:min(220px,55vw); height:auto; }}
            .logo-dark {{ display:none; }}
            @media (prefers-color-scheme:dark) {{
                .logo-light {{ display:none; }}
                .logo-dark  {{ display:block; }}
            }}
        </style>
        <div class="logo-container">
            <img class="logo-light" src="data:image/png;base64,{clara_b64}">
            <img class="logo-dark"  src="data:image/png;base64,{escura_b64}">
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Helpers ───────────────────────────────────────────────────────────────────

def _tema() -> str:
    return "plotly_dark" if st.get_option("theme.base") == "dark" else "plotly_white"


def _br(valor, decimais: int = 0, prefixo: str = "") -> str:
    fmt = f"{valor:,.{decimais}f}"
    fmt = fmt.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{prefixo}{fmt}"


def _badge_html(tipo: str) -> str:
    color = COLOR_MAP.get(tipo, "#888888")
    bg    = color + "22"
    bord  = color + "55"
    return (
        f'<span class="pub-badge" style="background:{bg};border:1px solid {bord};color:{color}">'
        f'<span class="pub-badge-dot" style="background:{color}"></span>{tipo}</span>'
    )


def _legenda_html(df: pd.DataFrame) -> str:
    tipos = df["Tipo_Midia"].dropna().unique()
    return "".join(
        f'<span class="pub-legend-item">'
        f'<span class="pub-legend-dot" style="background:{COLOR_MAP.get(t,"#888")}"></span>'
        f'{t}</span>'
        for t in COLOR_MAP if t in tipos
    )


# ── Semáforo ─────────────────────────────────────────────────────────────────

_COR_BOM    = "#008140"
_COR_MEDIO  = "#d4a017"
_COR_RUIM   = "#c0392b"


def _dot(color: str) -> str:
    """Círculo colorido para indicador semáforo."""
    return (
        f'<span style="display:inline-block;width:7px;height:7px;border-radius:50%;'
        f'background:{color};flex-shrink:0;margin-right:5px"></span>'
    )


def _cor_cpc(cpc: float, media: float) -> str:
    """Verde < 90 % da média | Amarelo 90–120 % | Vermelho > 120 %."""
    if media <= 0:
        return _COR_MEDIO
    ratio = cpc / media
    if ratio <= 0.90:
        return _COR_BOM
    elif ratio <= 1.20:
        return _COR_MEDIO
    return _COR_RUIM


def _cor_aproveitamento(pct: float) -> str:
    """Verde ≥ 80 % | Amarelo 50–79 % | Vermelho < 50 %."""
    if pct >= 80:
        return _COR_BOM
    elif pct >= 50:
        return _COR_MEDIO
    return _COR_RUIM


# ── KPIs ──────────────────────────────────────────────────────────────────────

def kpis(df: pd.DataFrame) -> None:
    imp  = df["impressions"].sum()
    clk  = df["clicks"].sum()
    bud  = df["budget"].sum()
    conv = df["conversions"].sum()
    ctr  = (clk / imp * 100) if imp else 0
    cpc  = (bud / clk) if clk else 0

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Impressões",  _br(imp))
    c2.metric("Cliques",     _br(clk))
    c3.metric("CTR médio",   _br(ctr, decimais=2) + "%")
    c4.metric("Valor gasto", _br(bud, decimais=2, prefixo="R$ "))
    c5.metric("CPC médio",   _br(cpc, decimais=2, prefixo="R$ "))
    c6.metric("Conversões",  _br(conv))


# ── Gráfico de barras paginado ────────────────────────────────────────────────

def _segmentos_html(df_camp: pd.DataFrame, coluna: str, total_camp: float, max_val: float, fmt_func) -> str:
    """Gera os segmentos coloridos de uma barra empilhada em HTML."""
    html = ""
    for tipo, color in COLOR_MAP.items():
        rows = df_camp[df_camp["Tipo_Midia"] == tipo]
        if rows.empty:
            continue
        val = float(rows[coluna].iloc[0])
        if val <= 0:
            continue

        seg_w   = val / max_val * 100       # largura proporcional ao máximo geral
        pct_int = val / total_camp * 100    # % dentro da campanha
        label   = f"{pct_int:.0f}%" if pct_int >= 8 else ""
        fc      = _font_color_para_fundo(color)
        tooltip = f"{tipo}: {pct_int:.0f}% ({fmt_func(val)})"

        html += (
            f'<div title="{tooltip}" style="width:{seg_w:.2f}%;height:100%;background:{color};flex-shrink:0;'
            f'display:inline-flex;align-items:center;justify-content:center;overflow:hidden;cursor:default;'
            f'font-family:JetBrains Mono,monospace;font-size:10px;font-weight:500;color:{fc}">'
            f'{label}</div>'
        )
    return html


def _grafico_barras_paginado(
    df: pd.DataFrame,
    coluna: str,
    titulo: str,
    fmt_func,
    key: str,
) -> None:
    if key not in st.session_state:
        st.session_state[key] = 0

    # Totais por campanha (todas as mídias somadas)
    totais = df.groupby("campaign_name")[coluna].sum().sort_values(ascending=False)
    campanhas_ord = totais.index.tolist()
    n_total  = len(campanhas_ord)
    n_pages  = max(1, -(-n_total // POR_PAGINA))
    page     = min(st.session_state[key], n_pages - 1)
    st.session_state[key] = page

    campanhas_pag = campanhas_ord[page * POR_PAGINA:(page + 1) * POR_PAGINA]
    max_val = totais.max() or 1

    rows_html = ""
    for camp in campanhas_pag:
        total_camp = totais[camp]
        df_camp    = df[df["campaign_name"] == camp]
        segs       = _segmentos_html(df_camp, coluna, total_camp, max_val, fmt_func)
        name_trunc = (camp[:38] + "…") if len(camp) > 38 else camp

        rows_html += (
            f'<div class="pub-bar-row">'
            f'<div class="pub-bar-name" title="{camp}">{name_trunc}</div>'
            f'<div class="pub-bar-track" style="display:flex;overflow:hidden;border-radius:3px">{segs}</div>'
            f'<div class="pub-bar-value">{fmt_func(total_camp)}</div>'
            f'</div>'
        )

    _html(f"""
        <div class="pub-card">
            <div class="pub-card-title">{titulo}</div>
            <div class="pub-bar-list">{rows_html}</div>
            <div class="pub-bar-legend">{_legenda_html(df)}</div>
        </div>
    """)

    if n_pages > 1:
        c1, c2, c3 = st.columns([1, 5, 1])
        with c1:
            if st.button("← Ant.", key=f"prev_{key}", disabled=page == 0):
                st.session_state[key] -= 1
                st.rerun()
        with c2:
            st.caption(f"Página {page + 1} de {n_pages}  ·  {n_total} campanhas")
        with c3:
            if st.button("Próx. →", key=f"next_{key}", disabled=page >= n_pages - 1):
                st.session_state[key] += 1
                st.rerun()


def grafico_impressoes(df: pd.DataFrame) -> None:
    _grafico_barras_paginado(df, "impressions", "Impressões por campanha",
                             lambda v: _br(v), "pag_imp")


def grafico_cliques(df: pd.DataFrame) -> None:
    _grafico_barras_paginado(df, "clicks", "Cliques por campanha",
                             lambda v: _br(v), "pag_clk")


def grafico_budget(df: pd.DataFrame) -> None:
    _grafico_barras_paginado(df, "budget", "Valor gasto por campanha (R$)",
                             lambda v: _br(v, decimais=2, prefixo="R$ "), "pag_bud")


# ── Donut ─────────────────────────────────────────────────────────────────────

def _font_color_para_fundo(hex_color: str) -> str:
    """Retorna 'black' ou 'white' de acordo com a luminância do fundo."""
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return "black" if lum > 0.55 else "white"


def grafico_tipo_midia(df: pd.DataFrame, coluna: str = "impressions", titulo: str | None = None) -> None:
    label_map = {"impressions": "Impressões", "clicks": "Cliques", "budget": "Valor gasto (R$)"}
    titulo    = titulo or f"Distribuição por tipo de mídia — {label_map.get(coluna, coluna)}"

    resumo = df.groupby("Tipo_Midia", as_index=False)[coluna].sum()
    total  = resumo[coluna].sum()
    fmt_total = _br(total) if coluna != "budget" else _br(total, 2, "R$ ")

    # Texto e cor de fonte por fatia
    def _fmt_val(v: float) -> str:
        return _br(v, 2, "R$ ") if coluna == "budget" else _br(v)

    resumo["_pct"]  = (resumo[coluna] / total * 100).round(1) if total else 0
    resumo["_text"] = resumo.apply(
        lambda r: f"{_fmt_val(r[coluna])}<br>{r['_pct']:.1f}%" if r["_pct"] >= 5 else "",
        axis=1,
    )

    font_colors = [
        _font_color_para_fundo(COLOR_MAP.get(t, "#888888"))
        for t in resumo["Tipo_Midia"]
    ]

    fig = px.pie(
        resumo, names="Tipo_Midia", values=coluna,
        color="Tipo_Midia", color_discrete_map=COLOR_MAP,
        hole=0.58, title=titulo,
    )
    fig.update_traces(
        text=resumo["_text"].tolist(),
        textposition="inside",
        textinfo="text",
        insidetextfont=dict(
            family="JetBrains Mono, monospace",
            size=11,
            color=font_colors,
        ),
        hovertemplate="%{label}: %{value:,.0f} (%{percent})",
        domain=dict(x=[0, 0.62], y=[0, 1]),
    )
    fig.add_annotation(
        text=f"<b>{fmt_total}</b><br><span style='font-size:11px;opacity:0.6'>total</span>",
        x=0.31, y=0.5, showarrow=False,
        font=dict(family="JetBrains Mono, monospace", size=14, color="#ffffff"),
        align="center",
        xanchor="center", yanchor="middle",
    )
    fig.update_layout(
        template=_tema(), separators=",.", height=360,
        margin=dict(l=10, r=10, t=50, b=10),
        legend=dict(
            orientation="v", x=0.65, y=0.5,
            xanchor="left", yanchor="middle",
            font=dict(size=12, color="rgba(255,255,255,0.8)"),
        ),
        title=dict(font=dict(size=14, color="#ffffff")),
    )
    st.plotly_chart(fig, use_container_width=True)


# ── Tabela resumo ─────────────────────────────────────────────────────────────

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

    header = (
        "<tr>"
        "<th>Tipo</th>"
        "<th class='num'>Campanhas</th>"
        "<th class='num'>Impressões</th>"
        "<th class='num'>Cliques</th>"
        "<th class='num'>CTR (%)</th>"
        "<th class='num'>Valor Gasto (R$)</th>"
        "<th class='num'>Conversões</th>"
        "<th class='num'>VCR (%)</th>"
        "<th class='num'>ACR (%)</th>"
        "<th class='num'>CPM (R$)</th>"
        "<th class='num'>CPC (R$)</th>"
        "</tr>"
    )

    rows_html = ""
    for i, row in resumo.iterrows():
        is_total = str(row["Tipo_Midia"]) == "TOTAL"
        tipo_cell = "<b>TOTAL</b>" if is_total else _badge_html(str(row["Tipo_Midia"]))
        row_cls   = "total" if is_total else ""

        def fmt(val, dec=0, pref=""):
            try:
                return _br(float(val), dec, pref) if pd.notna(val) else "—"
            except Exception:
                return "—"

        rows_html += (
            f'<tr class="{row_cls}">'
            f'<td>{tipo_cell}</td>'
            f'<td class="num">{fmt(row["Campanhas"])}</td>'
            f'<td class="num">{fmt(row["Impressões"])}</td>'
            f'<td class="num">{fmt(row["Cliques"])}</td>'
            f'<td class="num">{fmt(row["CTR (%)"], 2)}</td>'
            f'<td class="num">{fmt(row["Valor_Gasto"], 2, "R$ ")}</td>'
            f'<td class="num">{fmt(row["Conversões"])}</td>'
            f'<td class="num">{fmt(row.get("VCR (%)"), 2) if pd.notna(row.get("VCR (%)")) else "—"}</td>'
            f'<td class="num">{fmt(row.get("ACR (%)"), 2) if pd.notna(row.get("ACR (%)")) else "—"}</td>'
            f'<td class="num">{fmt(row["CPM (R$)"], 2, "R$ ")}</td>'
            f'<td class="num">{fmt(row["CPC (R$)"], 2, "R$ ")}</td>'
            f'</tr>'
        )

    _html(f"""
        <div class="pub-card">
            <div class="pub-table-wrap">
                <table class="pub-table">
                    <thead>{header}</thead>
                    <tbody>{rows_html}</tbody>
                </table>
            </div>
        </div>
    """)


# ── Tabela detalhe ────────────────────────────────────────────────────────────

def _aproveitamento_html(row: pd.Series) -> str:
    """
    Taxa de aproveitamento de mídia por tipo + semáforo:
      Display → CTR (%)  — verde ≥80 / amarelo 50-79 / vermelho <50
      Vídeo   → VCR (%)
      Áudio   → ACR (%)
    """
    tipo = str(row.get("Tipo_Midia", ""))
    mapa = {
        "Display": ("CTR (%)", "CTR"),
        "Vídeo":   ("VCR (%)", "VCR"),
        "Áudio":   ("ACR (%)", "ACR"),
    }
    col, label = mapa.get(tipo, (None, None))
    if col and col in row.index and pd.notna(row[col]):
        try:
            val = float(row[col])
            cor = _cor_aproveitamento(val)
            return (
                f'<span style="display:inline-flex;align-items:center">'
                f'{_dot(cor)}'
                f'<span style="font-family:JetBrains Mono,monospace;font-size:12px">{_br(val, 2)}%</span>'
                f'<span style="font-size:10px;color:rgba(255,255,255,0.45);margin-left:4px">{label}</span>'
                f'</span>'
            )
        except Exception:
            pass
    return "—"


def tabela_campanhas(df: pd.DataFrame) -> None:
    colunas = [
        "campaign_name", "Tipo_Midia", "impressions", "clicks",
        "CTR (%)", "budget", "CPM (R$)", "CPC (R$)", "conversions", "VCR (%)", "ACR (%)",
    ]
    df_exibir = df[[c for c in colunas if c in df.columns]].copy()
    df_exibir = df_exibir.sort_values("impressions", ascending=False)

    # Média do CPC para o semáforo (exclui zeros e NaN)
    avg_cpc = (
        df_exibir["CPC (R$)"].replace(0, pd.NA).dropna().mean()
        if "CPC (R$)" in df_exibir.columns else None
    )

    header = (
        "<tr>"
        "<th>Campanha</th><th>Tipo</th>"
        "<th class='num'>Impressões</th><th class='num'>Cliques</th>"
        "<th class='num'>Aproveitamento</th>"
        "<th class='num'>Valor Gasto (R$)</th>"
        "<th class='num'>CPM (R$)</th><th class='num'>CPC (R$)</th>"
        "<th class='num'>Conversões</th>"
        "</tr>"
    )

    rows_html = ""
    for _, row in df_exibir.iterrows():
        def fmt(col, dec=0, pref=""):
            try:
                return _br(float(row[col]), dec, pref) if col in row.index and pd.notna(row[col]) else "—"
            except Exception:
                return "—"

        # CPC com semáforo
        cpc_html = "—"
        if "CPC (R$)" in row.index and pd.notna(row["CPC (R$)"]) and float(row["CPC (R$)"]) > 0:
            cpc_val = float(row["CPC (R$)"])
            cor = _cor_cpc(cpc_val, avg_cpc) if avg_cpc else _COR_MEDIO
            cpc_html = (
                f'<span style="display:inline-flex;align-items:center">'
                f'{_dot(cor)}'
                f'<span style="font-family:JetBrains Mono,monospace;font-size:12px">'
                f'{_br(cpc_val, 2, "R$ ")}</span>'
                f'</span>'
            )

        rows_html += (
            f'<tr>'
            f'<td>{row["campaign_name"]}</td>'
            f'<td>{_badge_html(str(row.get("Tipo_Midia", "")))}</td>'
            f'<td class="num">{fmt("impressions")}</td>'
            f'<td class="num">{fmt("clicks")}</td>'
            f'<td class="num">{_aproveitamento_html(row)}</td>'
            f'<td class="num">{fmt("budget", 2, "R$ ")}</td>'
            f'<td class="num">{fmt("CPM (R$)", 2, "R$ ")}</td>'
            f'<td class="num">{cpc_html}</td>'
            f'<td class="num">{fmt("conversions")}</td>'
            f'</tr>'
        )

    _html(f"""
        <div class="pub-card">
            <div class="pub-table-wrap">
                <table class="pub-table">
                    <thead>{header}</thead>
                    <tbody>{rows_html}</tbody>
                </table>
            </div>
        </div>
    """)
