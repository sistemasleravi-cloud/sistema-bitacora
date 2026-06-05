import streamlit as st
import time
from streamlit_cookies_controller import CookieController

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
    cookie_controller = CookieController()
        
    cookie_auth = cookie_controller.get('auth_leravi')

    if cookie_auth == 'autenticado':
        st.session_state['logged'] = True
    elif 'logged' not in st.session_state:
        st.session_state['logged'] = False

    if not st.session_state['logged']:
        login_screen()
    else:
        admin_panel()
else:
    st.error("Error de conexion a la base de datos.")
