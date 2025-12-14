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
    try:
        # Tentar diferentes encodings
        try:
            df = pd.read_csv(uploaded_file, encoding='utf-8')
        except:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, encoding='latin-1')
        
        # Mostrar informações do arquivo carregado
        st.success(f"✅ Arquivo carregado com sucesso! {len(df)} linhas encontradas.")
        
        # DEBUG: Mostrar estrutura dos dados
        with st.expander("🔍 DEBUG - Estrutura do arquivo (clique para ver)", expanded=True):
            st.write("**Colunas originais do arquivo:**")
            st.code(df.columns.tolist())
            st.write("**Primeiras 5 linhas do arquivo:**")
            st.dataframe(df.head())
            st.write("**Tipos de dados:**")
            st.write(df.dtypes)
            st.write("**Valores únicos na coluna 'persona' (se existir):**")
            if 'persona' in df.columns:
                personas_debug = df['persona'].value_counts()
                st.write(personas_debug)
                st.write(f"Total de valores não-nulos: {df['persona'].notna().sum()}")
                st.write(f"Total de valores nulos: {df['persona'].isna().sum()}")
            else:
                st.warning("⚠️ Coluna 'persona' não encontrada!")
        
        # Limpar nomes das colunas apenas removendo espaços
        df.columns = df.columns.str.strip()
        
        # Verificar se as colunas necessárias existem (case insensitive)
        df_lower_cols = {col.lower(): col for col in df.columns}
        
        required_cols = ['campaign', 'persona', 'resultado', 'previousy']
        col_map = {}
        missing = []
        
        for req_col in required_cols:
            if req_col in df_lower_cols:
                col_map[req_col] = df_lower_cols[req_col]
            else:
                missing.append(req_col)
        
        if missing:
            st.error(f"❌ Colunas obrigatórias não encontradas: {', '.join(missing)}")
            st.info(f"📋 Colunas disponíveis: {', '.join(df.columns.tolist())}")
            st.stop()
        
        # Renomear colunas para padronizar
        df_work = df.rename(columns={v: k for k, v in col_map.items()})
        
        # Remover linhas onde persona está vazio
        df_work = df_work[df_work['persona'].notna()]
        df_work = df_work[df_work['persona'].astype(str).str.strip() != '']
        
        # Normalizar personas (capitalizar primeira letra de cada palavra)
        df_work['persona'] = df_work['persona'].astype(str).str.title()
        
        st.info(f"📊 Dados após limpeza: {len(df_work)} registros válidos")
        
        # Sidebar - Filtros
        st.sidebar.header("🔍 Filtros")
        
        # Filtro de Campanha
        campanhas_lista = df_work['campaign'].dropna().astype(str).unique().tolist()
        campanhas = ['Todas'] + sorted(campanhas_lista)
        campanha_selecionada = st.sidebar.selectbox("Campanha", campanhas)
        
        # Filtro de Persona
        personas_lista = df_work['persona'].dropna().astype(str).unique().tolist()
        personas = ['Todas'] + sorted(personas_lista)
        persona_selecionada = st.sidebar.selectbox("Persona", personas)
        
        st.sidebar.info(f"✅ {len(personas_lista)} personas encontradas")
        
        # Aplicar filtros
        df_filtrado = df_work.copy()
        if campanha_selecionada != 'Todas':
            df_filtrado = df_filtrado[df_filtrado['campaign'].astype(str) == campanha_selecionada]
        if persona_selecionada != 'Todas':
            df_filtrado = df_filtrado[df_filtrado['persona'].astype(str) == persona_selecionada]
        
        # Métricas principais
        col1, col2, col3, col4 = st.columns(4)
        
        total_registros = len(df_filtrado)
        
        if total_registros > 0:
            sucessos = df_filtrado['resultado'].astype(str).str.lower().isin(['sucesso', 'success']).sum()
            taxa_sucesso = (sucessos / total_registros * 100)
            
            previousy_sim = df_filtrado['previousy'].astype(str).str.lower().isin(['sim', 'yes', '1', 'true']).sum()
            taxa_previousy = (previousy_sim / total_registros * 100)
        else:
            taxa_sucesso = 0
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
        
        if total_registros == 0:
            st.warning("⚠️ Nenhum registro encontrado com os filtros aplicados.")
        else:
            # Gráficos
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📈 Distribuição por Campanha")
                campaign_counts = df_filtrado['campaign'].value_counts().reset_index()
                campaign_counts.columns = ['Campanha', 'Quantidade']
                fig1 = px.bar(campaign_counts, x='Campanha', y='Quantidade',
                              color='Quantidade',
                              color_continuous_scale='Blues',
                              text='Quantidade')
                fig1.update_traces(textposition='outside')
                fig1.update_layout(showlegend=False, xaxis_tickangle=-45)
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                st.subheader("🎯 Resultado das Ações")
                resultado_counts = df_filtrado['resultado'].value_counts().reset_index()
                resultado_counts.columns = ['Resultado', 'Quantidade']
                fig2 = px.pie(resultado_counts, values='Quantidade', names='Resultado',
                              color_discrete_sequence=['#10b981', '#ef4444'],
                              hole=0.4)
                fig2.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig2, use_container_width=True)
            
            col3, col4 = st.columns(2)
            
            with col3:
                st.subheader("👥 Distribuição por Persona")
                persona_counts = df_filtrado['persona'].value_counts().reset_index()
                persona_counts.columns = ['Persona', 'Quantidade']
                
                fig3 = px.bar(persona_counts, x='Persona', y='Quantidade',
                              color='Quantidade',
                              color_continuous_scale='Greens',
                              text='Quantidade')
                fig3.update_traces(textposition='outside')
                fig3.update_layout(showlegend=False, xaxis_tickangle=-45)
                st.plotly_chart(fig3, use_container_width=True)
                
                # Lista de personas
                st.caption(f"**Personas:** {', '.join(persona_counts['Persona'].tolist())}")
            
            with col4:
                st.subheader("📞 Contato Prévio")
                previousy_counts = df_filtrado['previousy'].value_counts().reset_index()
                previousy_counts.columns = ['Contato', 'Quantidade']
                fig4 = px.pie(previousy_counts, values='Quantidade', names='Contato',
                              color_discrete_sequence=['#f59e0b', '#8b5cf6'],
                              hole=0.4)
                fig4.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig4, use_container_width=True)
            
            st.markdown("---")
            
            # Tabela de dados
            st.subheader("📋 Dados Filtrados")
            
            # Mostrar colunas selecionadas
            colunas_mostrar = st.multiselect(
                "Selecione as colunas para exibir:",
                options=df_filtrado.columns.tolist(),
                default=df_filtrado.columns.tolist()
            )
            
            if colunas_mostrar:
                st.dataframe(df_filtrado[colunas_mostrar], use_container_width=True, height=400)
            else:
                st.dataframe(df_filtrado, use_container_width=True, height=400)
            
            # Download dos dados filtrados
            csv = df_filtrado.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="⬇️ Download dados filtrados (CSV)",
                data=csv,
                file_name='dados_filtrados.csv',
                mime='text/csv',
            )
    
    except Exception as e:
        st.error(f"❌ Erro ao processar o arquivo: {str(e)}")
        st.exception(e)

else:
    st.info("👆 Por favor, faça upload do arquivo CSV para visualizar o dashboard")
    st.markdown("""
    ### 📋 Formato esperado do CSV:
    O arquivo deve conter as seguintes colunas:
    - **campaign**: Nome da campanha
    - **persona**: Tipo de persona (DEVE estar preenchido!)
    - **previousy**: Contato prévio (sim/não)
    - **resultado**: Resultado da ação (sucesso/falha)
    
    ### ⚠️ Importante:
    - Certifique-se de que a coluna 'persona' está preenchida
    - Os nomes das colunas não diferenciam maiúsculas de minúsculas
    - Valores vazios na coluna 'persona' serão removidos automaticamente
    """)
