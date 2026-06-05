import streamlit as st

st.set_page_config(
    page_title="Control Administrativo · Leravi",
    layout="wide",
    page_icon="",
    initial_sidebar_state="expanded"
)

from config import load_css
from db import conn
from auth import login_screen
from admin import admin_panel

load_css()

if conn:
    if 'logged' not in st.session_state:
        st.session_state['logged'] = False
    if not st.session_state['logged']:
        login_screen()
    else:
        admin_panel()
else:
    st.error("No se pudo conectar a la base de datos. Verifica las credenciales o el estado del servidor MySQL.")
