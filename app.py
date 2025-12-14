import streamlit as st
import pandas as pd
import plotly.express as px

# ==================================================
# CONFIGURAÇÃO DA PÁGINA
# ==================================================
st.set_page_config(
    page_title="Dashboard de Campanhas",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Dashboard de Análise de Campanhas")
st.markdown("---")

# ==================================================
# UPLOAD DO ARQUIVO
# ==================================================
uploaded_file = st.file_uploader("Carregar arquivo CSV", type=["csv", "txt"])

if uploaded_file is None:
    st.info("👆 Faça upload do arquivo para iniciar")
    st.stop()

# ==================================================
# LEITURA DO ARQUIVO (SEPARADOR TAB)
# ==================================================
try:
    uploaded_file.seek(0)
    df = pd.read_csv(uploaded_file, sep="\t")
except Exception:
    st.error("❌ Erro ao ler o arquivo. O separador deve ser TAB (\\t).")
    st.stop()

st.success(f"✅ Arquivo carregado com sucesso — {len(df)} registros")

# ==================================================
# DEBUG OPCIONAL
# ==================================================
with st.expander("🔍 Estrutura da base"):
    st.write(df.columns.tolist())
    st.dataframe(df.head())

# ==================================================
# LIMPEZA BÁSICA
# ==================================================
df.columns = df.columns.str.strip()

# ==================================================
# MAPA DE PERSONAS (CLUSTER → PERSONA)
# ==================================================
mapa_personas = {
    1: "Jovem Promissor",
    2: "Operário Consciente",
    3: "Autônomo Endividado",
    4: "Rico Endividado",
    5: "Adulto Provedor",
    6: "Jovem Empreendedor",
    7: "Empregada Solteira",
    8: "Meia Idade Divorciado",
    9: "Baixa Renda Endividado"
}

# Garantir tipo correto do cluster
df["cluster"] = pd.to_numeric(df["cluster"], errors="coerce").astype("Int64")

# Criar coluna persona a partir do cluster
df["persona"] = df["cluster"].map(mapa_personas)

# Remover registros sem persona
df = df[df["persona"].notna()]

# ==================================================
# GARANTIR TIPOS DAS VARIÁVEIS PRINCIPAIS
# ==================================================
df["campaign"] = df["campaign"].astype(str)
df["resultado"] = pd.to_numeric(df["resultado"], errors="coerce").fillna(0)
df["previous"] = pd.to_numeric(df["previous"], errors="coerce").fillna(0)

# ==================================================
# SIDEBAR – FILTROS
# ==================================================
st.sidebar.header("🔍 Filtros")

campanhas = ["Todas"] + sorted(df["campaign"].unique())
personas = ["Todas"] + sorted(df["persona"].unique())

campanha_sel = st.sidebar.selectbox("Campanha", campanhas)
persona_sel = st.sidebar.selectbox("Persona", personas)

df_filt = df.copy()

if campanha_sel != "Todas":
    df_filt = df_filt[df_filt["campaign"] == campanha_sel]

if persona_sel != "Todas":
    df_filt = df_filt[df_filt["persona"] == persona_sel]

# ==================================================
# MÉTRICAS PRINCIPAIS
# ==================================================
total = len(df_filt)

sucesso = (df_filt["resultado"] == 1).sum()
contato_previo = (df_filt["previous"] > 0).sum()

taxa_sucesso = (sucesso / total * 100) if total > 0 else 0
taxa_contato = (contato_previo / total * 100) if total > 0 else 0

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total de Registros", total)
c2.metric("Taxa de Sucesso", f"{taxa_sucesso:.1f}%")
c3.metric("Contato Prévio", f"{taxa_contato:.1f}%")
c4.metric("Personas Únicas", df_filt["persona"].nunique())

st.markdown("---")

# ==================================================
# PERSONA SELECIONADA
# ==================================================
st.subheader("🧠 Persona")

if persona_sel != "Todas":
    st.success(persona_sel)
else:
    st.info("Selecione uma persona para visualizar")

# ==================================================
# GRÁFICO – DISTRIBUIÇÃO POR PERSONA
# ==================================================
st.subheader("👥 Distribuição por Persona")

persona_counts = (
    df_filt
    .groupby("persona", as_index=False)
    .size()
    .rename(columns={"size": "Quantidade"})
)

fig_persona = px.bar(
    persona_counts,
    x="persona",
    y="Quantidade",
    text="Quantidade"
)

fig_persona.update_traces(textposition="outside")
fig_persona.update_layout(
    xaxis_title="Persona",
    showlegend=False
)

st.plotly_chart(fig_persona, use_container_width=True)

# ==================================================
# GRÁFICO – RESULTADO
# ==================================================
st.subheader("🎯 Resultado da Campanha")

resultado_counts = (
    df_filt["resultado"]
    .map({1: "Sucesso", 0: "Falha"})
    .value_counts()
    .reset_index()
)

resultado_counts.columns = ["Resultado", "Quantidade"]

fig_res = px.pie(
    resultado_counts,
    values="Quantidade",
    names="Resultado",
    hole=0.4
)

st.plotly_chart(fig_res, use_container_width=True)

# ==================================================
# TABELA ANALÍTICA POR PERSONA
# ==================================================
st.subheader("📌 Performance por Persona")

tabela_persona = (
    df_filt
    .groupby("persona")
    .agg(
        Total=("persona", "count"),
        Sucessos=("resultado", lambda x: (x == 1).sum()),
        Contato_Previo=("previous", lambda x: (x > 0).sum())
    )
    .reset_index()
)

st.dataframe(tabela_persona, use_container_width=True)

# ==================================================
# DADOS FILTRADOS + DOWNLOAD
# ==================================================
st.subheader("📋 Dados Filtrados")

st.dataframe(df_filt, use_container_width=True, height=400)

csv = df_filt.to_csv(index=False).encode("utf-8-sig")

st.download_button(
    label="⬇️ Download dados filtrados",
    data=csv,
    file_name="dados_filtrados.csv",
    mime="text/csv"
)
