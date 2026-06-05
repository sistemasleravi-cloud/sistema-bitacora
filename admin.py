import streamlit as st
import os
import base64
from config import FB, FH, BLA, R
from utils import now_az
import views
import almacen
from db import db_query
from streamlit_autorefresh import st_autorefresh
from streamlit_cookies_controller import CookieController

def admin_panel():
    ruta_script = os.path.dirname(os.path.abspath(__file__))
    rutas_posibles = [
        os.path.join(ruta_script, "logoLeravi.jpeg"),
        os.path.join(ruta_script, "..", "logoLeravi.jpeg"),
        "/app/logoLeravi.jpeg"
    ]

    logo_encontrado = None
    for ruta in rutas_posibles:
        if os.path.exists(ruta):
            logo_encontrado = ruta
            break

    marca_html = ""
    if logo_encontrado:
        try:
            with open(logo_encontrado, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode()
                marca_html += f"""<div style="text-align: center; padding: 1.5rem 1rem 0.5rem 1rem;">
<img src="data:image/jpeg;base64,{encoded_string}" width="120" style="border-radius: 8px; border: 1px solid #2A2A2A; margin-bottom: 0.8rem;">
<p style="font-family:{FH};font-size:1.45rem;color:{BLA};letter-spacing:0.12em;margin:0;line-height:1;">LERAVI</p>
<p style="font-family:{FB};font-size:0.58rem;color:#3A3A3A;letter-spacing:0.18em;text-transform:uppercase;margin:0.2rem 0 0 0;font-weight:500;">Control Administrativo</p>
</div>
<div style="padding: 0 1.4rem;"><hr style="border: none; border-top: 1px solid #1A1A1A; margin: 0;"></div>"""
        except Exception as e:
            marca_html += f'<div style="text-align:center; padding:1.5rem;"><p style="color:red;font-size:0.8rem;">Error: {str(e)}</p></div>'
    else:
        marca_html += f'<div style="text-align:center; padding:1.5rem;"><p style="color:var(--gris);font-size:0.8rem;font-style:italic;">Logo no disponible</p></div>'

    st.sidebar.markdown(marca_html, unsafe_allow_html=True)

    st.sidebar.markdown(f"""
        <p style="font-family:{FB};font-size:0.58rem;font-weight:700;letter-spacing:0.18em;
                  text-transform:uppercase;color:#333;margin:1.2rem 1.4rem 0.5rem 1.4rem;">
            Navegacion
        </p>
    """, unsafe_allow_html=True)

    nav_labels = [
        "Dashboard",
        "Almacen General",
        "Alta de Trabajador",
        "Alta de Maquina",
        "Asignar Tarea",
        "Editar Avances",
        "Bitacora",
        "Eliminar Registro",
    ]
    nav_keys = [
        "Dashboard",
        "Almacen",
        "Alta de Trabajador",
        "Alta de Maquina",
        "Asignar Tarea",
        "Editar Avances",
        "Bitacora",
        "Eliminar",
    ]

    # --- AQUÍ ESTÁ LA LÍNEA CORREGIDA ---
    sel_label = st.sidebar.radio("Navegacion Principal", nav_labels, label_visibility="collapsed")
    menu = nav_keys[nav_labels.index(sel_label)]

    st.sidebar.markdown("<div style='flex:1;min-height:3rem;'></div>", unsafe_allow_html=True)

    st.sidebar.markdown(f"""
        <div style="border-top:1px solid #1A1A1A;padding:1.2rem 1.4rem 0.8rem 1.4rem;">
            <div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:1rem;">
                <div style="width:32px;height:32px;border-radius:50%;background:{R};
                            display:flex;align-items:center;justify-content:center;flex-shrink:0;">
                    <span style="font-family:{FB};font-size:0.78rem;font-weight:700;color:{BLA};">A</span>
                </div>
                <div>
                    <p style="font-family:{FB};font-size:0.8rem;font-weight:600;color:{BLA};margin:0;">Admin</p>
                    <p style="font-family:{FB};font-size:0.62rem;color:#444;margin:0;">
                        {now_az().strftime('%d %b %Y')}
                    </p>
                    <p style="font-family:{FB};font-size:0.8rem;font-weight:600;color:{BLA};margin:0;">Version: 2.1.1</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if st.sidebar.button("Cerrar Sesion", use_container_width=True):
        cookie_controller = CookieController()
        cookie_controller.remove('auth_leravi')
        st.session_state['logged'] = False
        st.rerun()

    # --- RUTAS DE NAVEGACION ---
    if menu == "Dashboard":
        st_autorefresh(interval=5000, limit=None, key="autorefresh_dashboard")
        views.render_dashboard()
    elif menu == "Almacen":
        almacen.render_almacen(db_query, es_publico=False)
    elif menu == "Alta de Trabajador":
        views.render_alta_trabajador()
    elif menu == "Alta de Maquina":
        views.render_alta_maquina()
    elif menu == "Asignar Tarea":
        views.render_asignar_tarea()
    elif menu == "Editar Avances":
        views.render_editar_avances()
    elif menu == "Bitacora":
        views.render_bitacora()
    elif menu == "Eliminar":
        views.render_eliminar_registro()
