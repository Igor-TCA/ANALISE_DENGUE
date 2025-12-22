import os
from datetime import datetime
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="Dengue Brasil 2025 | EDA", layout="wide")

# ----------------------------
# Helpers 
# ----------------------------
UF_NOME = {
    11: "Rondônia", 12: "Acre", 13: "Amazonas", 14: "Roraima", 15: "Pará", 16: "Amapá", 17: "Tocantins",
    21: "Maranhão", 22: "Piauí", 23: "Ceará", 24: "Rio Grande do Norte", 25: "Paraíba", 26: "Pernambuco",
    27: "Alagoas", 28: "Sergipe", 29: "Bahia",
    31: "Minas Gerais", 32: "Espírito Santo", 33: "Rio de Janeiro", 35: "São Paulo",
    41: "Paraná", 42: "Santa Catarina", 43: "Rio Grande do Sul",
    50: "Mato Grosso do Sul", 51: "Mato Grosso", 52: "Goiás", 53: "Distrito Federal",
}

def decode_idade_anos(nu_idade_n: float) -> float:
    """
    Padrão SINAN (NU_IDADE_N):
      4xxx = anos | 3xxx = meses | 2xxx = dias | 1xxx = horas
    Retorna idade aproximada em anos (float). NaN se inválido.
    """
    if pd.isna(nu_idade_n):
        return np.nan
    try:
        v = int(float(nu_idade_n))
    except Exception:
        return np.nan

    if v < 1000:
        # alguns registros podem vir sem codificação esperada
        return np.nan

    unidade = v // 1000
    valor = v % 1000

    if unidade == 4:  # anos
        return float(valor)
    if unidade == 3:  # meses
        return float(valor) / 12.0
    if unidade == 2:  # dias
        return float(valor) / 365.25
    if unidade == 1:  # horas
        return float(valor) / (365.25 * 24.0)

    return np.nan

def faixa_etaria(idade_anos: float) -> str:
    if pd.isna(idade_anos):
        return "Ignorado"
    # Faixas do seu relatório
    if idade_anos < 15:
        return "Crianças (0-15)"
    if idade_anos < 23:
        return "Jovens (15-23)"
    if idade_anos < 60:
        return "Adultos (23-60)"
    return "Idosos (60+)"

def map_regiao(uf_cod: float) -> str:
    if pd.isna(uf_cod):
        return "Ignorado"
    try:
        u = int(float(uf_cod))
    except Exception:
        return "Ignorado"
    if 11 <= u <= 17:
        return "Norte"
    if 21 <= u <= 29:
        return "Nordeste"
    if 31 <= u <= 35:
        return "Sudeste"
    if 41 <= u <= 43:
        return "Sul"
    if 50 <= u <= 53:
        return "Centro-Oeste"
    return "Ignorado"

@st.cache_data(show_spinner=False)
def load_csv(file) -> pd.DataFrame:
    # Ajuste de separador/encoding pode variar; tente defaults comuns
    try:
        df = pd.read_csv(file, low_memory=False)
        return df
    except Exception:
        df = pd.read_csv(file, sep=";", low_memory=False, encoding="latin-1")
        return df

@st.cache_data(show_spinner=False)
def prepare_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Colunas essenciais esperadas pelo notebook/relatório
    # - DT_NOTIFIC (data)
    # - NU_IDADE_N (idade codificada SINAN)
    # - SG_UF_NOT (UF de notificação)
    # - EVOLUCAO (desfecho)
    for c in ["DT_NOTIFIC", "NU_IDADE_N", "SG_UF_NOT", "EVOLUCAO"]:
        if c not in df.columns:
            pass

    # Data de notificação
    if "DT_NOTIFIC" in df.columns:
        df["DT_NOTIFIC"] = pd.to_datetime(df["DT_NOTIFIC"], errors="coerce", dayfirst=True)

    # UF / Região / Nome UF
    if "SG_UF_NOT" in df.columns:
        df["SG_UF_NOT"] = pd.to_numeric(df["SG_UF_NOT"], errors="coerce")
        df["NOME_UF"] = df["SG_UF_NOT"].map(lambda x: UF_NOME.get(int(x), "Ignorado") if pd.notna(x) else "Ignorado")
        df["REGIAO"] = df["SG_UF_NOT"].map(map_regiao)
    else:
        df["NOME_UF"] = "Ignorado"
        df["REGIAO"] = "Ignorado"

    # Idade
    if "NU_IDADE_N" in df.columns:
        df["NU_IDADE_N"] = pd.to_numeric(df["NU_IDADE_N"], errors="coerce")
        df["IDADE_ANOS"] = df["NU_IDADE_N"].map(decode_idade_anos)
        df["FAIXA_ETARIA"] = df["IDADE_ANOS"].map(faixa_etaria)
    else:
        df["IDADE_ANOS"] = np.nan
        df["FAIXA_ETARIA"] = "Ignorado"

    # Óbito (no notebook: EVOLUCAO in [2,3])
    if "EVOLUCAO" in df.columns:
        df["EVOLUCAO"] = pd.to_numeric(df["EVOLUCAO"], errors="coerce")
        df["OBITO"] = df["EVOLUCAO"].isin([2, 3]).astype(int)
    else:
        df["OBITO"] = 0

    return df

