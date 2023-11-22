import streamlit as st

st.set_page_config(layout="wide",page_title="AUCA",page_icon="🌿")

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

st.markdown("# Contacto")

st.write("### En esta ocasión, te hemos presentado una demostracion del módulo de Cálculos de AUCA. Sin embargo, quedan inmensas oportunidades para disminuir tus emisiones y costos energéticos al usar la version PRO.")

st.write("### Si quieres conocer como puedes lograr estos beneficios, agenda una cita en nuestra página web (https://pungoapp.com/) para guiarte en el proceso y recibir asesoria de nuestros expertos.")

# contact_form = """
# <form action="https://formsubmit.co/zapaz.consultores@gmail.com" method="POST">
#      <input type="hidden" name="_captcha" value="false">
#      <input type="text" name="Nombre" placeholder="Tu nombre" required>
#      <input type="email" name="email" placeholder="Tu email" required>
#      <textarea name="message" placeholder="Tu mensaje"></textarea>
#      <button type="submit">Send</button>
# </form>
# """
#
# st.markdown(contact_form, unsafe_allow_html=True)
#
# # Use Local CSS File
# def local_css(file_name):
#     with open(file_name) as f:
#         st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


#local_css("style.css")
