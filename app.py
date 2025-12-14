import streamlit as st
import pandas as pd
import plotly.express as px

# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(
    page_title="Dashboard de Campanhas",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Dashboard de Análise de Campanhas")
st.markdown("---")

# =========================
# UPLOAD DO ARQUIVO
# =========================
uploaded_file = st.file_uploader("Carregar arquivo CSV", type=["csv"])

if uploaded_file is None:
    st.info("👆 Faça upload de um arquivo CSV para iniciar")
    st.stop()

# =========================
# LEITURA ROBUSTA DO CSV
# =========================
separadores = [";", ",", "\t", "|"]
df = None

for sep in separadores:
    for enc in ["utf-8", "latin-1", "iso-8859-1", "cp1252"]:
        try:
            uploaded_file.seek(0)
            temp = pd.read_csv(uploaded_file, sep=sep, encoding=enc)
            if len(temp.columns) > 1:
                df = temp
                break
        except:
            pass
    if df is not None:
        break

if df is None:
    st.error("❌ Não foi possível ler o arquivo CSV.")
    st.stop()

st.success(f"✅ Arquivo carregado com sucesso ({len(df)} linhas)")

# =========================
# LIMPEZA E PADRONIZAÇÃO
# =========================
df.columns = df.columns.str.strip()

# Mapear colunas ignorando maiúsculas/minúsculas
col_map = {c.lower(): c for c in df.columns}
required = ["campaign", "persona", "resultado", "previousy"]

missing = [c for c in required if c not in col_map]
if missing:
    st.error(f"❌ Colunas obrigatórias ausentes: {missing}")
    st.stop()

df = df.rename(columns={col_map[c]: c for c in required})

# Limpar persona (texto qualitativo)
df = df[df["persona"].notna()]
df["persona"] = df["persona"].astype(str).str.strip()

# =========================
# SIDEBAR – FILTROS
# =========================
st.sidebar.header("🔍 Filtros")

campanhas = ["Todas"] + sorted(df["campaign"].dropna().astype(str).unique())
personas = ["Todas"] + sorted(df["persona"].unique())

campanha_sel = st.sidebar.selectbox("Campanha", campanhas)
persona_sel = st.sidebar.selectbox("Persona", personas)

df_filt = df.copy()

if campanha_sel != "Todas":
    df_filt = df_filt[df_filt["campaign"].astype(str) == campanha_sel]

if persona_sel != "Todas":
    df_filt = df_filt[df_filt["persona"] == persona_sel]

# =========================
# MÉTRICAS
# =========================
total = len(df_filt)

sucesso = df_filt["resultado"].astype(str).str.lower().isin(
    ["sucesso", "success", "sim", "yes"]
).sum()

previousy = df_filt["previousy"].astype(str).str.lower().isin(
    ["sim", "yes", "1", "true"]
).sum()

taxa_sucesso = (sucesso / total * 100) if total > 0 else 0
taxa_previousy = (previousy / total * 100) if total > 0 else 0

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total de Registros", total)
c2.metric("Taxa de Sucesso", f"{taxa_sucesso:.1f}%")
c3.metric("Contato Prévio", f"{taxa_previousy:.1f}%")
c4.metric("Personas Únicas", df_filt["persona"].nunique())

st.markdown("---")

# =========================
# DESCRIÇÃO DA PERSONA
# =========================
st.subheader("🧠 Características da Persona")

if persona_sel != "Todas":
    st.success(persona_sel)
else:
    st.info("Selecione uma persona para visualizar suas características.")

st.markdown("---")

# =========================
# GRÁFICOS
# =========================
if total == 0:
    st.warning("⚠️ Nenhum dado para os filtros selecionados.")
    st.stop()

col1, col2 = st.columns(2)

# ---- Campanhas
with col1:
    camp_counts = df_filt["campaign"].value_counts().reset_index()
    camp_counts.columns = ["Campanha", "Quantidade"]

    fig1 = px.bar(
        camp_counts,
        x="Campanha",
        y="Quantidade",
        text="Quantidade"
    )
    fig1.update_traces(textposition="outside")
    fig1.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig1, use_container_width=True)

# ---- Resultado
with col2:
    res_counts = df_filt["resultado"].value_counts().reset_index()
    res_counts.columns = ["Resultado", "Quantidade"]

    fig2 = px.pie(
        res_counts,
        values="Quantidade",
        names="Resultado",
        hole=0.4
    )
    st.plotly_chart(fig2, use_container_width=True)

# =========================
# PERSONAS (TEXTO LONGO)
# =========================
st.subheader("👥 Distribuição por Persona")

persona_counts = (
    df_filt
    .groupby("persona", as_index=False)
    .size()
    .rename(columns={"size": "Quantidade"})
)

# Quebra de linha para texto longo
persona_counts["Persona_wrap"] = (
    persona_counts["persona"]
    .str.wrap(35)
    .str.replace("\n", "<br>", regex=False)
)

fig3 = px.bar(
    persona_counts,
    x="Persona_wrap",
    y="Quantidade",
    text="Quantidade"
)

fig3.update_traces(textposition="outside")
fig3.update_layout(
    xaxis_title="Persona (características)",
    showlegend=False
)

st.plotly_chart(fig3, use_container_width=True)

# =========================
# TABELA ANALÍTICA
# =========================
st.subheader("📌 Performance por Persona")

tabela_persona = (
    df_filt
    .groupby("persona")
    .agg(
        Total=("persona", "count"),
        Sucesso=("resultado", lambda x: x.astype(str).str.lower().isin(["sucesso", "success"]).sum()),
        Contato_Previo=("previousy", lambda x: x.astype(str).str.lower().isin(["sim", "yes", "1", "true"]).sum())
    )
    .reset_index()
)

st.dataframe(tabela_persona, use_container_width=True)

# =========================
# TABELA FINAL + DOWNLOAD
# =========================
st.subheader("📋 Dados Filtrados")

st.dataframe(df_filt, use_container_width=True, height=400)

csv = df_filt.to_csv(index=False).encode("utf-8-sig")
st.download_button(
    "⬇️ Download dos dados filtrados",
    csv,
    "dados_filtrados.csv",
    "text/csv"
)
