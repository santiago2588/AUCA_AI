import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA

#Base de datos que se procesa
url="https://docs.google.com/spreadsheets/d/1fd_KYRl09ZFb23HBXLN8sIxEvmnuMhotgBDTRYqCBAk/edit?usp=sharing"

# Create a connection object.
conn = st.connection("gsheets", type=GSheetsConnection)

#Cargar base de datos fuentes de energia
df=conn.read(spreadsheet=url, worksheet='1910628376', ttl="1m")

df_equip = conn.read(spreadsheet=url,worksheet="1279293948",ttl="1m")
df_equip['date'] = pd.to_datetime(df_equip['date'], format='%d/%m/%Y')
df_equip['date'] = df_equip['date'].dt.date

df_equip=df_equip.sort_values(['date','energy_source'],ascending=[True,True])
df_equip_mod=df_equip.rename(columns={'date':'Date','id_process':'ID process','id_equipment':'ID equipment','energy_source':'Energy source','consumption':'Consumption','consumption_unit':'Unit'})

df_prod=conn.read(spreadsheet=url,worksheet="929766433",ttl="1m")
df_prod['date'] = pd.to_datetime(df_prod['date'],format='%d/%m/%Y')
df_prod['date']=df_prod['date'].dt.date
#df_prod=df_prod.sort_values(['date'],ascending=[True])

df_prod_mod=df_prod.rename(columns={'date':'Date','production':'Production','unit':'Unit'})
unit=df_prod_mod._get_value(1,'Unit')

#Obtener listado de procesos, equipos, combustibles, y consumos
process_list=df_equip['id_process'].tolist()
equipment_list=df_equip['id_equipment'].tolist()
fuel_list=df_equip['energy_source'].tolist()
consumption_list=df_equip['consumption'].tolist()

#Dataframes para guardar los resultados
df0=[]
df1=[]
df2=[]
df3=[]
df4=[]

#Calculo de las emisiones de carbono
def emission(fuel,consumption):
    fuel_name=df.loc[df["energy_source"] == i,'energy_source']
    heat_content = df.loc[df["energy_source"]==i,'calorific_value']
    emission_factor = df.loc[df["energy_source"]==i,'emission_factor']
    fuel_cost = df.loc[df["energy_source"]==i,'cost_unit']
    fuel_calor = df.loc[df["energy_source"]==i,'energy_content']
    scope = df.loc[df["energy_source"]==i,'emission_scope']
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

date=df_equip_mod['Date']
date=pd.to_datetime(date)
date=date.dt.date
process_name=pd.DataFrame(process_list)
process_name.columns=['ID process']
equipment_name=pd.DataFrame(equipment_list)
equipment_name.columns=['ID equipment']
fuel_name=pd.DataFrame(df0)
fuel_name.columns=['Energy source']
co2=pd.DataFrame(df1)
co2.columns=['Emissions kg CO2-eq']
scope=pd.DataFrame(df2)
scope.columns=['Emission Scope']
cost=pd.DataFrame(df3)
cost.columns=['Energy costs USD']
fuel_energy=pd.DataFrame(df4)
fuel_energy.columns=['Energy content MJ']

results=pd.concat([date,process_name,equipment_name,fuel_name,co2,scope,cost,fuel_energy],axis='columns')
#results.set_index('ID proceso',inplace=True)

#Resultados totales
emissions_total=np.sum(results['Emissions kg CO2-eq'])
cost_total=np.sum(results['Energy costs USD'])
energy_total=np.sum(results['Energy content MJ'])
prod_total=np.sum(df_prod_mod['Production'])

#Resultados por tiempo
co2_total_time=results.groupby('Date')['Emissions kg CO2-eq'].sum()
costo_total_time=results.groupby('Date')['Energy costs USD'].sum()

results_time=pd.concat([co2_total_time,costo_total_time],axis=1)
results_time['Date']=results_time.index

co2_total=results.groupby('Date')['Emissions kg CO2-eq'].sum()
prod_diaria=df_prod_mod.groupby('Date')['Production'].sum()

energy_int_total=results.groupby('Date')['Energy content MJ'].sum()

#Hotspot identification
process_hotspot_co2=results.groupby('ID process')['Emissions kg CO2-eq'].sum().idxmax()
process_hotspot_cost=results.groupby('ID process')['Energy costs USD'].sum().idxmax()
process_hotspot_energy=results.groupby('ID process')['Energy content MJ'].sum().idxmax()

equipment_hotspot_co2=results.groupby('ID equipment')['Emissions kg CO2-eq'].sum().idxmax()
equipment_hotspot_cost=results.groupby('ID equipment')['Energy costs USD'].sum().idxmax()
equipment_hotspot_energy=results.groupby('ID equipment')['Energy content MJ'].sum().idxmax()

fuel_hotspot_co2=results.groupby('Energy source')['Emissions kg CO2-eq'].sum().idxmax()
fuel_hotspot_cost=results.groupby('Energy source')['Energy costs USD'].sum().idxmax()
fuel_hotspot_energy=results.groupby('Energy source')['Energy content MJ'].sum().idxmax()

#Prediction model

#To try Prophet model:
#https://towardsdatascience.com/deploying-a-prophet-forecasting-model-with-streamlit-to-heroku-caf1729bd917
#https://github.com/edkrueger/covid-forecast/blob/master/app/app.py

data_emisiones=results_time.drop(['Energy costs USD','Date'],axis=1)
data_costos=results_time.drop(['Emissions kg CO2-eq','Date'],axis=1)

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
