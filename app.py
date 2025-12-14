import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuração da página
st.set_page_config(
    page_title="Dashboard de Campanhas",
    page_icon="📊",
    layout="wide"
)

# Título
st.title("📊 Dashboard de Análise de Campanhas")
st.markdown("---")

# Upload do arquivo
uploaded_file = st.file_uploader("Carregar arquivo CSV", type=['csv'])

if uploaded_file is not None:
    # Carregar dados
    df = pd.read_csv(uploaded_file)
    
    # Limpar nomes das colunas
    df.columns = df.columns.str.strip().str.lower()
    
    # Sidebar - Filtros
    st.sidebar.header("🔍 Filtros")
    
    # Filtro de Campanha
    campanhas = ['Todas'] + sorted(df['campaign'].unique().tolist())
    campanha_selecionada = st.sidebar.selectbox("Campanha", campanhas)
    
    # Filtro de Persona
    personas = ['Todas'] + sorted(df['persona'].unique().tolist())
    persona_selecionada = st.sidebar.selectbox("Persona", personas)
    
    # Aplicar filtros
    df_filtrado = df.copy()
    if campanha_selecionada != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['campaign'] == campanha_selecionada]
    if persona_selecionada != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['persona'] == persona_selecionada]
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    total_registros = len(df_filtrado)
    taxa_sucesso = (df_filtrado['resultado'].str.lower().isin(['sucesso', 'success']).sum() / total_registros * 100) if total_registros > 0 else 0
    taxa_previousy = (df_filtrado['previousy'].str.lower().isin(['sim', 'yes', '1']).sum() / total_registros * 100) if total_registros > 0 else 0
    personas_unicas = df_filtrado['persona'].nunique()
    
    with col1:
        st.metric("Total de Registros", f"{total_registros:,}")
    with col2:
        st.metric("Taxa de Sucesso", f"{taxa_sucesso:.1f}%")
    with col3:
        st.metric("Contato Prévio", f"{taxa_previousy:.1f}%")
    with col4:
        st.metric("Personas Únicas", personas_unicas)
    
    st.markdown("---")
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Distribuição por Campanha")
        campaign_counts = df_filtrado['campaign'].value_counts().reset_index()
        campaign_counts.columns = ['campaign', 'count']
        fig1 = px.bar(campaign_counts, x='campaign', y='count',
                      color='count',
                      color_continuous_scale='Blues',
                      labels={'campaign': 'Campanha', 'count': 'Quantidade'})
        fig1.update_layout(showlegend=False)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Resultado das Ações")
        resultado_counts = df_filtrado['resultado'].value_counts().reset_index()
        resultado_counts.columns = ['resultado', 'count']
        fig2 = px.pie(resultado_counts, values='count', names='resultado',
                      color_discrete_sequence=['#10b981', '#ef4444'])
        st.plotly_chart(fig2, use_container_width=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("👥 Distribuição por Persona")
        persona_counts = df_filtrado['persona'].value_counts().reset_index()
        persona_counts.columns = ['persona', 'count']
        fig3 = px.bar(persona_counts, x='persona', y='count',
                      color='count',
                      color_continuous_scale='Greens',
                      labels={'persona': 'Persona', 'count': 'Quantidade'})
        fig3.update_layout(showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)
    
    with col4:
        st.subheader("📞 Contato Prévio (Previousy)")
        previousy_counts = df_filtrado['previousy'].value_counts().reset_index()
        previousy_counts.columns = ['previousy', 'count']
        fig4 = px.pie(previousy_counts, values='count', names='previousy',
                      color_discrete_sequence=['#f59e0b', '#8b5cf6'])
        st.plotly_chart(fig4, use_container_width=True)
    
    st.markdown("---")
    
    # Tabela de dados
    st.subheader("📋 Dados Filtrados")
    st.dataframe(df_filtrado, use_container_width=True)
    
    # Download dos dados filtrados
    csv = df_filtrado.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="⬇️ Download dados filtrados (CSV)",
        data=csv,
        file_name='dados_filtrados.csv',
        mime='text/csv',
    )

else:
    st.info("👆 Por favor, faça upload do arquivo meus_dados.csv para visualizar o dashboard")
    st.markdown("""
    ### Formato esperado do CSV:
    O arquivo deve conter as seguintes colunas:
    - *campaign*: Nome da campanha
    - *previousy*: Contato prévio (sim/não)
    - *persona*: Tipo de persona
    - *resultado*: Resultado da ação (sucesso/falha)
    """)
