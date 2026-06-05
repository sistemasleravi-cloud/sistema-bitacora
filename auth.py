import streamlit as st
import os
import base64
from config import FB, FH, BLA, NEG, R
from utils import now_az
from db import db_query, check_password
from streamlit_cookies_controller import CookieController # <-- 1. IMPORTACION AGREGADA

def login_screen():
    ruta_script = os.path.dirname(os.path.abspath(__file__))
    rutas_posibles = [
        os.path.join(ruta_script, "logoLeravi.jpeg"),
        os.path.join(ruta_script, "..", "logoLeravi.jpeg"),
        "/app/logoLeravi.jpeg",
        "logoLeravi.jpeg"
    ]

    logo_encontrado = None
    for ruta in rutas_posibles:
        if os.path.exists(ruta):
            logo_encontrado = ruta
            break

    img_html = ""
    if logo_encontrado:
        try:
            with open(logo_encontrado, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode()
                img_html = f'<img src="data:image/jpeg;base64,{encoded_string}" width="110" style="border-radius: 8px; margin: 1.5rem auto; display: block; border: 1px solid #222; box-shadow: 0 4px 15px rgba(0,0,0,0.5);">'
        except Exception:
            pass
    if not img_html:
        img_html = f'<div style="width:36px;height:2px;background:{R};margin:1rem auto;border-radius:1px;"></div>'

    st.markdown(f"""
        <style>
            .stApp {{ background: {NEG} !important; }}
            .block-container {{ max-width: 440px !important; margin: 0 auto !important; padding-top: 9vh !important; }}
            .stTextInput > div > div > input {{
                background: #1A1A1A !important; color: {BLA} !important; border-color: #2E2E2E !important;
            }}
            .stTextInput > div > div > input:focus {{ background: #222 !important; border-color: {R} !important; }}
            .stTextInput label {{ color: #666 !important; }}
            [data-testid="stForm"] {{
                background: #111 !important; border: 1px solid #222 !important;
                border-radius: 12px !important; padding: 2.5rem !important;
                box-shadow: 0 24px 64px rgba(0,0,0,0.6) !important;
            }}
        </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""<div style="text-align:center;margin-bottom:3rem;">
<p style="font-family:{FB};font-size:0.62rem;font-weight:700;letter-spacing:0.32em;text-transform:uppercase;color:{R};margin:0 0 0.5rem 0;">GRUPO CONSTRUCTOR</p>
<p style="font-family:{FH};font-size:4.2rem;color:{BLA};margin:0;line-height:1;letter-spacing:0.08em;">LERAVI</p>
{img_html}
<p style="font-family:{FB};font-size:0.72rem;color:#444;margin:0;letter-spacing:0.18em;text-transform:uppercase;font-weight:500;">Sistema de Control Administrativo</p>
</div>""", unsafe_allow_html=True)

    with st.form("login_form"):
        st.markdown(f"""<p style="font-family:{FB};font-size:0.65rem;font-weight:600;letter-spacing:0.18em;text-transform:uppercase;color:#444;text-align:center;margin:0 0 1.8rem 0;">Acceso al sistema</p>""", unsafe_allow_html=True)
        usuario = st.text_input("Usuario", placeholder="Nombre de usuario")
        clave   = st.text_input("Contrasena", type="password", placeholder="Contrasena")
        st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
        if st.form_submit_button("INGRESAR", use_container_width=True):
            res = db_query("SELECT * FROM usuarios WHERE usuario=%s", (usuario,), fetch=True)
            if res and check_password(clave, res[0]['password_hash']):
                
                # --- 2. AQUI GUARDAMOS LA COOKIE EN LA COMPU DEL USUARIO ---
                cookie_controller = CookieController()
                cookie_controller.set('auth_leravi', 'autenticado', max_age=2592000) # Dura 30 días (en segundos)
                
                st.session_state['logged'] = True
                st.rerun()
            else:
                st.error("Usuario o contrasena incorrectos.")

    st.markdown(f"""<p style="text-align:center;font-family:{FB};font-size:0.62rem;color:#2A2A2A;margin-top:2rem;">&copy; {now_az().year} Grupo Constructor Leravi</p>""", unsafe_allow_html=True)
