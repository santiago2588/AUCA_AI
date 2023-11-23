import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import numpy as np
import plotly.express as px
from statsmodels.tsa.arima.model import ARIMA
from Calculations.Calculations import *

#st.set_page_config(layout="wide",page_title="AUCA",page_icon="🌿")

#Codigo para eliminar el boton de menu y logo de streamlit
# hide_menu_style = """
#         <style>
#         #MainMenu {visibility: hidden; }
#         footer {visibility: hidden;}
#         </style>
#         """
# st.markdown(hide_menu_style, unsafe_allow_html=True)

from PIL import Image
image = Image.open('Resources/AUCA.png')
st.image(image)

#Instrucciones
st.markdown("# The Net-Zero copilot for industrial SMEs")

st.write("This example presents the results when processing the database hosted in Google Sheets.")
st.link_button(label='Access the database',url='https://docs.google.com/spreadsheets/d/1FB-lPd8usv_XpFNSm0t4W6C7ogdcHIO1FuJZ2Dmvm_4/edit#gid=1930401626')

st.markdown("## Results")

with st.expander("Total costs and emissions",expanded=True):

    col1,col2=st.columns(2)

    with col1:
        st.metric('Total emisiones de carbono',str("%.1f" % np.float_(emissions_total))+ ' kg CO2-eq')

    with col2:
        st.metric('Costo total de energia',str("%.1f" % np.float_(cost_total))+ ' USD')

    tab1,tab2=st.tabs(['Total emisiones','Total costos'])

    #Ocultar toolbar de plotly
    config = {'displayModeBar': False}

    with tab1:
        fig_total=px.line(results,x=date.unique(),y=co2_total_time,markers=True,line_shape='spline')
        fig_total.update_layout(xaxis_title='Fecha',yaxis_title='kg CO2')
        st.plotly_chart(fig_total, use_container_width=True,config=config)

    with tab2:
        fig_total=px.line(results,x=date.unique(),y=costo_total_time,markers=True,line_shape='spline')
        fig_total.update_layout(xaxis_title='Fecha',yaxis_title='USD')
        st.plotly_chart(fig_total, use_container_width=True,config=config)

    st.markdown('Detalle de los resultados')
    st.dataframe(results)

    #Descargar csv de los resultados
    def convert_df(df):
        return df.to_csv().encode('utf-8')

    csv_results = convert_df(results)
    st.download_button("📥Press to Download", csv_results, "resultados.csv", "text/csv", key='download-csv')

with st.expander('Indicadores por unidad de producción',expanded=True):
    col1,col2=st.columns(2)
    with col1:
        st.metric('Intensidad de emisiones promedio',str("%.1f" % np.float_(emissions_total/prod_total))+ ' kg CO2-eq / '+unit)

    with col2:
        st.metric('Intensidad energetica promedio',str("%.1f" % np.float_(energy_total/prod_total))+ ' MJ / '+unit)

    tab1,tab2=st.tabs(['Intensidad emisiones','Intensidad energetica'])

    with tab1:
        co2_total=results.groupby('Fecha')['Emisiones kg CO2-eq'].sum()
        prod_diaria=df_prod_mod.groupby('Fecha')['Produccion'].sum()
        fig_total=px.line(results,x=date.unique(),y=co2_total/prod_diaria,markers=True,line_shape='spline')
        fig_total.update_layout(xaxis_title='Fecha',yaxis_title='kg CO2-eq / '+unit)
        st.plotly_chart(fig_total, use_container_width=True,config=config)

    with tab2:
        energy_int_total=results.groupby('Fecha')['Contenido energia MJ'].sum()
        fig_total=px.line(results,x=date.unique(),y=energy_int_total/prod_diaria,markers=True,line_shape='spline')
        fig_total.update_layout(xaxis_title='Fecha',yaxis_title='MJ / '+unit)
        st.plotly_chart(fig_total, use_container_width=True,config=config)

with st.expander('Contribución emisiones de carbono',expanded=True):

    tab1, tab2, tab3 = st.tabs(["Fuentes de energia", "Equipos", "Procesos"])

    with tab1:
        fig_results = px.pie(results, names='Fuente energia', values='Emisiones kg CO2-eq', hole=0.4)
        st.plotly_chart(fig_results, use_container_width=True,config=config)

        #fig_results_time=px.bar(results,x=date.unique(),y=co2_total,color=results['Fuente energia'].unique())
        #st.plotly_chart(fig_results_time,use_container_width=True)

    with tab2:
        fig_equipment = px.pie(results, names='ID equipo', values='Emisiones kg CO2-eq', hole=0.4)
        st.plotly_chart(fig_equipment, use_container_width=True,config=config)

    with tab3:
        fig_process = px.pie(results, names='ID proceso', values='Emisiones kg CO2-eq', hole=0.4)
        st.plotly_chart(fig_process, use_container_width=True,config=config)