def fmt_int(x: int) -> str:
    try:
        return f"{int(x):,}".replace(",", ".")
    except Exception:
        return str(x)

# ----------------------------
# UI
# ----------------------------
st.title("🦟 Dengue no Brasil (2025) — Dashboard EDA")
st.caption("Base: DATASUS / SINAN Online (notificações). Métricas aqui refletem dados de notificação, não necessariamente casos confirmados.")

with st.sidebar:
    st.header("Dados")
    st.write("Carregue `DENGBR25.csv` ou deixe o app tentar ler da raiz do projeto.")
    uploaded = st.file_uploader("Upload do CSV (DENGBR25.csv)", type=["csv"])
    local_path = st.text_input("Ou caminho local do CSV", value="DENGBR25.csv")
    st.divider()
    st.header("Filtros")
    st.caption("Filtros aplicam-se a todas as análises.")

# Load data
df_raw = None
if uploaded is not None:
    df_raw = load_csv(uploaded)
else:
    if os.path.exists(local_path):
        df_raw = load_csv(local_path)

if df_raw is None:
    st.warning("Nenhum dataset carregado ainda. Faça upload do CSV ou garanta que `DENGBR25.csv` esteja na raiz do projeto.")
    st.stop()

df = prepare_df(df_raw)

# Sidebar filters
with st.sidebar:
    # Data range
    if "DT_NOTIFIC" in df.columns and df["DT_NOTIFIC"].notna().any():
        min_dt = df["DT_NOTIFIC"].min()
        max_dt = df["DT_NOTIFIC"].max()
        dt_start, dt_end = st.date_input(
            "Período (DT_NOTIFIC)",
            value=(min_dt.date(), max_dt.date()),
            min_value=min_dt.date(),
            max_value=max_dt.date(),
        )
    else:
        dt_start, dt_end = None, None
        st.info("DT_NOTIFIC indisponível/sem datas válidas. Filtro de período desativado.")

    regioes = ["Todas"] + sorted([r for r in df["REGIAO"].dropna().unique() if r != "Ignorado"])
    reg_sel = st.selectbox("Região", regioes, index=0)

    faixas = ["Todas"] + ["Crianças (0-15)", "Jovens (15-23)", "Adultos (23-60)", "Idosos (60+)", "Ignorado"]
    fx_sel = st.selectbox("Faixa etária", faixas, index=0)

    ufs = ["Todas"] + sorted([u for u in df["NOME_UF"].dropna().unique() if u != "Ignorado"])
    uf_sel = st.selectbox("UF (notificação)", ufs, index=0)

# Apply filters
df_f = df.copy()
if dt_start and dt_end and "DT_NOTIFIC" in df_f.columns:
    df_f = df_f[(df_f["DT_NOTIFIC"].dt.date >= dt_start) & (df_f["DT_NOTIFIC"].dt.date <= dt_end)]
if reg_sel != "Todas":
    df_f = df_f[df_f["REGIAO"] == reg_sel]
if fx_sel != "Todas":
    df_f = df_f[df_f["FAIXA_ETARIA"] == fx_sel]
if uf_sel != "Todas":
    df_f = df_f[df_f["NOME_UF"] == uf_sel]

# ----------------------------
# KPIs
# ----------------------------
col1, col2, col3, col4 = st.columns(4)

total_reg = len(df_f)
total_ufs = df_f["NOME_UF"].nunique() if "NOME_UF" in df_f.columns else 0
total_mun = df_f["ID_MUNICIP"].nunique() if "ID_MUNICIP" in df_f.columns else np.nan
obitos = int(df_f["OBITO"].sum()) if "OBITO" in df_f.columns else 0

