# -*- coding: utf-8 -*-
"""
Created on Sun Aug 14 18:19:54 2022

@author: mjkipsz2
"""

import streamlit as st

st.set_page_config(layout="wide",page_title="AUCA",page_icon="🌿",initial_sidebar_state="expanded")

#Codigo para eliminar el boton de menu y logo de streamlit
hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden; }
        footer {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

from PIL import Image
image = Image.open('Resources/AUCA.png')
st.image(image)

st.write("# The net-zero copilot for industrial SMEs")

st.markdown("""
    ### AUCA is a digital tool that allows you to calculate the carbon footprint (Scopes 1 and 2) in industrial operations, and the associated energy costs.""")

image1 = Image.open('Resources/emissions scope.jpg')
st.image(image1)

st.markdown('This tool also allows you to reduce your carbon emissions and energy costs based on the results obtained in the model\
                  generating economic benefits. To do this, the tool uses predictions based on artificial intelligence and methodologies for process integration and energy efficiency.')
