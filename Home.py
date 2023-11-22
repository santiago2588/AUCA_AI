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
image = Image.open('Resources/logo_Pungo.png')
st.image(image)

st.write("# DIGITALIZATION WITH POSITIVE IMPACTS)
st.write("### Welcome to AUCA: la herramienta digital para la gestión de la energía y las emisiones de carbono en la industria")
