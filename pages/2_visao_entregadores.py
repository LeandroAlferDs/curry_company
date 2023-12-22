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


#import dataset
df= pd.read_csv('programacao/train.csv')

df1 = df.copy()

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
df1['Order_Date']= pd.to_datetime(df1['Order_Date'],format='%d-%m-%Y')
#4.Convertendo a coluna multiple_deliveries de string para inteiro
linhas_selecionadas= (df1['multiple_deliveries']!= 'NaN ')
df1 = df1.loc[linhas_selecionadas, :].copy()
df1['multiple_deliveries']=df1['multiple_deliveries'].astype( int )
#5.
#6.Removendo os espaços dentro das string/texto/objects
df1.loc[:, 'ID'] = df1.loc[:,'ID'].str.strip()
df1.loc[:, 'Road_traffic_density'] = df1.loc[:,'Road_traffic_density'].str.strip()
df1.loc[:, 'Type_of_order'] = df1.loc[:,'Type_of_order'].str.strip()
df1.loc[:, 'Type_of_vehicle'] = df1.loc[:,'Type_of_vehicle'].str.strip()
df1.loc[:, 'City'] = df1.loc[:,'City'].str.strip()
df1.loc[:, 'Festival'] = df1.loc[:,'Festival'].str.strip()

#7.Limpando a coluna Time_taken(min)
df1['Time_taken(min)']  = df1['Time_taken(min)'].apply( lambda x : x.split('(min)')[1])
linhas_selecionadas = (df1['City']!= 'NaN ' )
df1 = df1.loc[linhas_selecionadas, :].copy()

df1['Time_taken(min)'] = df1['Time_taken(min)'].astype( int )



#===============================================
#Barra Lateral
#===============================================
st.header('Marketplace - Visão Entregadores')
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
    min_value=datetime(2022, 2, 11),
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

tab1,tab2,tab3 = st.tabs(['Visão Gerencial','-','-'])

with tab1:
    with st.container ():
        st.title('Métricas Gerais')

        col1,col2,col3,col4 = st.columns(4,gap='large')
        with col1: 
        #A maior idade dos entregadores
            maior_idade = df1.loc[:,'Delivery_person_Age'].max()
            col1.metric ('Maior Idade', maior_idade)
        #A menor idade dos entregadores
        with col2: 
            menor_idade = df1.loc[:,'Delivery_person_Age'].min()
            col2.metric ('Menor Idade', menor_idade)
        with col3:
            melhor_condicao = df1.loc[:,'Vehicle_condition'].max()
            col3.metric('Melhor condição', melhor_condicao )
        with col4:
            pior_condicao = df1.loc[:,'Vehicle_condition'].min()
            col4.metric('Pior Condição', pior_condicao )

    with st.container():
        st.markdown("""---""")
        st.title('Avaliações')

        col1,col2 = st.columns(2)
        with col1:
            st.subheader('Avaliações média por entregador')
            df_avg_media = (df1.loc[:,['Delivery_person_Ratings','Delivery_person_ID']]
                                                                        .groupby('Delivery_person_ID')
                                                                        .mean()
                                                                        .reset_index())
            st.dataframe(df_avg_media)

        with col2:
            st.subheader('Avaliação média e desvio padrão por trânsito')
            df_avg_std_rating_by_traffic= ( df1.loc[:,['Delivery_person_Ratings','Road_traffic_density']]
                                           .groupby('Road_traffic_density')
                                           .agg( {'Delivery_person_Ratings':['mean','std']}))
            #mudança de nome das colunas
            df_avg_std_rating_by_traffic.columns = ['Delivery_mean','Delivery_std']
            #reset de index
            df_avg_std_rating_by_traffic = df_avg_std_rating_by_traffic.reset_index()
            
            
            #df_avg_std_rating_by_traffic
            st.dataframe (df_avg_std_rating_by_traffic)


            st.subheader('Avaliação média e desvio padrão por cond/clima')
            df_avg_std_rating_by_weather= ( df1.loc[:,['Delivery_person_Ratings','Weatherconditions']].groupby('Weatherconditions')
                            .agg( {'Delivery_person_Ratings':['mean','std']}))
            #mudança de nome das colunas
            df_avg_std_rating_by_weather.columns = ['Delivery_mean','Delivery_std']
            #reset de index 
            df_avg_std_rating_by_weather = df_avg_std_rating_by_weather.reset_index()
            st.dataframe (df_avg_std_rating_by_weather)

        with st.container():
            st.markdown("""___""")
            st.title('Velocidade de Entrega')

            col1,col2 = st.columns(2)
            with col1:
                st.subheader('Top Entregadores mais rápidos por cidade')
                df2= (df1.loc[:,['Delivery_person_ID','Time_taken(min)','City']]
                      .groupby(['City','Delivery_person_ID'])
                      .mean().sort_values(['City','Time_taken(min)'],ascending=True)
                      .reset_index())
                df_aux01 = df2.loc[df2['City']=='Metropolitian',:].head(10)
                df_aux02 = df2.loc[df2['City']== 'Urban',:].head(10)
                df_aux03 = df2.loc[df2['City']== 'Semi-Urban',:].head(10)
                df3 = df2.loc[df2['City']!= 'NaN', :]#tratei sozinho essa linha
                df3 =pd.concat([df_aux01,df_aux02,df_aux03]).reset_index(drop=True)
                st.dataframe(df3)

            with col2:
                st.subheader('Top Entregadores mais lentos por cidade')
                df2= (df1.loc[:,['Delivery_person_ID','Time_taken(min)','City']]
                      .groupby(['City','Delivery_person_ID']).mean()
                      .sort_values(['City','Time_taken(min)'],ascending=False)
                      .reset_index())
                
                df_aux01 = df2.loc[df2['City']=='Metropolitian',:].head(10)
                df_aux02 = df2.loc[df2['City']== 'Urban',:].head(10)
                df_aux03 = df2.loc[df2['City']== 'Semi-Urban',:].head(10)
                df3 =pd.concat([df_aux01,df_aux02,df_aux03]).reset_index(drop=True)
                st.dataframe(df3)