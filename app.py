import pandas as pd
import plotly.express as px
import streamlit as st

#Configuração da Página

# Definir titulo, icone e layout p ocupar a tela inteira
st.set_page_config(
    page_title='Dashboard de Salários na Área de Dados',
    page_icon='📉',
    layout='wide')

#Carregar os Dados
@st.cache_data
def carregar_dados():
    url = "https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/main/dados-imersao-final.csv"
    df = pd.read_csv(url, sep=',')
    return df

df = carregar_dados()

#Barra Lateral de Filtros
st.sidebar.header("🔎 Filtros")

#Filtro do ano
anos_disponiveis = sorted(df['ano'].unique()) #sorted organiza os anos
anos_selecionados = st.sidebar.multiselect(label='Ano',
                                           options=anos_disponiveis,
                                           default=anos_disponiveis)

#Filtro Senioridade
senioridade_disponivel = sorted(df['senioridade'].unique())
senioridade_selecionada = st.sidebar.multiselect(label='Senioridade',
                                                 options=senioridade_disponivel,
                                                 default=senioridade_disponivel)

#Filtro Contrato
contratos_disponiveis = sorted(df['contrato'].unique())
contratos_selecionados = st.sidebar.multiselect(label='Contrato do Funcionário',
                                               options=contratos_disponiveis,
                                               default=contratos_disponiveis)

#Filtro tamanho da empresa
tamanhos_disponiveis = sorted(df['tamanho_empresa'].unique())
tamanhos_selecionados = st.sidebar.multiselect(label='Tamanho da Empresa',
                                               options=tamanhos_disponiveis,
                                               default=tamanhos_disponiveis)

#--- Filtragem do DataFrame ---
#filtragem do df baseado nas escolhas feitas nos filtros escolhidos
df_filtrado = df[
    df['ano'].isin(anos_selecionados) & # & é um and (e)
    df['senioridade'].isin(senioridade_selecionada) &
    df['tamanho_empresa'].isin(tamanhos_selecionados) &
    df['contrato'].isin(contratos_selecionados)
]

#--- Conteudo Principal ---
st.title('📊 Dashboard de Análise de Salários na Área de Dados')
st.markdown('Explore os dados salariais na area de dados nos ultimos anos. Utilize os filtros à esquerda para filtrar sua análise')

# - Metricas Principais - 
st.subheader('Métricas Gerais (Salário anual em USD)')

if not df_filtrado.empty: #se o df nao estiver vazio
    salario_medio = df_filtrado['usd'].mean()
    salario_maximo = df_filtrado['usd'].max()
    total_registros = df_filtrado.shape[0] #qtd linhas diz qts registross tem
    cargo_mais_frequente = df_filtrado['cargo'].mode()[0] #mode é a moda estatística, [0] pega o 1o item da lista
else:
    salario_medio,salario_maximo,total_registros,cargo_mais_frequente = 0,0,0,0

col1,col2,col3,col4 = st.columns(4) #dividindo a pagina em 4 colunas
col1.metric('Salario Medio',f'${salario_medio:,.0f}')
col2.metric('Salario Maximo',f'${salario_maximo:,.0f}')
col3.metric('Total de Registros',f'{total_registros:,}')
col4.metric('Cargo mais frequente',cargo_mais_frequente)

st.markdown('---')

#--- Analises Visuais ---
st.subheader('Gráficos') #subtitulo

col_graf1,col_graf2 = st.columns(2)

with col_graf1: #feito na coluna 1
    if not df_filtrado.empty:
        top_cargos = df_filtrado.groupby('cargo')['usd'].mean().nlargest(10).sort_values(ascending=True).reset_index()
        grafico_cargos = px.bar(
            top_cargos,
            x='usd',
            y='cargo',
            orientation='h', #orientação horizontal
            title='Top 10 cargos por salario Médio',
            labels = {'usd': 'Media Salarial anual (em USD)','cargo':''}
        )
        #title_x : mover o titulo x p direita, yaxis: 
        grafico_cargos.update_layout(title_x=0.1,yaxis={'categoryorder':'total ascending'})
        #exibir o grafico no streamlit
        st.plotly_chart(grafico_cargos, use_container_width=True)
    else:
        st.warning('Nenhum dado para exibir no grafico de cargos')


with col_graf2:
    if not df_filtrado.empty:
        grafico_hist = px.histogram(
            df_filtrado,
            x='usd',
            nbins=30,
            title='Distribuição Salarial dos funcionários',
            labels = {'usd': 'Media Salarial anual (em USD)','count':''}
        )
        #title_x : mover o titulo x p direita, yaxis: 
        grafico_hist.update_layout(title_x=0.1)
        st.plotly_chart(grafico_hist, use_container_width=True)
    else:
        st.warning('Nenhum dado para exibir no grafico de cargos')
    
#Grafcios 3 e 4 abaixo do 1 e 2

col_graf3,col_graf4 = st.columns(2)

with col_graf3: 
    if not df_filtrado.empty:
        remoto_contagem = df_filtrado['remoto'].value_counts().reset_index()
        remoto_contagem.columns = ['tipo_trabalho','quantidade']
        grafico_remoto = px.pie(
            remoto_contagem,
            names='tipo_trabalho',
            values='quantidade',
            title='Proporção dos tipos de trabalho',
            hole=0.5
        )
        grafico_remoto.update_traces(textinfo='percent+label')
        grafico_remoto.update_layout(title_x=0.1)
        #exibir o grafico no streamlit
        st.plotly_chart(grafico_remoto, use_container_width=True)
    else:
        st.warning('Nenhum dado para exibir no grafico de cargos')

with col_graf4:
    if not df_filtrado.empty:
        df_ds = df_filtrado[df_filtrado['cargo']=='Data Scientist']
        media_pais = df_ds.groupby('residencia_iso3')['usd'].mean().reset_index()
        grafico_paises = px.choropleth(media_pais,
                                       locations='residencia_iso3',
                                       color='usd',
                                       color_continuous_scale='rdylgn',
                                       title='Salario medio de Cientista de Dados por pais',
                                       labels={'usd':'Salario Medio (usd)','residencia_iso3':'Pais'})
        grafico_paises.update_layout(title_x=0.1)
        st.plotly_chart(grafico_paises,use_container_width=True)

#---Tabela de Dados Detalhados ---
st.subheader('Dados detalhados')
st.dataframe(df_filtrado)

