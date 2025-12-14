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
    
    # Limpar nomes das colunas (remover espaços mas manter case original)
    df.columns = df.columns.str.strip()
    
    # Normalizar nomes de colunas para minúsculas para busca
    col_mapping = {col: col.lower() for col in df.columns}
    df_work = df.rename(columns=col_mapping)
    
    # Verificar se as colunas necessárias existem
    required_cols = ['campaign', 'persona', 'resultado', 'previousy']
    missing_cols = [col for col in required_cols if col not in df_work.columns]
    
    if missing_cols:
        st.error(f"❌ Colunas faltando no arquivo: {', '.join(missing_cols)}")
        st.info(f"Colunas encontradas: {', '.join(df_work.columns.tolist())}")
    else:
        # Sidebar - Filtros
        st.sidebar.header("🔍 Filtros")
        
        # Filtro de Campanha
        campanhas_unicas = df_work['campaign'].dropna().unique().tolist()
        campanhas = ['Todas'] + sorted([str(c) for c in campanhas_unicas])
        campanha_selecionada = st.sidebar.selectbox("Campanha", campanhas)
        
        # Filtro de Persona
        personas_unicas = df_work['persona'].dropna().unique().tolist()
        personas = ['Todas'] + sorted([str(p) for p in personas_unicas])
        persona_selecionada = st.sidebar.selectbox("Persona", personas)
        
        # Aplicar filtros
        df_filtrado = df_work.copy()
        if campanha_selecionada != 'Todas':
            df_filtrado = df_filtrado[df_filtrado['campaign'] == campanha_selecionada]
        if persona_selecionada != 'Todas':
            df_filtrado = df_filtrado[df_filtrado['persona'] == persona_selecionada]
        
        # Métricas principais
        col1, col2, col3, col4 = st.columns(4)
        
        total_registros = len(df_filtrado)
        
        # Taxa de sucesso com tratamento de valores nulos
        if total_registros > 0:
            sucessos = df_filtrado['resultado'].fillna('').astype(str).str.lower().isin(['sucesso', 'success']).sum()
            taxa_sucesso = (sucessos / total_registros * 100)
        else:
            taxa_sucesso = 0
        
        # Taxa de previousy com tratamento de valores nulos
        if total_registros > 0:
            previousy_sim = df_filtrado['previousy'].fillna('').astype(str).str.lower().isin(['sim', 'yes', '1', 'true']).sum()
            taxa_previousy = (previousy_sim / total_registros * 100)
        else:
            taxa_previousy = 0
        
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
            fig1.update_layout(showlegend=False, xaxis_tickangle=-45)
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
            fig3.update_layout(showlegend=False, xaxis_tickangle=-45)
            st.plotly_chart(fig3, use_container_width=True)
            
            # Mostrar lista de personas encontradas
            st.caption(f"Personas encontradas: {', '.join([str(p) for p in personas_unicas])}")
        
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
        st.dataframe(df_filtrado, use_container_width=True, height=400)
        
        # Informações adicionais sobre os dados
        with st.expander("ℹ️ Informações sobre os dados"):
            st.write(f"**Total de linhas:** {len(df_filtrado)}")
            st.write(f"**Colunas:** {', '.join(df_filtrado.columns.tolist())}")
            st.write("**Primeiras linhas:**")
            st.dataframe(df_filtrado.head())
        
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
    - **campaign**: Nome da campanha
    - **previousy**: Contato prévio (sim/não)
    - **persona**: Tipo de persona
    - **resultado**: Resultado da ação (sucesso/falha)
    
    ### Dica:
    Certifique-se de que a coluna 'persona' está preenchida com os nomes das personas.
    """)
