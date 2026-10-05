import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from sqlalchemy import create_engine

# -----------------------------------------------------------------------------
# 1. CONFIGURAÇÃO DA PÁGINA E ESTILO
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Dashboard Epidemiológico - Dengue Brasil",
    page_icon="🦟",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo CSS customizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F3F4F6;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    footer {
        visibility: hidden;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. CONEXÃO COM BANCO DE DADOS E CACHE (@st.cache_data)
# -----------------------------------------------------------------------------
@st.cache_data(ttl=3600)
def load_data():
    db_path = 'database/dengue_brasil.db'
    if not os.path.exists(db_path):
        db_path = '../database/dengue_brasil.db'
    
    if not os.path.exists(db_path):
        st.error(f"Banco de dados não encontrado em '{db_path}'. Execute a ingestão de dados primeiro.")
        st.stop()
        
    engine = create_engine(f'sqlite:///{db_path}')
    df = pd.read_sql('SELECT * FROM dengue', engine)
    df['data'] = pd.to_datetime(df['data'])
    return df

df = load_data()

# -----------------------------------------------------------------------------
# 3. BARRA LATERAL (SIDEBAR) - FILTROS E FOOTER
# -----------------------------------------------------------------------------
st.sidebar.image("https://img.icons8.com/color/96/mosquito.png", width=70)
st.sidebar.title("Filtros do Dashboard")

# 3.1 Slider de Anos (2015 - 2024)
min_year_data = int(df['ano'].min())
max_year_data = int(df['ano'].max())
ano_inicio, ano_fim = st.sidebar.slider(
    "Período (Anos)",
    min_value=min_year_data,
    max_value=max_year_data,
    value=(min_year_data, max_year_data),
    step=1
)

# 3.2 Selectbox de Região
list_regioes = ["Todas"] + sorted(list(df['regiao'].unique()))
regiao_sel = st.sidebar.selectbox("Região", options=list_regioes)

# 3.3 Selectbox de UF (Dinamicamente filtrado pela região)
if regiao_sel == "Todas":
    list_ufs = ["Todas"] + sorted(list(df['uf'].unique()))
else:
    list_ufs = ["Todas"] + sorted(list(df[df['regiao'] == regiao_sel]['uf'].unique()))

uf_sel = st.sidebar.selectbox("Unidade Federativa (UF)", options=list_ufs)

# 3.4 Multiselect de Nível de Alerta
list_alertas = sorted(list(df['nivel_alerta'].unique()))
alerta_sel = st.sidebar.multiselect(
    "Nível de Alerta",
    options=list_alertas,
    default=list_alertas
)

# Rodapé da Barra Lateral
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style='font-size: 0.85rem; color: #4B5563; background-color: #F9FAFB; padding: 10px; border-radius: 6px; border: 1px solid #E5E7EB;'>
    <strong>Projeto Acadêmico G1</strong><br>
    <strong>Disciplina:</strong> Linguagens de Programação<br>
    <strong>Professor:</strong> Alexandre Neves Louzada<br>
    <strong>Aluno:</strong> Alexandre Souza de Abreu Junior
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 4. APLICAÇÃO DOS FILTROS
# -----------------------------------------------------------------------------
df_filtered = df[(df['ano'] >= ano_inicio) & (df['ano'] <= ano_fim)].copy()

if regiao_sel != "Todas":
    df_filtered = df_filtered[df_filtered['regiao'] == regiao_sel]

if uf_sel != "Todas":
    df_filtered = df_filtered[df_filtered['uf'] == uf_sel]

if alerta_sel:
    df_filtered = df_filtered[df_filtered['nivel_alerta'].isin(alerta_sel)]
else:
    st.warning("Selecione ao menos um Nível de Alerta nos filtros da barra lateral.")
    st.stop()

if df_filtered.empty:
    st.info("Nenhum registro encontrado para os filtros selecionados.")
    st.stop()

# -----------------------------------------------------------------------------
# 5. TÍTULO E INTRODUÇÃO
# -----------------------------------------------------------------------------
st.markdown("<h1 class='main-header'>🦟 Dashboard Epidemiológico: Monitoramento da Dengue no Brasil</h1>", unsafe_allow_html=True)
st.markdown("""
<p class='sub-header'>
Plataforma interativa para análise dos surtos de dengue, perfil epidemiológico e determinantes climáticos 
(temperatura e pluviosidade) no território brasileiro.
</p>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 6. CARDS DE KPIS DINÂMICOS
# -----------------------------------------------------------------------------
casos_totais = int(df_filtered['casos_dengue'].sum())
internacoes_totais = int(df_filtered['internacoes'].sum())
obitos_totais = int(df_filtered['obitos'].sum())
incidencia_media = df_filtered['incidencia_100k'].mean()
taxa_letalidade = (obitos_totais / casos_totais * 100) if casos_totais > 0 else 0.0

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    label="Casos Notificados",
    value=f"{casos_totais:,}".replace(",", ".")
)
col2.metric(
    label="Total Internações",
    value=f"{internacoes_totais:,}".replace(",", ".")
)
col3.metric(
    label="Óbitos Confirmados",
    value=f"{obitos_totais:,}".replace(",", ".")
)
col4.metric(
    label="Incidência Média / 100k",
    value=f"{incidencia_media:.2f}"
)
col5.metric(
    label="Taxa de Letalidade",
    value=f"{taxa_letalidade:.3f}%"
)

st.markdown("---")

# -----------------------------------------------------------------------------
# 7. GRÁFICOS INTERATIVOS (PLOTLY EXPRESS & GRAPH OBJECTS)
# -----------------------------------------------------------------------------
st.subheader("📈 Análise Temporal e Distribuição Geográfica")

col_left, col_right = st.columns([1.2, 1])

with col_left:
    st.markdown("##### Série Temporal: Evolução de Casos vs Clima")
    
    # Agrupamento temporal por mês/ano
    df_temporal = df_filtered.groupby('data').agg({
        'casos_dengue': 'sum',
        'chuva_mm': 'mean',
        'temperatura_media': 'mean'
    }).reset_index()

    fig_temporal = make_subplots(specs=[[{"secondary_y": True}]])

    fig_temporal.add_trace(
        go.Scatter(
            x=df_temporal['data'], 
            y=df_temporal['casos_dengue'], 
            name="Casos Dengue", 
            line=dict(color="#DC2626", width=2.5)
        ),
        secondary_y=False,
    )

    fig_temporal.add_trace(
        go.Scatter(
            x=df_temporal['data'], 
            y=df_temporal['chuva_mm'], 
            name="Pluviosidade (mm)", 
            line=dict(color="#2563EB", width=1.5, dash='dash')
        ),
        secondary_y=True,
    )

    fig_temporal.update_layout(
        title_text="Tendência Temporal de Notificações e Precipitação",
        xaxis_title="Data",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=20, r=20, t=50, b=20),
        height=380,
        hovermode="x unified"
    )

    fig_temporal.update_yaxes(title_text="Casos Notificados", secondary_y=False)
    fig_temporal.update_yaxes(title_text="Chuva Média (mm)", secondary_y=True)

    st.plotly_chart(fig_temporal, use_container_width=True)

with col_right:
    st.markdown("##### Top 15 Municípios com Maior Número de Casos")
    
    top15_muni = df_filtered.groupby(['municipio', 'uf'])['casos_dengue'].sum().reset_index()
    top15_muni['localidade'] = top15_muni['municipio'] + " (" + top15_muni['uf'] + ")"
    top15_muni = top15_muni.sort_values(by='casos_dengue', ascending=True).tail(15)

    fig_top15 = px.bar(
        top15_muni,
        x='casos_dengue',
        y='localidade',
        orientation='h',
        color='casos_dengue',
        color_continuous_scale='Reds',
        labels={'casos_dengue': 'Casos Acumulados', 'localidade': 'Município (UF)'},
        text_auto='.2s'
    )
    fig_top15.update_layout(
        height=380,
        margin=dict(l=20, r=20, t=30, b=20),
        coloraxis_showscale=False
    )
    st.plotly_chart(fig_top15, use_container_width=True)

st.markdown("---")

# -----------------------------------------------------------------------------
# 8. GRÁFICOS ESTATÍSTICOS (MATPLOTLIB / SEABORN)
# -----------------------------------------------------------------------------
st.subheader("📊 Diagnóstico Estatístico e Sazonalidade")

col_stat1, col_stat2 = st.columns(2)

with col_stat1:
    st.markdown("##### Sazonalidade Mensal Notificada (Boxplot / Distribuição)")
    
    fig_sns1, ax_sns1 = plt.subplots(figsize=(8, 5))
    sns.set_theme(style="whitegrid")
    
    meses_labels = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    
    sns.boxplot(
        data=df_filtered,
        x='mes',
        y='casos_dengue',
        palette="YlOrRd",
        hue='mes',
        legend=False,
        ax=ax_sns1,
        showfliers=False
    )
    
    ax_sns1.set_xticklabels(meses_labels)
    ax_sns1.set_title("Distribuição Mensal de Casos (Sem Outliers)", fontsize=12, fontweight='bold', pad=10)
    ax_sns1.set_xlabel("Mês", fontsize=10)
    ax_sns1.set_ylabel("Casos de Dengue", fontsize=10)
    plt.tight_layout()
    
    st.pyplot(fig_sns1)

with col_stat2:
    st.markdown("##### Matriz de Correlação de Pearson (Clima vs Saúde)")
    
    fig_sns2, ax_sns2 = plt.subplots(figsize=(8, 5))
    
    cols_corr = ['chuva_mm', 'temperatura_media', 'casos_dengue', 'internacoes', 'obitos', 'incidencia_100k']
    corr = df_filtered[cols_corr].corr(method='pearson')
    
    sns.heatmap(
        corr,
        annot=True,
        fmt=".2f",
        cmap="Blues",
        vmin=-1,
        vmax=1,
        linewidths=0.5,
        cbar_kws={"shrink": .8},
        ax=ax_sns2
    )
    
    ax_sns2.set_title("Correlação Estatística de Pearson", fontsize=12, fontweight='bold', pad=10)
    plt.xticks(rotation=45, ha='right', fontsize=9)
    plt.yticks(rotation=0, fontsize=9)
    plt.tight_layout()
    
    st.pyplot(fig_sns2)

st.markdown("---")

# -----------------------------------------------------------------------------
# 9. TABELA INTERATIVA (EXPANDER)
# -----------------------------------------------------------------------------
with st.expander("🔍 Explorar e Exportar Base de Dados Filtrada"):
    st.markdown(f"**Total de linhas retornadas:** {len(df_filtered):,}".replace(",", "."))
    
    st.dataframe(
        df_filtered[[
            'ano', 'mes', 'data', 'regiao', 'uf', 'municipio', 
            'populacao', 'chuva_mm', 'temperatura_media', 'casos_dengue', 
            'internacoes', 'obitos', 'incidencia_100k', 'nivel_alerta',
            'taxa_internacao_pct', 'taxa_letalidade_pct'
        ]],
        use_container_width=True,
        height=300
    )
    
    csv_data = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Baixar Dados Filtrados em CSV",
        data=csv_data,
        file_name=f"dengue_filtrado_{ano_inicio}_{ano_fim}.csv",
        mime="text/csv"
    )

st.markdown("---")

# -----------------------------------------------------------------------------
# 10. CONCLUSÃO EXECUTIVA E RECOMENDAÇÕES DE SAÚDE PÚBLICA
# -----------------------------------------------------------------------------
st.subheader("💡 Conclusão Executiva e Diretrizes de Saúde Pública")

st.info("""
### Principais Achados Epidemiológicos:
1. **Padrão Sazonal Crítico**: As notificações concentram-se no primeiro semestre do ano (especialmente entre os meses de Janeiro e Maio), impulsionadas pela combinação de temperaturas elevadas e alta pluviosidade.
2. **Correlação Pluviométrica**: Existe uma forte associação estatística entre o volume de chuvas e o aumento de focos do vetor *Aedes aegypti*, demandando ações preventivas prévias aos períodos chuvosos.
3. **Pressão no Sistema de Saúde**: Municípios com alta densidade populacional registram os maiores picos absolutos de hospitalizações, exigindo suporte logístico direcionado às redes de atenção básica e urgência.

### Recomendações Estratégicas:
- **Inteligência Preditiva**: Utilizar dados meteorológicos antecipados para disparar alertas de intensificação de combate a criadouros.
- **Gestão de Leitos**: Redirecionamento planejado de insumos e profissionais de saúde entre os meses de Fevereiro e Abril nas regiões de alto risco.
- **Engajamento Comunitário**: Campanha contínua de conscientização focada na eliminação de reservatórios de água parada.
""")