with col1:
    st.metric("Total de registros", fmt_int(total_reg))
with col2:
    st.metric("Óbitos (EVOLUCAO 2 ou 3)", fmt_int(obitos))
with col3:
    st.metric("UFs no recorte", fmt_int(total_ufs))
with col4:
    st.metric("Municípios no recorte", "—" if pd.isna(total_mun) else fmt_int(total_mun))

if "DT_NOTIFIC" in df_f.columns and df_f["DT_NOTIFIC"].notna().any():
    st.caption(f"Período no recorte: {df_f['DT_NOTIFIC'].min().date()} → {df_f['DT_NOTIFIC'].max().date()}")

st.divider()

# ----------------------------
# Charts
# ----------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "Faixa etária",
    "Região / UF",
    "Óbitos por faixa",
    "Evolução temporal",
])

with tab1:
    st.subheader("Distribuição de casos notificados por faixa etária")
    age_counts = (
        df_f["FAIXA_ETARIA"]
        .value_counts(dropna=False)
        .reindex(["Crianças (0-15)", "Jovens (15-23)", "Adultos (23-60)", "Idosos (60+)", "Ignorado"], fill_value=0)
        .reset_index()
    )
    age_counts.columns = ["FAIXA_ETARIA", "CASOS"]
    age_counts["PERCENTUAL"] = (age_counts["CASOS"] / age_counts["CASOS"].sum() * 100).round(1)

    c1, c2 = st.columns([2, 1])
    with c1:
        fig, ax = plt.subplots()
        ax.bar(age_counts["FAIXA_ETARIA"], age_counts["CASOS"])
        ax.set_ylabel("Casos (notificados)")
        ax.set_xlabel("")
        ax.set_title("Casos por faixa etária")
        ax.tick_params(axis="x", rotation=25)
        st.pyplot(fig, clear_figure=True)
    with c2:
        st.dataframe(age_counts, use_container_width=True, hide_index=True)

with tab2:
    st.subheader("Distribuição territorial (notificação)")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("**Casos por região**")
        reg_counts = (
            df_f["REGIAO"].value_counts(dropna=False)
            .reindex(["Sudeste", "Sul", "Centro-Oeste", "Nordeste", "Norte", "Ignorado"], fill_value=0)
            .reset_index()
        )
        reg_counts.columns = ["REGIAO", "CASOS"]
        reg_counts["PERCENTUAL"] = (reg_counts["CASOS"] / reg_counts["CASOS"].sum() * 100).round(1)

        fig, ax = plt.subplots()
        ax.bar(reg_counts["REGIAO"], reg_counts["CASOS"])
        ax.set_ylabel("Casos (notificados)")
        ax.set_xlabel("")
        ax.set_title("Casos por região")
        ax.tick_params(axis="x", rotation=25)
        st.pyplot(fig, clear_figure=True)

        st.dataframe(reg_counts, use_container_width=True, hide_index=True)

    with c2:
        st.markdown("**Top 10 UFs por volume**")
        uf_counts = (
            df_f["NOME_UF"].value_counts(dropna=False)
            .reset_index()
            .rename(columns={"index": "UF", "NOME_UF": "CASOS"})
        )
        uf_counts = uf_counts.rename(columns={uf_counts.columns[0]: "UF", uf_counts.columns[1]: "CASOS"})
        uf_counts = uf_counts[uf_counts["UF"] != "Ignorado"].head(10).copy()
        uf_counts["PERCENTUAL"] = (uf_counts["CASOS"] / df_f["NOME_UF"].value_counts().sum() * 100).round(1)

        fig, ax = plt.subplots()
        ax.barh(uf_counts["UF"][::-1], uf_counts["CASOS"][::-1])
        ax.set_xlabel("Casos (notificados)")
        ax.set_ylabel("")
        ax.set_title("Top 10 UFs")
        st.pyplot(fig, clear_figure=True)

        st.dataframe(uf_counts, use_container_width=True, hide_index=True)

