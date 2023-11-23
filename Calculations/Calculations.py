import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA

#Base de datos que se procesa
url="https://docs.google.com/spreadsheets/d/1FB-lPd8usv_XpFNSm0t4W6C7ogdcHIO1FuJZ2Dmvm_4/edit?usp=sharing"

# Create a connection object.
conn = st.connection("gsheets", type=GSheetsConnection)

#Cargar base de datos fuentes de energia
df=conn.read(spreadsheet=url, worksheet='1930401626', ttl="1m")

df_equip = conn.read(spreadsheet=url,worksheet="324598336",ttl="1m")

df_equip['fecha'] = pd.to_datetime(df_equip['fecha'])

df_equip=df_equip.sort_values(['fecha','fuente_energia'],ascending=[True,True])
df_equip_mod=df_equip.rename(columns={'fecha':'Fecha','id_proceso':'ID proceso','id_equipo':'ID equipo','fuente_energia':'Fuente energia','consumo':'Consumo','unidad_consumo':'Unidad'})

df_prod=conn.read(spreadsheet=url,worksheet="1391049495",ttl="1m")
df_prod['fecha'] = pd.to_datetime(df_prod['fecha'])
#df_prod=df_prod.sort_values(['fecha'],ascending=[True])

df_prod_mod=df_prod.rename(columns={'fecha':'Fecha','produccion':'Produccion','unidad':'Unidad'})
unit=df_prod_mod._get_value(1,'Unidad')

#Obtener listado de procesos, equipos, combustibles, y consumos
process_list=df_equip['id_proceso'].tolist()
equipment_list=df_equip['id_equipo'].tolist()
fuel_list=df_equip['fuente_energia'].tolist()
consumption_list=df_equip['consumo'].tolist()

#Dataframes para guardar los resultados
df0=[]
df1=[]
df2=[]
df3=[]
df4=[]

#Calculo de las emisiones de carbono
def emission(fuel,consumption):
    fuel_name=df.loc[df["fuente_energia"] == i,'fuente_energia']
    heat_content = df.loc[df["fuente_energia"]==i,'valor_calorifico']
    emission_factor = df.loc[df["fuente_energia"]==i,'factor_emision']
    fuel_cost = df.loc[df["fuente_energia"]==i,'costo_unitario']
    fuel_calor = df.loc[df["fuente_energia"]==i,'contenido_energia']
    scope = df.loc[df["fuente_energia"]==i,'alcance_emisiones']
    co2=j*heat_content*emission_factor
    cost=j*fuel_cost
    energy=j*fuel_calor
    return fuel_name,scope,co2,cost,energy


#Prueba de la funcion
for i,j in zip(fuel_list,consumption_list):
    fuel_name,scope,co2,cost,energy=emission(fuel_list,consumption_list)
    df0.extend(fuel_name)
    df1.extend(co2)
    df2.extend(scope)
    df3.extend(cost)
    df4.extend(energy)

date=df_equip_mod['Fecha']
date=pd.to_datetime(date)
process_name=pd.DataFrame(process_list)
process_name.columns=['ID proceso']
equipment_name=pd.DataFrame(equipment_list)
equipment_name.columns=['ID equipo']
fuel_name=pd.DataFrame(df0)
fuel_name.columns=['Fuente energia']
co2=pd.DataFrame(df1)
co2.columns=['Emisiones kg CO2-eq']
scope=pd.DataFrame(df2)
scope.columns=['Alcance emisiones']
cost=pd.DataFrame(df3)
cost.columns=['Costo energia USD']
fuel_energy=pd.DataFrame(df4)
fuel_energy.columns=['Contenido energia MJ']

results=pd.concat([date,process_name,equipment_name,fuel_name,co2,scope,cost,fuel_energy],axis='columns')
#results.set_index('ID proceso',inplace=True)

#Resultados totales
emissions_total=np.sum(results['Emisiones kg CO2-eq'])
cost_total=np.sum(results['Costo energia USD'])
energy_total=np.sum(results['Contenido energia MJ'])
prod_total=np.sum(df_prod_mod['Produccion'])

#Resultados por tiempo
co2_total_time=results.groupby('Fecha')['Emisiones kg CO2-eq'].sum()
costo_total_time=results.groupby('Fecha')['Costo energia USD'].sum()

results_time=pd.concat([co2_total_time,costo_total_time],axis=1)
results_time['Fecha']=results_time.index

co2_total=results.groupby('Fecha')['Emisiones kg CO2-eq'].sum()
prod_diaria=df_prod_mod.groupby('Fecha')['Produccion'].sum()

energy_int_total=results.groupby('Fecha')['Contenido energia MJ'].sum()

#Hotspot identification
process_hotspot_co2=results.groupby('ID proceso')['Emisiones kg CO2-eq'].sum().idxmax()
process_hotspot_cost=results.groupby('ID proceso')['Costo energia USD'].sum().idxmax()
process_hotspot_energy=results.groupby('ID proceso')['Contenido energia MJ'].sum().idxmax()

#results_process_filtered = results[results['ID proceso'] == process_hotspot_co2]

#results_process=pd.concat([co2_total_process,costo_total_process,energy_total_process],axis=1)
#process_hotspot_co2=(results.loc[results['Emisiones kg CO2-eq'].idxmax(),'ID proceso']
#process_hotspot_costo=results_process.loc[results_process['Costo energia USD'].idxmax(),'ID proceso']
#process_hotspot_energy=results_process.loc[results_process['Contenido energia MJ'].idxmax(),'ID proceso']

#Prediction model
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

forecast_emisiones=fit_arima(data_emisiones,order)
results_pred_emisiones=pd.concat([data_emisiones,forecast_emisiones], axis=1)

forecast_costos=fit_arima(data_costos,order)
results_pred_costos=pd.concat([data_costos,forecast_costos], axis=1)

#Optimizacion emisiones y costos
co2_reduced=emissions_total*0.1
co2_new=emissions_total*0.9
#Se asume que un árbol almacena unos 167 kg de CO2 al año https://climate.selectra.com/es/actualidad/co2-arbol
arboles=co2_reduced/167

cost_reduced=cost_total*0.1
cost_new=cost_total*0.9
