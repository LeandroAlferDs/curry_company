#Libraries
from haversine import haversine #haversine serve para habilitar calculos lat/long
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from PIL import Image

#bibliotecas necessarias

import pandas as pd
import numpy as np
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

#visão empresa
#colunas
cols=['ID','Order_Date']
#seleção de linhas
df_aux= df1.loc[:,cols].groupby('Order_Date').count().reset_index()
df_aux.head(5)
#desenhar o grafico de linhas (plotly)


px.bar(df_aux,x='Order_Date',y='ID')


#===============================================
#Barra Lateral
#===============================================
st.header('Marketplace - Visão Restaurantes')
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
    default='High')
st.sidebar.markdown ("""___""")
st.sidebar.markdown ("Powered by LeandroAlfer")
st.sidebar.markdown ("""___""")

#filtro de datas
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas,:]

#filtro de trânsito
linhas_selecionadas = df1['Road_traffic_density'].isin( traffic_options )
df1 = df1.loc[linhas_selecionadas,:]

tab1,tab2,tab3 = st.tabs(['Visão Gerencial','-','-'])

with tab1:
    with st.container ():
        st.title('Métricas Gerais')

        col1,col2,col3= st.columns(3,gap='large')

        with col1:
            delivery_unique = df1.loc[:,'Delivery_person_ID'].nunique()
            col1.metric("Entregadores Únicos", delivery_unique)
        with col2:
            cols = ['Restaurant_latitude','Restaurant_longitude','Delivery_location_latitude','Delivery_location_longitude']
            df1['Distance']=df1.loc[:,cols].apply( lambda x: #lambda faz percorrer a matriz linha por linha.
                                      # e criacao de coluna Distance na atribuição da linha de cima.
                    haversine(      #haversine faz calcular lat/long
            (x['Restaurant_latitude'], x['Restaurant_longitude']),
            (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)
            avg_distance = np.round(df1['Distance'].mean(),2)
            col2.metric('Distancia media das entregas', avg_distance) 
            
        with col3: 
            df_aux= (df1.loc[:,['Time_taken(min)','Festival']]
                         .groupby('Festival')
                         .agg({'Time_taken(min)' : ['mean','std']}))
            
            df_aux.columns = ['avg_time','std_time']
            df_aux = df_aux.reset_index()
            df_aux = np.round(df_aux.loc[df_aux['Festival']=='Yes','avg_time'],2 )
            col3.metric('Tempo Médio de Entrega c/ Festival', df_aux)

with st.container():
        col4,col5,col6= st.columns(3,gap='large')
        with col4: 
            df_aux= (df1.loc[:,['Time_taken(min)','Festival']]
                         .groupby('Festival')
                         .agg({'Time_taken(min)' : ['mean','std']}))
            
            df_aux.columns = ['avg_time','std_time']
            df_aux = df_aux.reset_index()
            df_aux = np.round(df_aux.loc[df_aux['Festival']=='Yes','std_time'],2 )
            col4.metric('Desvio Padrão de Entrega c/ Festival', df_aux)
        with col5: 
            df_aux= (df1.loc[:,['Time_taken(min)','Festival']]
                         .groupby('Festival')
                         .agg({'Time_taken(min)' : ['mean','std']}))
            
            df_aux.columns = ['avg_time','std_time']
            df_aux = df_aux.reset_index()
            df_aux = np.round(df_aux.loc[df_aux['Festival']=='No','avg_time'],2 )
            col5.metric('Tempo Médio de Entrega c/ Festival', df_aux)
        with col6: 
            df_aux= (df1.loc[:,['Time_taken(min)','Festival']]
                         .groupby('Festival')
                         .agg({'Time_taken(min)' : ['mean','std']}))
            
            df_aux.columns = ['avg_time','std_time']
            df_aux = df_aux.reset_index()
            df_aux = np.round(df_aux.loc[df_aux['Festival']=='No','std_time'],2 )
            col6.metric('Desvio Padrão de Entrega c/ Festival', df_aux)
            
        st.markdown("""___""")
with st.container():
        st.title("Tempo Médio de entrega por cidade")
        cols = ['Delivery_location_latitude','Delivery_location_longitude','Restaurant_latitude','Restaurant_longitude']
        df1['distance'] = df1.loc[:,cols].apply( lambda x:
                                        haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                        (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)
        
        avg_distance = df1.loc[:,['City','distance']].groupby('City').mean().reset_index()
        fig = go.Figure( data=[go.Pie( labels=avg_distance['City'], values= avg_distance['distance'], pull=[0,0.1,0])])
        st.plotly_chart(fig)

        st.markdown("""___""")
with st.container ():
        st.title( "Distribuição do Tempo")
        col1, = st.columns (1)
        with col1:
            
            df_aux= (df1.loc[:, ['City','Time_taken(min)']]
                            .groupby('City')
                            .agg({'Time_taken(min)':['mean','std']}))
            df_aux.columns = ['avg_time','std_time']
            df_aux = df_aux.reset_index()

            fig = go.Figure()
            fig.add_trace( go.Bar(name='Control', x = df_aux['City'], y=df_aux['avg_time'], error_y=dict(type='data', array=df_aux['std_time'])))
            fig.update_layout(barmode='group')
            st.plotly_chart(fig)

        
with st.container():
        
        df_aux = (df1.loc[:, ['City','Time_taken(min)','Road_traffic_density']]
                     .groupby(['City', 'Road_traffic_density'])     
                     .agg({'Time_taken(min)':['mean','std']}))
        
        df_aux.columns = ['avg_time','std_time']
        df_aux = df_aux.reset_index()

        fig = px.sunburst(df_aux, path=['City','Road_traffic_density'], values='avg_time',
                            color='std_time', color_continuous_scale='RdBu',
                            color_continuous_midpoint=np.average(df_aux['std_time']))
        st.plotly_chart(fig)


        st.markdown("""___""")