with st.expander('Contribución costos de energia',expanded=True):

    tab1, tab2, tab3 = st.tabs(["Fuentes de energia", "Equipos", "Procesos"])

    with tab1:
        fig_results = px.pie(results, names='Fuente energia', values='Costo energia USD', hole=0.4)
        st.plotly_chart(fig_results, use_container_width=True,config=config)

    with tab2:
        fig_equipment = px.pie(results, names='ID equipo', values='Costo energia USD', hole=0.4)
        st.plotly_chart(fig_equipment, use_container_width=True,config=config)

    with tab3:
        fig_process = px.pie(results, names='ID proceso', values='Costo energia USD', hole=0.4)
        st.plotly_chart(fig_process, use_container_width=True,config=config)

with st.expander("Prediccion emisiones y costos",expanded=True):
    #To try Prophet model:
    #https://towardsdatascience.com/deploying-a-prophet-forecasting-model-with-streamlit-to-heroku-caf1729bd917
    #https://github.com/edkrueger/covid-forecast/blob/master/app/app.py

    data_emisiones=results_time.drop(['Costo energia USD','Fecha'],axis=1)
    data_costos=results_time.drop(['Emisiones kg CO2-eq','Fecha'],axis=1)

    #Estos parametros se los debe optimizar. Los que estan aqui no son los optimos
    order=(5,1,20)

    def fit_arima(data,order):
        model=ARIMA(data, order=order)
        model_fit=model.fit()
        forecast=model_fit.forecast(steps=15)
        return forecast

    tab1, tab2=st.tabs(['Prediccion Emisiones','Prediccion Costos'])

    with tab1:
        forecast_emisiones=fit_arima(data_emisiones,order)
        results_pred_emisiones=pd.concat([data_emisiones,forecast_emisiones], axis=1)
        fig_emisiones=px.line(results_pred_emisiones, y=["Emisiones kg CO2-eq","predicted_mean"],markers=True,line_shape='spline')
        st.plotly_chart(fig_emisiones,use_container_width=True,config=config)

    with tab2:
        forecast_costos=fit_arima(data_costos,order)
        results_pred_costos=pd.concat([data_costos,forecast_costos], axis=1)
        fig_costos=px.line(results_pred_costos, y=['Costo energia USD',"predicted_mean"],markers=True,line_shape='spline')
        st.plotly_chart(fig_costos,use_container_width=True,config=config)

with st.expander("Optimizar emisiones y costos",expanded=True):

    co2_reduced=emissions_total*0.1
    co2_new=emissions_total*0.9
    #Se asume que un árbol almacena unos 167 kg de CO2 al año https://climate.selectra.com/es/actualidad/co2-arbol
    arboles=co2_reduced/167

    cost_reduced=cost_total*0.1
    cost_new=cost_total*0.9

    tab1, tab2=st.tabs(['Emisiones','Costos'])

    with tab1:
        col1,col2=st.columns(2)

        with col1:
            st.metric('Emisiones actuales',str("%.1f" % np.float_(emissions_total))+ ' kg CO2-eq')

        with col2:
            st.metric('Emisiones optimizadas',str("%.1f" % np.float_(co2_new))+ ' kg CO2-eq',delta=str("%.1f" % np.float_(-co2_reduced))+ ' kg CO2-eq', delta_color='inverse')

        st.write('Tu reducción de emisiones equivalen a que siembres',str("%.1f" % np.float_(arboles))+ ' arboles 🌳')

    with tab2:
        col1,col2=st.columns(2)

        with col1:
            st.metric('Costos actuales',str("%.1f" % np.float_(cost_total))+ ' USD')

        with col2:
            st.metric('Costos optimizados',str("%.1f" % np.float_(cost_new))+ ' USD',delta=str("%.1f" % np.float_(-cost_reduced))+ ' USD', delta_color='inverse' )

with st.expander('Personalized Advice',expanded=True):

    emissions_total=np.sum(results['Emisiones kg CO2-eq'])
    cost_total=np.sum(results['Costo energia USD'])
    energy_total=np.sum(results['Contenido energia MJ'])
    prod_total=np.sum(df_prod_mod['Produccion'])

    import streamlit as st
    from langchain.llms import OpenAI
    openai_api_key = st.text_input('OpenAI API Key')

    def generate_response(input_text):
        llm = OpenAI(temperature=0.7, openai_api_key=openai_api_key)
        st.info(llm(input_text))

    if not openai_api_key.startswith('sk-'):
        st.warning('Please enter your OpenAI API key!', icon='⚠')
    if submitted and openai_api_key.startswith('sk-'):
        generate_response(text)

    st.success(""" 
    Felicitaciones, has reducido tus emisiones de carbono y los costos energeticos y ahora tu planta es mas rentable y eficiente!
    
    Contáctanos si quieres acceder al Plan Pro para que modelemos tu empresa, ingresando tus procesos, equipos y fuentes de energía, para así obtener el desempeño de tu planta y optimizar tus operaciones.""")