with tab3:
    st.subheader("Óbitos por faixa etária (entre casos notificados)")
    # Tabela de óbitos e proporção (óbito/casos) por faixa
    tmp = df_f.copy()
    grp = tmp.groupby("FAIXA_ETARIA", dropna=False)["OBITO"].agg(["sum", "count"]).reset_index()
    grp.columns = ["FAIXA_ETARIA", "OBITOS", "CASOS"]
    grp["PROPORCAO_%"] = (grp["OBITOS"] / grp["CASOS"] * 100).replace([np.inf, -np.inf], np.nan).round(3)
    grp = grp.set_index("FAIXA_ETARIA").reindex(
        ["Crianças (0-15)", "Jovens (15-23)", "Adultos (23-60)", "Idosos (60+)", "Ignorado"]
    ).reset_index()

    c1, c2 = st.columns([2, 1])
    with c1:
        fig, ax = plt.subplots()
        ax.bar(grp["FAIXA_ETARIA"], grp["PROPORCAO_%"])
        ax.set_ylabel("Óbitos / casos (%)")
        ax.set_xlabel("")
        ax.set_title("Proporção de óbitos entre notificados por faixa etária")
        ax.tick_params(axis="x", rotation=25)
        st.pyplot(fig, clear_figure=True)

    with c2:
        st.dataframe(grp, use_container_width=True, hide_index=True)
        st.caption("Métrica: OBITOS/CASOS (%), baseada em EVOLUCAO ∈ {2,3} como óbito.")

with tab4:
    st.subheader("Evolução temporal (semanal) — casos notificados")
    if "DT_NOTIFIC" not in df_f.columns or not df_f["DT_NOTIFIC"].notna().any():
        st.info("Não foi possível gerar a série temporal: DT_NOTIFIC ausente ou sem datas válidas.")
    else:
        df_t = df_f[df_f["DT_NOTIFIC"].notna()].copy()
        # Semana como início do período semanal
        df_t["SEMANA"] = df_t["DT_NOTIFIC"].dt.to_period("W").apply(lambda r: r.start_time)

        total_sem = df_t.groupby("SEMANA").size().reset_index(name="TOTAL_CASOS").sort_values("SEMANA")

        # Faixa para overlay
        fx_options = ["(somente total)"] + ["Crianças (0-15)", "Jovens (15-23)", "Adultos (23-60)", "Idosos (60+)"]
        fx_overlay = st.selectbox("Linha adicional (por faixa etária)", fx_options, index=0)

        fig, ax = plt.subplots()
        ax.plot(total_sem["SEMANA"], total_sem["TOTAL_CASOS"], marker="o", linewidth=1)
        ax.set_title("Casos por semana epidemiológica (aprox.)")
        ax.set_ylabel("Casos (notificados)")
        ax.set_xlabel("Semana")
        ax.tick_params(axis="x", rotation=25)

        if fx_overlay != "(somente total)":
            fx_sem = (
                df_t[df_t["FAIXA_ETARIA"] == fx_overlay]
                .groupby("SEMANA")
                .size()
                .reset_index(name="CASOS_FAIXA")
                .sort_values("SEMANA")
            )
            ax.plot(fx_sem["SEMANA"], fx_sem["CASOS_FAIXA"], marker="o", linewidth=1)
            ax.legend(["Total", fx_overlay])

        st.pyplot(fig, clear_figure=True)

# ----------------------------
# Insights rápidos
# ----------------------------
st.divider()
st.subheader("Insights rápidos (no recorte atual)")

insights = []

# Maior faixa etária
if "FAIXA_ETARIA" in df_f.columns and len(df_f) > 0:
    top_fx = df_f["FAIXA_ETARIA"].value_counts().idxmax()
    insights.append(f"- Maior volume de notificações na faixa: **{top_fx}**.")

# Maior região
if "REGIAO" in df_f.columns and len(df_f) > 0:
    top_reg = df_f["REGIAO"].value_counts().idxmax()
    insights.append(f"- Região com maior volume no recorte: **{top_reg}**.")

# Maior UF
if "NOME_UF" in df_f.columns and len(df_f) > 0:
    top_uf = df_f["NOME_UF"].value_counts().idxmax()
    insights.append(f"- UF com maior volume no recorte: **{top_uf}**.")

# Proporção de óbitos no recorte
if len(df_f) > 0:
    p_ob = (df_f["OBITO"].sum() / len(df_f)) * 100
    insights.append(f"- Proporção de óbitos entre notificados no recorte: **{p_ob:.4f}%**.")

st.markdown("\n".join(insights) if insights else "Sem insights disponíveis para o recorte atual.")

st.caption("Dica: use os filtros na lateral para explorar recortes por período, região, UF e faixa etária.")
