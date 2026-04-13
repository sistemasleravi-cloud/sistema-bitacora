import streamlit as st
import pandas as pd
import mysql.connector
import bcrypt
from datetime import datetime
import time
import plotly.graph_objects as go
import os
import html

st.set_page_config(page_title="Control Administrativo", layout="wide", page_icon="")

def load_css(file_name):
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("style.css")

@st.cache_resource
def init_connection():
    retries = 15
    while retries > 0:
        try:
            conn = mysql.connector.connect(
                host=st.secrets["mysql"]["host"],
                port=st.secrets["mysql"]["port"],
                user=st.secrets["mysql"]["user"],
                password=st.secrets["mysql"]["password"]
            )
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {st.secrets['mysql']['database']}")
            cursor.execute(f"USE {st.secrets['mysql']['database']}")

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bitacora (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(100) NOT NULL,
                    fecha DATE NOT NULL,
                    tarea_1 VARCHAR(255) DEFAULT '-', avance_1 INT DEFAULT 0, fecha_inicio_1 DATE DEFAULT NULL, maquina_1 VARCHAR(255) DEFAULT '-',
                    tarea_2 VARCHAR(255) DEFAULT '-', avance_2 INT DEFAULT 0, fecha_inicio_2 DATE DEFAULT NULL, maquina_2 VARCHAR(255) DEFAULT '-',
                    tarea_3 VARCHAR(255) DEFAULT '-', avance_3 INT DEFAULT 0, fecha_inicio_3 DATE DEFAULT NULL, maquina_3 VARCHAR(255) DEFAULT '-',
                    tarea_4 VARCHAR(255) DEFAULT '-', avance_4 INT DEFAULT 0, fecha_inicio_4 DATE DEFAULT NULL, maquina_4 VARCHAR(255) DEFAULT '-',
                    tarea_5 VARCHAR(255) DEFAULT '-', avance_5 INT DEFAULT 0, fecha_inicio_5 DATE DEFAULT NULL, maquina_5 VARCHAR(255) DEFAULT '-'
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bitacora_completados (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(100) NOT NULL,
                    tarea VARCHAR(255) NOT NULL,
                    maquina VARCHAR(255) DEFAULT '-',
                    fecha_inicio DATE NOT NULL,
                    fecha_cierre DATE NOT NULL,
                    dias_duracion INT DEFAULT 0
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    usuario VARCHAR(50) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS maquinas (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(100) UNIQUE NOT NULL
                )
            """)

            cursor.execute("SELECT * FROM usuarios WHERE usuario = 'Admin'")
            if not cursor.fetchone():
                hashed = bcrypt.hashpw("SistemaMantenimiento0611".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                cursor.execute("INSERT INTO usuarios (usuario, password_hash) VALUES ('Admin', %s)", (hashed,))

            try:
                cursor.execute("ALTER TABLE bitacora ADD COLUMN maquina_1 VARCHAR(255) DEFAULT '-'")
                cursor.execute("ALTER TABLE bitacora ADD COLUMN maquina_2 VARCHAR(255) DEFAULT '-'")
                cursor.execute("ALTER TABLE bitacora ADD COLUMN maquina_3 VARCHAR(255) DEFAULT '-'")
                conn.commit()
            except:
                pass
                
            try:
                cursor.execute("ALTER TABLE bitacora ADD COLUMN tarea_4 VARCHAR(255) DEFAULT '-'")
                cursor.execute("ALTER TABLE bitacora ADD COLUMN avance_4 INT DEFAULT 0")
                cursor.execute("ALTER TABLE bitacora ADD COLUMN fecha_inicio_4 DATE DEFAULT NULL")
                cursor.execute("ALTER TABLE bitacora ADD COLUMN maquina_4 VARCHAR(255) DEFAULT '-'")
                cursor.execute("ALTER TABLE bitacora ADD COLUMN tarea_5 VARCHAR(255) DEFAULT '-'")
                cursor.execute("ALTER TABLE bitacora ADD COLUMN avance_5 INT DEFAULT 0")
                cursor.execute("ALTER TABLE bitacora ADD COLUMN fecha_inicio_5 DATE DEFAULT NULL")
                cursor.execute("ALTER TABLE bitacora ADD COLUMN maquina_5 VARCHAR(255) DEFAULT '-'")
                conn.commit()
            except:
                pass

            try:
                cursor.execute("ALTER TABLE bitacora_completados ADD COLUMN maquina VARCHAR(255) DEFAULT '-'")
                conn.commit()
            except:
                pass

            # Limpiador de espacios y mayusculas automatico en historico
            try:
                cursor.execute("UPDATE bitacora_completados SET maquina = TRIM(UPPER(maquina)) WHERE maquina IS NOT NULL AND maquina != '-'")
                cursor.execute("UPDATE maquinas SET nombre = TRIM(UPPER(nombre)) WHERE nombre IS NOT NULL")
                conn.commit()
            except:
                pass

            conn.commit()
            cursor.close()
            return conn
        except:
            retries -= 1
            time.sleep(3)
    return None

conn = init_connection()

def db_query(query, params=None, fetch=False):
    try:
        conn.ping(reconnect=True, attempts=3, delay=1)
    except:
        pass
        
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, params or ())
    if fetch:
        res = cursor.fetchall()
        cursor.close()
        return res
    conn.commit()
    cursor.close()

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def cerrar_actividades_completadas(trabajador_id, nombre, fi1, fi2, fi3, fi4, fi5, t1, a1, m1, t2, a2, m2, t3, a3, m3, t4, a4, m4, t5, a5, m5):
    tareas = [t1, t2, t3, t4, t5]
    avances = [a1, a2, a3, a4, a5]
    fechas_inicio = [fi1, fi2, fi3, fi4, fi5]
    maquinas = [m1, m2, m3, m4, m5]
    slots = [("tarea_1", "avance_1", "fecha_inicio_1", "maquina_1"),
             ("tarea_2", "avance_2", "fecha_inicio_2", "maquina_2"),
             ("tarea_3", "avance_3", "fecha_inicio_3", "maquina_3"),
             ("tarea_4", "avance_4", "fecha_inicio_4", "maquina_4"),
             ("tarea_5", "avance_5", "fecha_inicio_5", "maquina_5")]
    cerradas = []
    hoy = datetime.now().date()

    for i, (t, a, fi, m) in enumerate(zip(tareas, avances, fechas_inicio, maquinas)):
        if t and t != '-' and a == 100:
            if fi:
                fi_date = fi if hasattr(fi, 'year') else datetime.strptime(str(fi), '%Y-%m-%d').date()
            else:
                fi_date = hoy
            dias = (hoy - fi_date).days
            m_clean = str(m).strip().upper() if m else '-'
            db_query(
                "INSERT INTO bitacora_completados (nombre, tarea, maquina, fecha_inicio, fecha_cierre, dias_duracion) VALUES (%s, %s, %s, %s, %s, %s)",
                (nombre, t, m_clean, fi_date, hoy, dias)
            )
            col_t, col_a, col_fi, col_m = slots[i]
            db_query(
                f"UPDATE bitacora SET {col_t}='-', {col_a}=0, {col_fi}=NULL, {col_m}='-' WHERE id=%s",
                (trabajador_id,)
            )
            cerradas.append(t)

    return cerradas

def obtener_lista_maquinas():
    res = db_query("SELECT nombre FROM maquinas ORDER BY nombre ASC", fetch=True)
    lista = ["-"]
    if res:
        lista.extend([str(r['nombre']).strip().upper() for r in res])
    return sorted(list(set(lista)))

def asegurar_valor_en_lista(lista, valor):
    if not valor:
        valor = "-"
    valor = str(valor).strip().upper()
    opciones = list(lista)
    if valor not in opciones:
        opciones.append(valor)
    return opciones, opciones.index(valor)

def login_screen():
    st.markdown("""
        <div style="text-align:center;padding:3rem 0 2rem 0;">
            <div style="
                display:inline-block;background:#0A0A0A;color:#C8102E;
                font-family:'Bebas Neue',sans-serif;font-size:2.6rem;
                letter-spacing:0.2em;padding:0.4rem 1.6rem;
                border:3px solid #C8102E;margin-bottom:0.5rem;">Grupo Constructor Leravi</div>
            <p style="color:#5A5A5A;font-family:'DM Sans',sans-serif;font-size:0.8rem;
                      letter-spacing:0.2em;text-transform:uppercase;margin-top:0.5rem;">
                Control Administrativo de Personal</p>
        </div>
    """, unsafe_allow_html=True)

    _, center, _ = st.columns([1, 1, 1])
    with center:
        with st.form("login_form"):
            st.markdown("<p style='font-family:DM Sans;font-size:0.75rem;font-weight:600;letter-spacing:0.12em;text-transform:uppercase;color:#5A5A5A;margin-bottom:0.2rem;'>Acceso Restringido</p>", unsafe_allow_html=True)
            user = st.text_input("Usuario")
            pw   = st.text_input("Contrasena", type="password")
            st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
            if st.form_submit_button("INGRESAR"):
                res = db_query("SELECT * FROM usuarios WHERE usuario = %s", (user,), fetch=True)
                if res and check_password(pw, res[0]['password_hash']):
                    st.session_state['logged'] = True
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas")

def admin_panel():
    st.sidebar.markdown("""
        <div style="padding:1rem 0 0.5rem 0;">
            <span style="font-family:'Bebas Neue',sans-serif;font-size:1.5rem;letter-spacing:0.2em;color:white;">CONTROL</span>
            <span style="font-family:'Bebas Neue',sans-serif;font-size:1.5rem;letter-spacing:0.2em;color:#C8102E;"> ADMIN</span>
            <hr style="border-color:#C8102E;margin:0.5rem 0 1rem 0;">
        </div>
    """, unsafe_allow_html=True)

    if st.sidebar.button("Cerrar Sesion"):
        st.session_state['logged'] = False
        st.rerun()

    st.sidebar.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    menu = st.sidebar.radio("NAVEGACION", ["Dashboard", "Alta de Trabajador", "Alta de Maquina", "Asignar Tarea", "Editar Avances", "Bitacora", "Eliminar"])

    if menu == "Dashboard":
        st.markdown("<h1>Dashboard Analitico</h1>", unsafe_allow_html=True)
        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

        # AÑADIMOS "Top Trabajadores" a las vistas
        vista = st.radio("Selecciona una vista:", ["Vision General", "Top Maquinas", "Top Trabajadores"], horizontal=True, label_visibility="collapsed")
        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

        if vista == "Vision General":
            data = db_query("SELECT * FROM bitacora", fetch=True)
            if data:
                df = pd.DataFrame(data)
                df['ID_TRAB'] = df['id'].apply(lambda x: f"TRAB-{x:03d}")

                total = len(df)
                avances = []
                for _, row in df.iterrows():
                    vals = [row.get('avance_1', 0), row.get('avance_2', 0), row.get('avance_3', 0), row.get('avance_4', 0), row.get('avance_5', 0)]
                    activos = [v for v in vals if pd.notna(v) and v > 0]
                    avances.append(sum(activos) / len(activos) if activos else 0)
                prom_global = sum(avances) / len(avances) if avances else 0
                
                res_cerradas = db_query("SELECT COUNT(*) as cnt FROM bitacora_completados", fetch=True)
                total_cerradas = res_cerradas[0]['cnt'] if res_cerradas else 0

                m1, m2, m3 = st.columns(3)
                m1.markdown(f"""
                    <div style="background:#0A0A0A;border-left:4px solid #C8102E;padding:1.2rem 1.4rem;border-radius:3px;">
                        <p style="color:#5A5A5A;font-size:0.7rem;letter-spacing:0.15em;text-transform:uppercase;margin:0;">Total Personal</p>
                        <p style="color:white;font-family:'Bebas Neue',sans-serif;font-size:2.8rem;margin:0;line-height:1.1;">{total}</p>
                    </div>
                """, unsafe_allow_html=True)
                m2.markdown(f"""
                    <div style="background:#0A0A0A;border-left:4px solid #C8102E;padding:1.2rem 1.4rem;border-radius:3px;">
                        <p style="color:#5A5A5A;font-size:0.7rem;letter-spacing:0.15em;text-transform:uppercase;margin:0;">Avance Promedio</p>
                        <p style="color:white;font-family:'Bebas Neue',sans-serif;font-size:2.8rem;margin:0;line-height:1.1;">{prom_global:.1f}%</p>
                    </div>
                """, unsafe_allow_html=True)
                m3.markdown(f"""
                    <div style="background:#0A0A0A;border-left:4px solid #C8102E;padding:1.2rem 1.4rem;border-radius:3px;">
                        <p style="color:#5A5A5A;font-size:0.7rem;letter-spacing:0.15em;text-transform:uppercase;margin:0;">Actividades Cerradas</p>
                        <p style="color:white;font-family:'Bebas Neue',sans-serif;font-size:2.8rem;margin:0;line-height:1.1;">{total_cerradas}</p>
                    </div>
                """, unsafe_allow_html=True)

                st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
                st.markdown("<h2>Registro Completo</h2>", unsafe_allow_html=True)
                st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
                
                columnas_ordenadas = ['ID_TRAB', 'nombre', 'fecha', 
                                      'tarea_1', 'maquina_1', 'avance_1', 'fecha_inicio_1', 
                                      'tarea_2', 'maquina_2', 'avance_2', 'fecha_inicio_2', 
                                      'tarea_3', 'maquina_3', 'avance_3', 'fecha_inicio_3',
                                      'tarea_4', 'maquina_4', 'avance_4', 'fecha_inicio_4',
                                      'tarea_5', 'maquina_5', 'avance_5', 'fecha_inicio_5']
                df_mostrar = df[[c for c in columnas_ordenadas if c in df.columns]]
                st.dataframe(df_mostrar, use_container_width=True, hide_index=True)

                st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
                st.markdown("<h2>Avance por Trabajador</h2>", unsafe_allow_html=True)
                st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

                COLORS_FILL = ["#C8102E", "#E8546A", "#F2A0AC", "#F9B4BE", "#FFC8D2"]

                cols = st.columns(min(len(df), 3))
                for i, (_, row) in enumerate(df.iterrows()):
                    col = cols[i % 3]
                    tareas = [row.get('tarea_1'), row.get('tarea_2'), row.get('tarea_3'), row.get('tarea_4'), row.get('tarea_5')]
                    avs = [row.get('avance_1', 0), row.get('avance_2', 0), row.get('avance_3', 0), row.get('avance_4', 0), row.get('avance_5', 0)]
                    fechas = [row.get('fecha_inicio_1'), row.get('fecha_inicio_2'), row.get('fecha_inicio_3'), row.get('fecha_inicio_4'), row.get('fecha_inicio_5')]
                    maquinas = [row.get('maquina_1', '-'), row.get('maquina_2', '-'), row.get('maquina_3', '-'), row.get('maquina_4', '-'), row.get('maquina_5', '-')]
                    hoy = datetime.now().date()

                    def dias_desde(fi):
                        if not fi or pd.isna(fi):
                            return 0
                        fi_date = fi if hasattr(fi, 'year') else datetime.strptime(str(fi), '%Y-%m-%d').date()
                        return (hoy - fi_date).days

                    labels, values, colors = [], [], []
                    task_dias_html = ""
                    has_active_tasks = False

                    for j, (t, a, m) in enumerate(zip(tareas, avs, maquinas)):
                        if pd.notna(t) and t and t != '-':
                            has_active_tasks = True
                            d = dias_desde(fechas[j])
                            
                            t_safe = html.escape(str(t)[:20])
                            m_safe = html.escape(str(m))
                            a_safe = int(a) if pd.notna(a) and a is not None else 0
                            
                            labels.append(t_safe)
                            values.append(a_safe)
                            colors.append(COLORS_FILL[j])
                            
                            maq_text = f" | {m_safe}" if m_safe and m_safe != '-' else ""
                            task_dias_html += f"""
                                <div style="display:flex;justify-content:space-between;align-items:center;
                                            border-bottom:1px solid #F0F0F0;padding:0.3rem 0;">
                                    <span style="font-family:'DM Sans',sans-serif;font-size:0.78rem;
                                                 color:#2C2C2C;flex:1;">{t_safe}{maq_text}</span>
                                    <span style="font-family:'Bebas Neue',sans-serif;font-size:1rem;
                                                 color:#C8102E;margin-left:0.5rem;white-space:nowrap;">{d} dias</span>
                                </div>"""

                    with col:
                        nombre_safe = html.escape(str(row['nombre']))
                        id_safe = html.escape(str(row['ID_TRAB']))

                        if not has_active_tasks:
                            st.markdown(f"""
                                <div style="background:white;border:1px solid #E8E8E8;border-top:3px solid #C8102E;
                                            border-radius:3px;padding:1rem;margin-bottom:1rem;">
                                    <p style="font-family:'DM Sans',sans-serif;font-size:0.7rem;font-weight:600;
                                              letter-spacing:0.12em;text-transform:uppercase;color:#5A5A5A;margin:0;">
                                        {id_safe}</p>
                                    <p style="font-family:'Bebas Neue',sans-serif;font-size:1.3rem;color:#0A0A0A;
                                              margin:0.2rem 0 0.8rem 0;">{nombre_safe}</p>
                                    <p style="font-family:'DM Sans',sans-serif;font-size:0.85rem;color:#5A5A5A;text-align:center;">
                                        Sin actividades activas</p>
                                </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                                <div style="background:white;border:1px solid #E8E8E8;border-top:3px solid #C8102E;border-bottom:none;
                                            border-radius:3px 3px 0 0;padding:1rem 1rem 0.2rem 1rem;">
                                    <p style="font-family:'DM Sans',sans-serif;font-size:0.7rem;font-weight:600;
                                              letter-spacing:0.12em;text-transform:uppercase;color:#5A5A5A;margin:0 0 0.2rem 0;">
                                        {id_safe}</p>
                                    <p style="font-family:'Bebas Neue',sans-serif;font-size:1.3rem;
                                              color:#0A0A0A;margin:0 0 0.2rem 0;letter-spacing:0.05em;">{nombre_safe}</p>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            if values:
                                labels.reverse()
                                values.reverse()
                                colors.reverse()

                                fig = go.Figure(go.Bar(
                                    x=values,
                                    y=labels,
                                    orientation='h',
                                    marker=dict(color=colors, line=dict(color='#0A0A0A', width=1)),
                                    text=[f"{v}%" for v in values],
                                    textposition='auto',
                                    textfont=dict(size=12, color='white', family='DM Sans'),
                                    hovertemplate='<b>%{y}</b>: %{x}%<extra></extra>'
                                ))
                                fig.update_layout(
                                    paper_bgcolor='white',
                                    plot_bgcolor='white',
                                    margin=dict(t=5, b=5, l=10, r=10),
                                    height=max(150, len(values) * 45),
                                    xaxis=dict(range=[0, 100], showgrid=False, zeroline=False, visible=False),
                                    yaxis=dict(showgrid=False, zeroline=False, tickfont=dict(family='DM Sans', color='#1A1A1A', size=11)),
                                    showlegend=False
                                )
                                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                            else:
                                st.markdown("<div style='background:white; border-left:1px solid #E8E8E8; border-right:1px solid #E8E8E8;'><p style='text-align:center; color:#5A5A5A; font-size:0.85rem; margin:0; padding:1rem 0;'>Actividades en 0%</p></div>", unsafe_allow_html=True)

                            st.markdown(f"""
                                <div style="background:white;border:1px solid #E8E8E8;border-top:none;
                                            border-radius:0 0 3px 3px;padding:0.5rem 1rem 0.8rem 1rem;margin-bottom:1rem;">
                                    <div style="border-top:1px solid #F0F0F0;padding-top:0.5rem;">
                                        <p style="font-family:'DM Sans',sans-serif;font-size:0.65rem;font-weight:600;
                                                  letter-spacing:0.12em;text-transform:uppercase;color:#5A5A5A;margin:0 0 0.4rem 0;">
                                            Tiempo por actividad</p>
                                        {task_dias_html}
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)

                    if (i + 1) % 3 == 0 and i + 1 < len(df):
                        cols = st.columns(3)

            else:
                st.info("No hay registros disponibles")

        elif vista == "Top Maquinas":
            st.markdown("<h2>Maquinas con Mayor Cantidad de Servicios (Historial Total)</h2>", unsafe_allow_html=True)
            
            data_completados = db_query("""
                SELECT maquina, nombre as Empleado, tarea as Actividad, fecha_inicio as 'Fecha Inicio', fecha_cierre as 'Fecha Cierre', dias_duracion as Dias 
                FROM bitacora_completados 
                WHERE maquina != '-' AND maquina IS NOT NULL 
            """, fetch=True)

            if data_completados:
                df_comp = pd.DataFrame(data_completados)
                
                df_comp['maquina_limpia'] = df_comp['maquina'].astype(str).str.upper().str.strip()
                
                df_counts = df_comp.groupby('maquina_limpia').size().reset_index(name='total')
                df_top = df_counts.sort_values(by='total', ascending=False).head(10)
                
                x_nombres = df_top['maquina_limpia'].tolist()
                y_totales = df_top['total'].tolist()
                text_totales = [str(v) for v in y_totales]
                
                fig_maq = go.Figure(go.Bar(
                    x=x_nombres,
                    y=y_totales,
                    orientation='v',
                    marker_color='#C8102E',
                    text=text_totales,
                    textposition='outside',
                    textfont=dict(size=14, family='DM Sans', color='#1A1A1A')
                ))
                
                fig_maq.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    xaxis=dict(
                        title="Maquina",
                        type='category', 
                        categoryorder='array',
                        categoryarray=x_nombres,
                        tickfont=dict(family='DM Sans', size=12, color='#1A1A1A')
                    ),
                    yaxis=dict(
                        title="Servicios Completados",
                        tickmode='linear',
                        tick0=0,
                        dtick=1, 
                        rangemode='tozero', 
                        tickfont=dict(family='DM Sans', size=12, color='#1A1A1A'),
                        showgrid=True,
                        gridcolor='#E8E8E8'
                    ),
                    height=450,
                    margin=dict(t=30, b=30, l=30, r=30)
                )
                st.plotly_chart(fig_maq, use_container_width=True, config={'displayModeBar': False})

                st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
                st.markdown("<h3>Historial Detallado por Maquina</h3>", unsafe_allow_html=True)
                
                maq_sel = st.selectbox("Selecciona una maquina de la lista para ver todos sus servicios completados:", x_nombres)
                
                if maq_sel:
                    detalles = df_comp[df_comp['maquina_limpia'] == maq_sel]
                    detalles_mostrar = detalles[['Empleado', 'Actividad', 'Fecha Inicio', 'Fecha Cierre', 'Dias']]
                    
                    st.markdown(f"<p style='font-family:DM Sans; font-size:0.85rem; color:#5A5A5A;'>Mostrando <b>{len(detalles_mostrar)}</b> registro(s) encontrado(s).</p>", unsafe_allow_html=True)
                    st.dataframe(detalles_mostrar, use_container_width=True, hide_index=True)
            else:
                st.info("Aun no hay suficientes servicios completados registrados para generar este analisis.")

        # ---- NUEVA PESTAÑA: TOP TRABAJADORES ----
        elif vista == "Top Trabajadores":
            st.markdown("<h2>Trabajadores con Mayor Cantidad de Tareas Completadas</h2>", unsafe_allow_html=True)
            
            data_completados_trab = db_query("""
                SELECT nombre as Empleado, maquina as Maquina, tarea as Actividad, fecha_inicio as 'Fecha Inicio', fecha_cierre as 'Fecha Cierre', dias_duracion as Dias 
                FROM bitacora_completados 
            """, fetch=True)

            if data_completados_trab:
                df_comp_t = pd.DataFrame(data_completados_trab)
                
                # Limpieza por si hay espacios invisibles
                df_comp_t['empleado_limpio'] = df_comp_t['Empleado'].astype(str).str.strip()
                
                df_counts_t = df_comp_t.groupby('empleado_limpio').size().reset_index(name='total')
                df_top_t = df_counts_t.sort_values(by='total', ascending=False).head(10)
                
                # Listas puras para Plotly
                x_nombres_t = df_top_t['empleado_limpio'].tolist()
                y_totales_t = df_top_t['total'].tolist()
                text_totales_t = [str(v) for v in y_totales_t]
                
                fig_trab = go.Figure(go.Bar(
                    x=x_nombres_t,
                    y=y_totales_t,
                    orientation='v',
                    marker_color='#C8102E', # Mismo color que todo el sistema
                    text=text_totales_t,
                    textposition='outside',
                    textfont=dict(size=14, family='DM Sans', color='#1A1A1A')
                ))
                
                fig_trab.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    xaxis=dict(
                        title="Trabajador",
                        type='category', 
                        categoryorder='array',
                        categoryarray=x_nombres_t,
                        tickfont=dict(family='DM Sans', size=12, color='#1A1A1A')
                    ),
                    yaxis=dict(
                        title="Tareas Completadas",
                        tickmode='linear',
                        tick0=0,
                        dtick=1, 
                        rangemode='tozero', 
                        tickfont=dict(family='DM Sans', size=12, color='#1A1A1A'),
                        showgrid=True,
                        gridcolor='#E8E8E8'
                    ),
                    height=450,
                    margin=dict(t=30, b=30, l=30, r=30)
                )
                st.plotly_chart(fig_trab, use_container_width=True, config={'displayModeBar': False})

                st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
                st.markdown("<h3>Historial Detallado por Trabajador</h3>", unsafe_allow_html=True)
                
                trab_sel = st.selectbox("Selecciona un trabajador de la lista para ver todas sus tareas completadas:", x_nombres_t)
                
                if trab_sel:
                    detalles_t = df_comp_t[df_comp_t['empleado_limpio'] == trab_sel]
                    detalles_mostrar_t = detalles_t[['Actividad', 'Maquina', 'Fecha Inicio', 'Fecha Cierre', 'Dias']]
                    
                    st.markdown(f"<p style='font-family:DM Sans; font-size:0.85rem; color:#5A5A5A;'>Mostrando <b>{len(detalles_mostrar_t)}</b> registro(s) encontrado(s).</p>", unsafe_allow_html=True)
                    st.dataframe(detalles_mostrar_t, use_container_width=True, hide_index=True)
            else:
                st.info("Aun no hay suficientes tareas completadas registradas para generar este analisis.")

    elif menu == "Alta de Trabajador":
        st.markdown("<h1>Alta de Trabajador</h1>", unsafe_allow_html=True)
        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        with st.form("alta_trabajador"):
            nom = st.text_input("Nombre Completo")
            st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
            if st.form_submit_button("REGISTRAR TRABAJADOR"):
                if nom:
                    db_query("INSERT INTO bitacora (nombre, fecha) VALUES (%s, %s)",
                             (nom, datetime.now().date()))
                    st.success("Trabajador registrado correctamente")
                    st.rerun()

    elif menu == "Alta de Maquina":
        st.markdown("<h1>Alta de Maquina</h1>", unsafe_allow_html=True)
        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        with st.form("alta_maquina"):
            nom_maq = st.text_input("Nombre de la Maquina")
            st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
            if st.form_submit_button("REGISTRAR MAQUINA"):
                if nom_maq:
                    nom_maq_clean = nom_maq.strip().upper()
                    try:
                        db_query("INSERT INTO maquinas (nombre) VALUES (%s)", (nom_maq_clean,))
                        st.success("Maquina registrada correctamente")
                        time.sleep(1)
                        st.rerun()
                    except mysql.connector.IntegrityError:
                        st.error("Esta maquina ya se encuentra registrada.")

    elif menu == "Asignar Tarea":
        st.markdown("<h1>Asignar Tarea</h1>", unsafe_allow_html=True)
        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        res = db_query("SELECT * FROM bitacora", fetch=True)
        lista_maquinas = obtener_lista_maquinas()

        if res:
            opc = {f"{r['nombre']} (ID: TRAB-{r['id']:03d})": r for r in res}
            with st.form("asignar_tarea"):
                sel = st.selectbox("Seleccione Trabajador", list(opc.keys()))
                tar = st.text_input("Nueva Tarea")
                maq = st.selectbox("Maquina (Opcional)", lista_maquinas)
                st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
                
                if st.form_submit_button("ASIGNAR TAREA"):
                    if tar:
                        curr = opc[sel]
                        hoy = datetime.now().date()
                        val_maq = maq.strip().upper() if maq else '-'
                        
                        if curr.get('tarea_1') == '-' or not curr.get('tarea_1'):
                            db_query("UPDATE bitacora SET tarea_1=%s, maquina_1=%s, avance_1=0, fecha_inicio_1=%s WHERE id=%s", (tar, val_maq, hoy, curr['id']))
                            st.success("Tarea asignada en el espacio 1")
                            st.rerun()
                        elif curr.get('tarea_2') == '-' or not curr.get('tarea_2'):
                            db_query("UPDATE bitacora SET tarea_2=%s, maquina_2=%s, avance_2=0, fecha_inicio_2=%s WHERE id=%s", (tar, val_maq, hoy, curr['id']))
                            st.success("Tarea asignada en el espacio 2")
                            st.rerun()
                        elif curr.get('tarea_3') == '-' or not curr.get('tarea_3'):
                            db_query("UPDATE bitacora SET tarea_3=%s, maquina_3=%s, avance_3=0, fecha_inicio_3=%s WHERE id=%s", (tar, val_maq, hoy, curr['id']))
                            st.success("Tarea asignada en el espacio 3")
                            st.rerun()
                        elif curr.get('tarea_4') == '-' or not curr.get('tarea_4'):
                            db_query("UPDATE bitacora SET tarea_4=%s, maquina_4=%s, avance_4=0, fecha_inicio_4=%s WHERE id=%s", (tar, val_maq, hoy, curr['id']))
                            st.success("Tarea asignada en el espacio 4")
                            st.rerun()
                        elif curr.get('tarea_5') == '-' or not curr.get('tarea_5'):
                            db_query("UPDATE bitacora SET tarea_5=%s, maquina_5=%s, avance_5=0, fecha_inicio_5=%s WHERE id=%s", (tar, val_maq, hoy, curr['id']))
                            st.success("Tarea asignada en el espacio 5")
                            st.rerun()
                        else:
                            st.error("El trabajador ya tiene 5 tareas activas. Cierre una antes de asignar otra.")
        else:
            st.info("Primero debe dar de alta a un trabajador en la pestana 'Alta de Trabajador'.")

    elif menu == "Editar Avances":
        st.markdown("<h1>Actualizar Avances</h1>", unsafe_allow_html=True)
        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        res = db_query("SELECT * FROM bitacora", fetch=True)
        lista_maquinas = obtener_lista_maquinas()

        if res:
            opc  = {r['nombre']: r for r in res}
            sel  = st.selectbox("Seleccione Personal", list(opc.keys()))
            curr = opc[sel]
            st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
            with st.form("upd"):
                st.markdown("### ", unsafe_allow_html=True)
                c1, c2, c3 = st.columns([2, 2, 1])
                t1 = c1.text_input("Tarea 1", value=curr.get('tarea_1', '-'))
                opts_m1, idx_m1 = asegurar_valor_en_lista(lista_maquinas, curr.get('maquina_1', '-'))
                m1 = c2.selectbox("Maquina 1", opts_m1, index=idx_m1)
                a1 = c3.number_input("Avance 1 (%)", 0, 100, curr.get('avance_1', 0), step=5)
                
                st.markdown("###", unsafe_allow_html=True)
                c4, c5, c6 = st.columns([2, 2, 1])
                t2 = c4.text_input("Tarea 2", value=curr.get('tarea_2', '-'))
                opts_m2, idx_m2 = asegurar_valor_en_lista(lista_maquinas, curr.get('maquina_2', '-'))
                m2 = c5.selectbox("Maquina 2", opts_m2, index=idx_m2)
                a2 = c6.number_input("Avance 2 (%)", 0, 100, curr.get('avance_2', 0), step=5)
                
                st.markdown("### ", unsafe_allow_html=True)
                c7, c8, c9 = st.columns([2, 2, 1])
                t3 = c7.text_input("Tarea 3", value=curr.get('tarea_3', '-'))
                opts_m3, idx_m3 = asegurar_valor_en_lista(lista_maquinas, curr.get('maquina_3', '-'))
                m3 = c8.selectbox("Maquina 3", opts_m3, index=idx_m3)
                a3 = c9.number_input("Avance 3 (%)", 0, 100, curr.get('avance_3', 0), step=5)

                st.markdown("### ", unsafe_allow_html=True)
                c10, c11, c12 = st.columns([2, 2, 1])
                t4 = c10.text_input("Tarea 4", value=curr.get('tarea_4', '-'))
                opts_m4, idx_m4 = asegurar_valor_en_lista(lista_maquinas, curr.get('maquina_4', '-'))
                m4 = c11.selectbox("Maquina 4", opts_m4, index=idx_m4)
                a4 = c12.number_input("Avance 4 (%)", 0, 100, curr.get('avance_4', 0), step=5)

                st.markdown("### ", unsafe_allow_html=True)
                c13, c14, c15 = st.columns([2, 2, 1])
                t5 = c13.text_input("Tarea 5", value=curr.get('tarea_5', '-'))
                opts_m5, idx_m5 = asegurar_valor_en_lista(lista_maquinas, curr.get('maquina_5', '-'))
                m5 = c14.selectbox("Maquina 5", opts_m5, index=idx_m5)
                a5 = c15.number_input("Avance 5 (%)", 0, 100, curr.get('avance_5', 0), step=5)
                
                st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
                
                if st.form_submit_button("ACTUALIZAR REGISTRO"):
                    hoy = datetime.now().date()
                    nuevas_tareas = [
                        (t1, "fecha_inicio_1", curr.get('tarea_1'), curr.get('fecha_inicio_1')),
                        (t2, "fecha_inicio_2", curr.get('tarea_2'), curr.get('fecha_inicio_2')),
                        (t3, "fecha_inicio_3", curr.get('tarea_3'), curr.get('fecha_inicio_3')),
                        (t4, "fecha_inicio_4", curr.get('tarea_4'), curr.get('fecha_inicio_4')),
                        (t5, "fecha_inicio_5", curr.get('tarea_5'), curr.get('fecha_inicio_5'))
                    ]
                    
                    fi1 = curr.get('fecha_inicio_1')
                    fi2 = curr.get('fecha_inicio_2')
                    fi3 = curr.get('fecha_inicio_3')
                    fi4 = curr.get('fecha_inicio_4')
                    fi5 = curr.get('fecha_inicio_5')
                    fi_nuevas = [fi1, fi2, fi3, fi4, fi5]
                    
                    for idx, (nueva_t, col_fi, prev_t, prev_fi) in enumerate(nuevas_tareas):
                        if nueva_t and nueva_t != '-' and (not prev_t or prev_t == '-'):
                            fi_nuevas[idx] = hoy
                    
                    fi1, fi2, fi3, fi4, fi5 = fi_nuevas

                    m1_clean = m1.strip().upper() if m1 else '-'
                    m2_clean = m2.strip().upper() if m2 else '-'
                    m3_clean = m3.strip().upper() if m3 else '-'
                    m4_clean = m4.strip().upper() if m4 else '-'
                    m5_clean = m5.strip().upper() if m5 else '-'

                    db_query(
                        "UPDATE bitacora SET tarea_1=%s, avance_1=%s, fecha_inicio_1=%s, maquina_1=%s, tarea_2=%s, avance_2=%s, fecha_inicio_2=%s, maquina_2=%s, tarea_3=%s, avance_3=%s, fecha_inicio_3=%s, maquina_3=%s, tarea_4=%s, avance_4=%s, fecha_inicio_4=%s, maquina_4=%s, tarea_5=%s, avance_5=%s, fecha_inicio_5=%s, maquina_5=%s WHERE id=%s",
                        (t1, a1, fi1, m1_clean, t2, a2, fi2, m2_clean, t3, a3, fi3, m3_clean, t4, a4, fi4, m4_clean, t5, a5, fi5, m5_clean, curr['id'])
                    )
                    
                    cerradas = cerrar_actividades_completadas(
                        curr['id'], sel, fi1, fi2, fi3, fi4, fi5, t1, a1, m1_clean, t2, a2, m2_clean, t3, a3, m3_clean, t4, a4, m4_clean, t5, a5, m5_clean
                    )
                    if cerradas:
                        for c in cerradas:
                            st.success(f"Actividad cerrada y enviada a Bitacora: {c}")
                    else:
                        st.success("Registro actualizado correctamente")
                    st.rerun()

            actividades = [
                ("tarea_1", "avance_1", "fecha_inicio_1", "maquina_1", curr.get('tarea_1', '-'), curr.get('avance_1', 0)),
                ("tarea_2", "avance_2", "fecha_inicio_2", "maquina_2", curr.get('tarea_2', '-'), curr.get('avance_2', 0)),
                ("tarea_3", "avance_3", "fecha_inicio_3", "maquina_3", curr.get('tarea_3', '-'), curr.get('avance_3', 0)),
                ("tarea_4", "avance_4", "fecha_inicio_4", "maquina_4", curr.get('tarea_4', '-'), curr.get('avance_4', 0)),
                ("tarea_5", "avance_5", "fecha_inicio_5", "maquina_5", curr.get('tarea_5', '-'), curr.get('avance_5', 0)),
            ]
            activas = [(ct, ca, cfi, cm, t, a) for ct, ca, cfi, cm, t, a in actividades if t and t != '-']

            if activas:
                st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
                st.markdown("""
                    <div style="border-top:2px solid #E8E8E8;padding-top:1.2rem;">
                        <p style="font-family:'Bebas Neue',sans-serif;font-size:1.4rem;letter-spacing:0.08em;
                                  color:#0A0A0A;margin:0 0 0.3rem 0;">Eliminar Actividad</p>
                        <p style="font-family:'DM Sans',sans-serif;font-size:0.8rem;color:#5A5A5A;margin:0 0 1rem 0;">
                            Selecciona la actividad a eliminar por error. Esta accion no se puede deshacer.</p>
                    </div>
                """, unsafe_allow_html=True)

                for col_t, col_a, col_fi, col_m, nombre_t, avance_t in activas:
                    nombre_t_safe = html.escape(str(nombre_t))
                    c_info, c_btn = st.columns([5, 1])
                    c_info.markdown(f"""
                        <div style="background:white;border:1px solid #E8E8E8;border-left:3px solid #C8102E;
                                    border-radius:3px;padding:0.7rem 1rem;margin-bottom:0.5rem;">
                            <p style="font-family:'DM Sans',sans-serif;font-size:0.7rem;font-weight:600;
                                      letter-spacing:0.1em;text-transform:uppercase;color:#5A5A5A;margin:0;">
                                {col_t.replace('_', ' ').upper()}</p>
                            <p style="font-family:'DM Sans',sans-serif;font-size:0.95rem;color:#0A0A0A;
                                      margin:0.1rem 0 0 0;">{nombre_t_safe}
                                <span style="color:#C8102E;font-weight:600;margin-left:0.5rem;">{avance_t}%</span>
                            </p>
                        </div>
                    """, unsafe_allow_html=True)
                    if c_btn.button("BORRAR", key=f"del_{col_t}_{curr['id']}"):
                        db_query(
                            f"UPDATE bitacora SET {col_t}='-', {col_a}=0, {col_fi}=NULL, {col_m}='-' WHERE id=%s",
                            (curr['id'],)
                        )
                        st.warning(f"Actividad eliminada: {nombre_t_safe}")
                        time.sleep(0.8)
                        st.rerun()

    elif menu == "Bitacora":
        st.markdown("<h1>Bitacora de Actividades Completadas</h1>", unsafe_allow_html=True)
        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

        data = db_query("SELECT * FROM bitacora_completados ORDER BY fecha_cierre DESC", fetch=True)
        if data:
            df_bit = pd.DataFrame(data)
            df_bit.rename(columns={
                'nombre':        'Empleado',
                'tarea':         'Actividad',
                'maquina':       'Maquina',
                'fecha_inicio':  'Fecha Inicio',
                'fecha_cierre':  'Fecha Cierre',
                'dias_duracion': 'Dias'
            }, inplace=True)
            df_bit.drop(columns=['id'], inplace=True)

            total_bit        = len(df_bit)
            empleados_unicos = df_bit['Empleado'].nunique()
            ultima           = str(df_bit['Fecha Cierre'].iloc[0])

            m1, m2, m3 = st.columns(3)
            m1.markdown(f"""
                <div style="background:#0A0A0A;border-left:4px solid #C8102E;padding:1.2rem 1.4rem;border-radius:3px;">
                    <p style="color:#5A5A5A;font-size:0.7rem;letter-spacing:0.15em;text-transform:uppercase;margin:0;">Total Cerradas</p>
                    <p style="color:white;font-family:'Bebas Neue',sans-serif;font-size:2.8rem;margin:0;line-height:1.1;">{total_bit}</p>
                </div>
            """, unsafe_allow_html=True)
            m2.markdown(f"""
                <div style="background:#0A0A0A;border-left:4px solid #C8102E;padding:1.2rem 1.4rem;border-radius:3px;">
                    <p style="color:#5A5A5A;font-size:0.7rem;letter-spacing:0.15em;text-transform:uppercase;margin:0;">Empleados Participantes</p>
                    <p style="color:white;font-family:'Bebas Neue',sans-serif;font-size:2.8rem;margin:0;line-height:1.1;">{empleados_unicos}</p>
                </div>
            """, unsafe_allow_html=True)
            m3.markdown(f"""
                <div style="background:#0A0A0A;border-left:4px solid #C8102E;padding:1.2rem 1.4rem;border-radius:3px;">
                    <p style="color:#5A5A5A;font-size:0.7rem;letter-spacing:0.15em;text-transform:uppercase;margin:0;">Ultimo Cierre</p>
                    <p style="color:white;font-family:'Bebas Neue',sans-serif;font-size:1.8rem;margin:0;line-height:1.3;">{ultima}</p>
                </div>
            """, unsafe_allow_html=True)

            st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

            res_trabajadores = db_query("SELECT nombre FROM bitacora ORDER BY nombre ASC", fetch=True)
            lista_trabajadores = ["Todos"]
            if res_trabajadores:
                lista_trabajadores.extend([r['nombre'] for r in res_trabajadores])

            col_f1, col_f2 = st.columns(2)
            with col_f1:
                filtro_empleado = st.selectbox("Filtrar por Empleado", lista_trabajadores)
            with col_f2:
                buscar = st.text_input("Buscar por Actividad o Maquina")

            if filtro_empleado != "Todos":
                df_bit = df_bit[df_bit['Empleado'] == filtro_empleado]

            if buscar:
                mask = (
                    df_bit['Actividad'].str.contains(buscar, case=False, na=False) |
                    df_bit['Maquina'].str.contains(buscar, case=False, na=False)
                )
                df_bit = df_bit[mask]

            st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
            if not df_bit.empty:
                st.dataframe(df_bit, use_container_width=True, hide_index=True)
            else:
                st.warning("No se encontraron registros con esos filtros.")
        else:
            st.info("No hay actividades completadas aun")

    elif menu == "Eliminar":
        st.markdown("<h1>Eliminar Registro</h1>", unsafe_allow_html=True)
        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        res = db_query("SELECT id, nombre FROM bitacora", fetch=True)
        if res:
            opc = {r['nombre']: r['id'] for r in res}
            sel = st.selectbox("Seleccione Registro a Eliminar", list(opc.keys()))
            st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
            if st.button("CONFIRMAR ELIMINACION", type="primary"):
                db_query("DELETE FROM bitacora WHERE id = %s", (opc[sel],))
                st.warning("Registro eliminado")
                time.sleep(1)
                st.rerun()

if conn:
    if 'logged' not in st.session_state:
        st.session_state['logged'] = False

    if not st.session_state['logged']:
        login_screen()
    else:
        admin_panel()
else:
    st.error("No se pudo conectar a la base de datos. Verifica tus credenciales o el estado del servidor MySQL.")
