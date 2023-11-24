import plotly.express as px
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
st.link_button(label='Access the database',url=url)

st.markdown("## Results")

with st.expander("Total costs and emissions",expanded=True):

    col1,col2=st.columns(2)

    with col1:
        st.metric('Total emissions',str("%.1f" % np.float_(emissions_total))+ ' kg CO2-eq')

    with col2:
        st.metric('Total energy costs',str("%.1f" % np.float_(cost_total))+ ' USD')

    tab1,tab2=st.tabs(['Total emissions','Total costs'])

    #Ocultar toolbar de plotly
    config = {'displayModeBar': False}

    with tab1:
        fig_total=px.line(results,x=date.unique(),y=co2_total_time,markers=True,line_shape='spline')
        fig_total.update_layout(xaxis_title='Date',yaxis_title='kg CO2')
        st.plotly_chart(fig_total, use_container_width=True,config=config)

    with tab2:
        fig_total=px.line(results,x=date.unique(),y=costo_total_time,markers=True,line_shape='spline')
        fig_total.update_layout(xaxis_title='Date',yaxis_title='USD')
        st.plotly_chart(fig_total, use_container_width=True,config=config)

    st.markdown('Detailed results')
    st.dataframe(results)

    #Descargar csv de los resultados
    def convert_df(df):
        return df.to_csv().encode('utf-8')

    csv_results = convert_df(results)
    st.download_button("📥Press to Download", csv_results, "results.csv", "text/csv", key='download-csv')

with st.expander('Indicators por production unit',expanded=True):
    col1,col2=st.columns(2)
    with col1:
        st.metric('Average CO2 emissions',str("%.1f" % np.float_(emissions_total/prod_total))+ ' kg CO2-eq / '+unit)

    with col2:
        st.metric('Average energy intensity',str("%.1f" % np.float_(energy_total/prod_total))+ ' MJ / '+unit)

    tab1,tab2=st.tabs(['CO2 emissions','Energy intensity'])

    with tab1:

        fig_total=px.line(results,x=date.unique(),y=co2_total/prod_diaria,markers=True,line_shape='spline')
        fig_total.update_layout(xaxis_title='Date',yaxis_title='kg CO2-eq / '+unit)
        st.plotly_chart(fig_total, use_container_width=True,config=config)

    with tab2:

        fig_total=px.line(results,x=date.unique(),y=energy_int_total/prod_diaria,markers=True,line_shape='spline')
        fig_total.update_layout(xaxis_title='Date',yaxis_title='MJ / '+unit)
        st.plotly_chart(fig_total, use_container_width=True,config=config)

with st.expander('Hotspot analysis: CO2 emissions',expanded=True):

    st.markdown(f'- Process hotspot: {process_hotspot_co2}')
    st.markdown(f'- Equipment hotspot: {equipment_hotspot_co2}')
    st.markdown(f'- Energy source hotspot: {fuel_hotspot_co2}')

    tab1, tab2, tab3 = st.tabs(["Energy source", "Equipment", "Process"])

    with tab1:
        fig_results = px.pie(results, names='Energy source', values='Emissions kg CO2-eq', hole=0.4)
        st.plotly_chart(fig_results, use_container_width=True,config=config)

        #fig_results_time=px.bar(results,x=date.unique(),y=co2_total,color=results['Fuente energia'].unique())
        #st.plotly_chart(fig_results_time,use_container_width=True)

    with tab2:
        fig_equipment = px.pie(results, names='ID equipment', values='Emissions kg CO2-eq', hole=0.4)
        st.plotly_chart(fig_equipment, use_container_width=True,config=config)

    with tab3:
        fig_process = px.pie(results, names='ID process', values='Emissions kg CO2-eq', hole=0.4)
        st.plotly_chart(fig_process, use_container_width=True,config=config)

with st.expander('Hotspot analysis: Energy costs',expanded=True):

    st.markdown(f'- Process hotspot: {process_hotspot_cost}')
    st.markdown(f'- Equipment hotspot: {equipment_hotspot_cost}')
    st.markdown(f'- Energy source hotspot: {fuel_hotspot_cost}')

    tab1, tab2, tab3 = st.tabs(["Energy source", "Equipment", "Process"])

    with tab1:
        fig_results = px.pie(results, names='Energy source', values='Energy costs USD', hole=0.4)
        st.plotly_chart(fig_results, use_container_width=True,config=config)

    with tab2:
        fig_equipment = px.pie(results, names='ID equipment', values='Energy costs USD', hole=0.4)
        st.plotly_chart(fig_equipment, use_container_width=True,config=config)

    with tab3:
        fig_process = px.pie(results, names='ID process', values='Energy costs USD', hole=0.4)
        st.plotly_chart(fig_process, use_container_width=True,config=config)

with st.expander("Prediction of CO2 emissions and energy costs",expanded=True):

    tab1, tab2=st.tabs(['Emissions prediction','Costs prediction'])

    with tab1:

        fig_emisiones=px.line(results_pred_emisiones, y=["Emissions kg CO2-eq","predicted_mean"],markers=True,line_shape='spline')
        st.plotly_chart(fig_emisiones,use_container_width=True,config=config)

    with tab2:

        fig_costos=px.line(results_pred_costos, y=['Energy costs USD',"predicted_mean"],markers=True,line_shape='spline')
        st.plotly_chart(fig_costos,use_container_width=True,config=config)

with st.expander("CO2 emissions and energy costs optimization",expanded=True):

    tab1, tab2=st.tabs(['CO2 emissions','Costs'])

    with tab1:
        col1,col2=st.columns(2)

        with col1:
            st.metric('Baseline emissions',str("%.1f" % np.float_(emissions_total))+ ' kg CO2-eq')

        with col2:
            st.metric('Optimized emissions',str("%.1f" % np.float_(co2_new))+ ' kg CO2-eq',delta=str("%.1f" % np.float_(-co2_reduced))+ ' kg CO2-eq', delta_color='inverse')

        st.write('The reduction in CO2 emissions is equivalent to plant ',str("%.1f" % np.float_(arboles))+ ' trees 🌳')

    with tab2:
        col1,col2=st.columns(2)

        with col1:
            st.metric('Baseline energy costs',str("%.1f" % np.float_(cost_total))+ ' USD')

        with col2:
            st.metric('Optimized energy costs',str("%.1f" % np.float_(cost_new))+ ' USD',delta=str("%.1f" % np.float_(-cost_reduced))+ ' USD', delta_color='inverse' )

