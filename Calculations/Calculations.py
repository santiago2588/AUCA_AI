import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import numpy as np

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

# st.markdown("## Datos ingresados")
# tab1,tab2=st.tabs(['Consumos de energía','Producción de la planta'])
# with tab1:
#     st.dataframe(df_equip_mod)
# with tab2:
#     st.dataframe(df_prod_mod)

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
#@st.cache_data
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