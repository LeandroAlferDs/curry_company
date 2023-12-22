#Libraries
from haversine import haversine #haversine serve para habilitar calculos lat/long
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from PIL import Image

#bibliotecas necessarias

import pandas as pd
import streamlit as st
import folium
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster


st.set_page_config(page_title='Visão Empresa',page_icon='', layout='wide')

#________________________________________
#Funções
#________________________________________
def country_maps( df1 ):

        df_aux = (df1.loc[:,['City','Road_traffic_density','Delivery_location_latitude','Delivery_location_longitude']]
                  .groupby(['City','Road_traffic_density'])
                  .median()
                  .reset_index())
        
        map = folium.Map()

        for index, location_info in df_aux.iterrows():
            folium.Marker( [location_info['Delivery_location_latitude'],
                        location_info['Delivery_location_longitude']],
                        popup= location_info[['City','Road_traffic_density']] ).add_to ( map)
                        

        folium_static(map, width=1024, height=600)

def order_share_by_week( df1 ):
            df_aux01 = df1.loc[:,['ID','week_of_year']].groupby('week_of_year').count().reset_index()
            df_aux02 = (df1.loc[:,['Delivery_person_ID','week_of_year']]
                               .groupby('week_of_year')
                               .nunique()
                               .reset_index())

            df_aux = pd.merge(df_aux01, df_aux02, how='inner', on='week_of_year' )
            df_aux['order_by_delivery'] = df_aux['ID'] / df_aux['Delivery_person_ID']
            fig = px.line(df_aux, x='week_of_year', y='order_by_delivery')
            return fig

def order_by_week(df1):
         #criar a coluna de semana
            df1['week_of_year'] = df1['Order_Date'].dt.strftime ('%U')
            df_aux = df1.loc[:,['ID','week_of_year']].groupby ('week_of_year').count().reset_index()
            fig = px.line(df_aux, x='week_of_year', y='ID')
            return fig

def traffic_order_city( df1):
    df_aux = (df1.loc[:,['ID','City','Road_traffic_density']]
             .groupby([ 'City','Road_traffic_density'])
             .count()
             .reset_index())
    fig = px.scatter( df_aux, x='City', y='Road_traffic_density', size='ID', color='City')
    return ( fig )

def traffic_order_share( df1 ):
    df_aux = (df1.loc[:, ['ID','Road_traffic_density']].groupby('Road_traffic_density')
                                                        .count()
                                                        .reset_index())

    df_aux = df_aux.loc[df_aux['Road_traffic_density']!= 'NaN', :]         
    df_aux['entregas_perc']= df_aux['ID']/ df_aux['ID'].sum()
    fig = px.pie(df_aux, values='entregas_perc', names='Road_traffic_density')
    return fig

def order_metric( df1 ):
    cols=['ID','Order_Date']
    #seleção de linhas
    df_aux= df1.loc[:,cols].groupby('Order_Date').count().reset_index()

    #desenhar o gráfico de linhas
    fig = px.bar( df_aux, x='Order_Date', y='ID')

    return fig

def clean_code( df1 ):
    """Esta funcao tem a responsabilidade de limpar o dataframe

        Tipos de limpeza:
        1. Remoção dos dados NaN
        2. Mudança do tipo da coluna de dados
        3. Remoção dos espaços das variáveis de texto
        4. Formatação da coluna de datas
        5. Limpeza da coluna de tempo. (remoção do texto da variável numérica)

        Input: Dataframe
        Output: Dataframe

    """
    #1.Convertendo a coluna Age de string para inteiro
    linhas_selecionadas = (df1['Delivery_person_Age']!= 'NaN ' )
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = (df1['Road_traffic_density']!= 'NaN ' )
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = (df1['City']!= 'NaN ' )
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = (df1['Festival']!= 'NaN ' )
    df1 = df1.loc[linhas_selecionadas, :].copy()

    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype( int )

    #2.Convertendo a coluna Ratings de String para float
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)

    #3.Convertendo a coluna Order_Date de string para date
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'],format='%d-%m-%Y')

    #4.Convertendo a coluna multiple_deliveries de string para inteiro
    linhas_selecionadas = (df1['multiple_deliveries']!= 'NaN ')

    df1 = df1.loc[linhas_selecionadas, :].copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype( int )
    
    #5.Removendo os espaços dentro das string/texto/objects
    df1.loc[:, 'ID'] = df1.loc[:,'ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:,'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:,'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:,'Type_of_vehicle'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:,'City'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:,'Festival'].str.strip()

    #6.Limpando a coluna Time_taken(min)
    df1['Time_taken(min)']  = df1['Time_taken(min)'].apply( lambda x : x.split('(min)')[1])
    linhas_selecionadas = (df1['City']!= 'NaN ' )
    df1 = df1.loc[linhas_selecionadas, :].copy()

    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype( int )
    return df1
#-----------------------------Início da Estrutura lógica do código-------------------------
#import dataset
df= pd.read_csv('programacao/train.csv')

#Limpando os dados
df1 = clean_code (df)



#===============================================
#Barra Lateral
#===============================================
st.header('Marketplace - Visão Cliente')
#image_path = 'logo1.png'
image = Image.open('logo1.png')
st.sidebar.image ( image, width=280)



st.sidebar.markdown ('# Cury Company')
st.sidebar.markdown ('## Fastest Delivery in Town')
st.sidebar.markdown ("""___""")

st.sidebar.markdown ('# Selecione a data:')

date_slider= st.sidebar.slider (
    '',
    value=datetime(2022, 4, 13),
    min_value=datetime(2022, 2, 12),
    max_value=datetime(2022, 4, 6),
    format="DD-MM-YYYY")

st.header( date_slider)
st.sidebar.markdown ("""___""")

traffic_options = st.sidebar.multiselect(
    'Insira a condição do trânsito',
    ['Low','Medium','High','Jam'],
    default='Low')
st.sidebar.markdown ("""___""")
st.sidebar.markdown ("Powered by LeandroAlfer")
st.sidebar.markdown ("""___""")

#filtro de datas
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas,:]

#filtro de trânsito
linhas_selecionadas = df1['Road_traffic_density'].isin( traffic_options )
df1 = df1.loc[linhas_selecionadas,:]

#===============================================
#Layout no Streamlit
#===============================================

tab1,tab2,tab3 = st.tabs(['Visão Gerencial','Visão Tática','Visão Geográfica'])

with tab1:
    with st.container():
        #Order Metric
        fig = order_metric (df1)
        st.markdown('# Pedidos por Dia')
        st.plotly_chart(fig,use_container_width=True)

    #desenhar o grafico de linhas (plotly)

    fig = px.bar(df1,x='Order_Date',y='ID')#coloquei a variavel df1 no lugar de df_aux 
    
    col1, col2 = st.columns(2)
with col1:
    fig = traffic_order_share( df1 )
    st.header('Pedidos por Tipo de Tráfego')
    st.plotly_chart(fig, use_container_width=True)

    
    
with col2:
    st.header('Volume de pedidos por cidade e por tipo de tráfego')
    fig = traffic_order_city( df1 )
    st.plotly_chart(fig, use_container_width=True )

    
with tab2:
    with st.container():
        st.header('Pedidos por Semana')
        fig = order_by_week( df1 )
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        st.header("Pedidos por Entregador por Semana")
        fig = order_share_by_week(df1)
        st.plotly_chart(fig, use_container_width=True)

        

with tab3:
        
        st.header('Mapa Local')
        
        country_maps( df1 )