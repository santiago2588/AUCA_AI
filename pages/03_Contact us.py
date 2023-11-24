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
image = Image.open('Resources/AUCA.png')
st.image(image)

st.markdown("# Contact us")

st.write("### On this occasion, we have shown you a demo of AUCA. However, there remain immense opportunities to reduce your emissions and energy costs by using the PRO version.")


st.write("### If you want to know how you can achieve these benefits, schedule an appointment to guide you through the process and receive advice from our experts.")

st.link_button(label='Schedule an appointment',url='https://calendly.com/pungo_szapata/meeting')

contact_form = """
<form action="https://formsubmit.co/zapaz.consultores@gmail.com" method="POST">
     <input type="hidden" name="_captcha" value="false">
     <input type="text" name="Name" placeholder="Your name" required>
     <input type="email" name="email" placeholder="Your email" required>
     <textarea name="Message" placeholder="Your message"></textarea>
     <button type="submit">Send</button>
</form>
"""

st.markdown(contact_form, unsafe_allow_html=True)

# Use Local CSS File
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


local_css("style.css")
