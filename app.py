import streamlit as st
import pandas as pd
import mysql.connector
import bcrypt
from datetime import datetime
import time
import plotly.graph_objects as go
import os

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
                    tarea_3 VARCHAR(255) DEFAULT '-', avance_3 INT DEFAULT 0, fecha_inicio_3 DATE DEFAULT NULL, maquina_3 VARCHAR(255) DEFAULT '-'
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
                cursor.execute("ALTER TABLE bitacora_completados ADD COLUMN maquina VARCHAR(255) DEFAULT '-'")
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

def cerrar_actividades_completadas(trabajador_id, nombre, fi1, fi2, fi3, t1, a1, m1, t2, a2, m2, t3, a3, m3):
    tareas = [t1, t2, t3]
    avances = [a1, a2, a3]
    fechas_inicio = [fi1, fi2, fi3]
    maquinas = [m1, m2, m3]
    slots = [("tarea_1", "avance_1", "fecha_inicio_1", "maquina_1"),
             ("tarea_2", "avance_2", "fecha_inicio_2", "maquina_2"),
             ("tarea_3", "avance_3", "fecha_inicio_3", "maquina_3")]
    cerradas = []
    hoy = datetime.now().date()

    for i, (t, a, fi, m) in enumerate(zip(tareas, avances, fechas_inicio, maquinas)):
        if t and t != '-' and a == 100:
            if fi:
                fi_date = fi if hasattr(fi, 'year') else datetime.strptime(str(fi), '%Y-%m-%d').date()
            else:
                fi_date = hoy
            dias = (hoy - fi_date).days
            db_query(
                "INSERT INTO bitacora_completados (nombre, tarea, maquina, fecha_inicio, fecha_cierre, dias_duracion) VALUES (%s, %s, %s, %s, %s, %s)",
                (nombre, t, m, fi_date, hoy, dias)
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
        lista.extend([r['nombre'] for r in res])
    return lista

def asegurar_valor_en_lista(lista, valor):
    if not valor:
        valor = "-"
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
                border:3px solid #C8102E;margin-bottom:0.5rem;">Grupo Constructora Leravi</div>
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
        st.markdown("<h1>Dashboard de Personal</h1>", unsafe_allow_html=True)
        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        data = db_query("SELECT * FROM bitacora", fetch=True)
        if data:
            df = pd.DataFrame(data)
            df['ID_TRAB'] = df['id'].apply(lambda x: f"TRAB-{x:03d}")

            total = len(df)
            avances = []
            for _, row in df.iterrows():
                vals = [row['avance_1'], row['avance_2'], row['avance_3']]
                activos = [v for v in vals if v > 0]
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
            
            columnas_ordenadas = ['ID_TRAB', 'nombre', 'fecha', 'tarea_1', 'maquina_1', 'avance_1', 'fecha_inicio_1', 'tarea_2', 'maquina_2', 'avance_2', 'fecha_inicio_2', 'tarea_3', 'maquina_3', 'avance_3', 'fecha_inicio_3']
            df_mostrar = df[columnas_ordenadas]
            st.dataframe(df_mostrar, use_container_width=True, hide_index=True)

            st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
            st.markdown("<h2>Avance por Trabajador</h2>", unsafe_allow_html=True)
            st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

            COLORS_FILL = ["#C8102E", "#E8546A", "#F2A0AC"]

            cols = st.columns(min(len(df), 3))
            for i, (_, row) in enumerate(df.iterrows()):
                col = cols[i % 3]
                tareas = [row['tarea_1'], row['tarea_2'], row['tarea_3']]
                avs = [row['avance_1'], row['avance_2'], row['avance_3']]
                fechas = [row.get('fecha_inicio_1'), row.get('fecha_inicio_2'), row.get('fecha_inicio_3')]
                maquinas = [row.get('maquina_1', '-'), row.get('maquina_2', '-'), row.get('maquina_3', '-')]
                hoy = datetime.now().date()

                def dias_desde(fi):
                    if not fi:
                        return 0
                    fi_date = fi if hasattr(fi, 'year') else datetime.strptime(str(fi), '%Y-%m-%d').date()
                    return (hoy - fi_date).days

                labels, values, colors = [], [], []
                task_dias_html = ""
                has_active_tasks = False

                for j, (t, a, m) in enumerate(zip(tareas, avs, maquinas)):
                    if t and t != '-':
                        has_active_tasks = True
                        d = dias_desde(fechas[j])
                        labels.append(t[:20])
                        values.append(a)
                        colors.append(COLORS_FILL[j])
                        
                        maq_text = f" | {m}" if m and m != '-' else ""
                        task_dias_html += f"""
                            <div style="display:flex;justify-content:space-between;align-items:center;
                                        border-bottom:1px solid #F0F0F0;padding:0.3rem 0;">
                                <span style="font-family:'DM Sans',sans-serif;font-size:0.78rem;
                                             color:#2C2C2C;flex:1;">{t[:20]}{maq_text}</span>
                                <span style="font-family:'Bebas Neue',sans-serif;font-size:1rem;
                                             color:#C8102E;margin-left:0.5rem;white-space:nowrap;">{d} dias</span>
                            </div>"""

                with col:
                    if not has_active_tasks:
                        st.markdown(f"""
                            <div style="background:white;border:1px solid #E8E8E8;border-top:3px solid #C8102E;
                                        border-radius:3px;padding:1rem;margin-bottom:1rem;">
                                <p style="font-family:'DM Sans',sans-serif;font-size:0.7rem;font-weight:600;
                                          letter-spacing:0.12em;text-transform:uppercase;color:#5A5A5A;margin:0;">
                                    {row['ID_TRAB']}</p>
                                <p style="font-family:'Bebas Neue',sans-serif;font-size:1.3rem;color:#0A0A0A;
                                          margin:0.2rem 0 0.8rem 0;">{row['nombre']}</p>
                                <p style="font-family:'DM Sans',sans-serif;font-size:0.85rem;color:#5A5A5A;text-align:center;">
                                    Sin actividades activas</p>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                            <div style="background:white;border:1px solid #E8E8E8;border-top:3px solid #C8102E;
                                        border-radius:3px;padding:1rem 1rem 0.8rem 1rem;margin-bottom:1rem;">
                                <p style="font-family:'DM Sans',sans-serif;font-size:0.7rem;font-weight:600;
                                          letter-spacing:0.12em;text-transform:uppercase;color:#5A5A5A;margin:0 0 0.2rem 0;">
                                    {row['ID_TRAB']}</p>
                                <p style="font-family:'Bebas Neue',sans-serif;font-size:1.3rem;
                                          color:#0A0A0A;margin:0 0 0.6rem 0;letter-spacing:0.05em;">{row['nombre']}</p>
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
                                paper_bgcolor='rgba(0,0,0,0)',
                                plot_bgcolor='rgba(0,0,0,0)',
                                margin=dict(t=10, b=10, l=10, r=10),
                                height=200,
                                xaxis=dict(range=[0, 100], showgrid=False, zeroline=False, visible=False),
                                yaxis=dict(showgrid=False, zeroline=False, tickfont=dict(family='DM Sans', color='#1A1A1A', size=11)),
                                showlegend=False
                            )
                            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                        else:
                            st.markdown("<p style='text-align:center; color:#5A5A5A; font-size:0.85rem;'>Actividades en 0%</p>", unsafe_allow_html=True)

                        st.markdown(f"""
                                    <div style="border-top:1px solid #F0F0F0;padding-top:0.5rem;margin-top:0.2rem;">
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
                    try:
                        db_query("INSERT INTO maquinas (nombre) VALUES (%s)", (nom_maq,))
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
                        val_maq = maq if maq else '-'
                        
                        if curr['tarea_1'] == '-' or not curr['tarea_1']:
                            db_query("UPDATE bitacora SET tarea_1=%s, maquina_1=%s, avance_1=0, fecha_inicio_1=%s WHERE id=%s", (tar, val_maq, hoy, curr['id']))
                            st.success("Tarea asignada en el espacio 1")
                            st.rerun()
                        elif curr['tarea_2'] == '-' or not curr['tarea_2']:
                            db_query("UPDATE bitacora SET tarea_2=%s, maquina_2=%s, avance_2=0, fecha_inicio_2=%s WHERE id=%s", (tar, val_maq, hoy, curr['id']))
                            st.success("Tarea asignada en el espacio 2")
                            st.rerun()
                        elif curr['tarea_3'] == '-' or not curr['tarea_3']:
                            db_query("UPDATE bitacora SET tarea_3=%s, maquina_3=%s, avance_3=0, fecha_inicio_3=%s WHERE id=%s", (tar, val_maq, hoy, curr['id']))
                            st.success("Tarea asignada en el espacio 3")
                            st.rerun()
                        else:
                            st.error("El trabajador ya tiene 3 tareas activas. Cierre una antes de asignar otra.")
        else:
            st.info("Primero debe dar de alta a un trabajador en la pestana 'Alta de Trabajador'.")

    elif menu == "Editar Avances":
        st.markdown("<h1>Actualizar Avances</h1>", unsafe_allow_html=True)
        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        res = db_query("SELECT id, nombre FROM bitacora", fetch=True)
        lista_maquinas = obtener_lista_maquinas()

        if res:
            opc  = {r['nombre']: r['id'] for r in res}
            sel  = st.selectbox("Seleccione Personal", list(opc.keys()))
            curr = db_query("SELECT * FROM bitacora WHERE id = %s", (opc[sel],), fetch=True)[0]
            st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
            with st.form("upd"):
                st.markdown("### Espacio 1", unsafe_allow_html=True)
                c1, c2, c3 = st.columns([2, 2, 1])
                t1 = c1.text_input("Tarea 1", value=curr['tarea_1'])
                opts_m1, idx_m1 = asegurar_valor_en_lista(lista_maquinas, curr['maquina_1'])
                m1 = c2.selectbox("Maquina 1", opts_m1, index=idx_m1)
                a1 = c3.number_input("Avance 1 (%)", 0, 100, curr['avance_1'], step=5)
                
                st.markdown("### Espacio 2", unsafe_allow_html=True)
                c4, c5, c6 = st.columns([2, 2, 1])
                t2 = c4.text_input("Tarea 2", value=curr['tarea_2'])
                opts_m2, idx_m2 = asegurar_valor_en_lista(lista_maquinas, curr['maquina_2'])
                m2 = c5.selectbox("Maquina 2", opts_m2, index=idx_m2)
                a2 = c6.number_input("Avance 2 (%)", 0, 100, curr['avance_2'], step=5)
                
                st.markdown("### Espacio 3", unsafe_allow_html=True)
                c7, c8, c9 = st.columns([2, 2, 1])
                t3 = c7.text_input("Tarea 3", value=curr['tarea_3'])
                opts_m3, idx_m3 = asegurar_valor_en_lista(lista_maquinas, curr['maquina_3'])
                m3 = c8.selectbox("Maquina 3", opts_m3, index=idx_m3)
                a3 = c9.number_input("Avance 3 (%)", 0, 100, curr['avance_3'], step=5)
                
                st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
                
                if st.form_submit_button("ACTUALIZAR REGISTRO"):
                    hoy = datetime.now().date()
                    nuevas_tareas = [
                        (t1, "fecha_inicio_1", curr['tarea_1'], curr.get('fecha_inicio_1')),
                        (t2, "fecha_inicio_2", curr['tarea_2'], curr.get('fecha_inicio_2')),
                        (t3, "fecha_inicio_3", curr['tarea_3'], curr.get('fecha_inicio_3')),
                    ]
                    fi1 = curr.get('fecha_inicio_1')
                    fi2 = curr.get('fecha_inicio_2')
                    fi3 = curr.get('fecha_inicio_3')
                    fi_nuevas = [fi1, fi2, fi3]
                    
                    for idx, (nueva_t, col_fi, prev_t, prev_fi) in enumerate(nuevas_tareas):
                        if nueva_t and nueva_t != '-' and (not prev_t or prev_t == '-'):
                            fi_nuevas[idx] = hoy
                    
                    fi1, fi2, fi3 = fi_nuevas

                    db_query(
                        "UPDATE bitacora SET tarea_1=%s, avance_1=%s, fecha_inicio_1=%s, maquina_1=%s, tarea_2=%s, avance_2=%s, fecha_inicio_2=%s, maquina_2=%s, tarea_3=%s, avance_3=%s, fecha_inicio_3=%s, maquina_3=%s WHERE id=%s",
                        (t1, a1, fi1, m1 if m1 else '-', t2, a2, fi2, m2 if m2 else '-', t3, a3, fi3, m3 if m3 else '-', opc[sel])
                    )
                    
                    cerradas = cerrar_actividades_completadas(
                        opc[sel], sel, fi1, fi2, fi3, t1, a1, m1, t2, a2, m2, t3, a3, m3
                    )
                    if cerradas:
                        for c in cerradas:
                            st.success(f"Actividad cerrada y enviada a Bitacora: {c}")
                    else:
                        st.success("Registro actualizado correctamente")
                    st.rerun()

            actividades = [
                ("tarea_1", "avance_1", "fecha_inicio_1", "maquina_1", curr['tarea_1'], curr['avance_1']),
                ("tarea_2", "avance_2", "fecha_inicio_2", "maquina_2", curr['tarea_2'], curr['avance_2']),
                ("tarea_3", "avance_3", "fecha_inicio_3", "maquina_3", curr['tarea_3'], curr['avance_3']),
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
                    c_info, c_btn = st.columns([5, 1])
                    c_info.markdown(f"""
                        <div style="background:white;border:1px solid #E8E8E8;border-left:3px solid #C8102E;
                                    border-radius:3px;padding:0.7rem 1rem;margin-bottom:0.5rem;">
                            <p style="font-family:'DM Sans',sans-serif;font-size:0.7rem;font-weight:600;
                                      letter-spacing:0.1em;text-transform:uppercase;color:#5A5A5A;margin:0;">
                                {col_t.replace('_', ' ').upper()}</p>
                            <p style="font-family:'DM Sans',sans-serif;font-size:0.95rem;color:#0A0A0A;
                                      margin:0.1rem 0 0 0;">{nombre_t}
                                <span style="color:#C8102E;font-weight:600;margin-left:0.5rem;">{avance_t}%</span>
                            </p>
                        </div>
                    """, unsafe_allow_html=True)
                    if c_btn.button("BORRAR", key=f"del_{col_t}_{opc[sel]}"):
                        db_query(
                            f"UPDATE bitacora SET {col_t}='-', {col_a}=0, {col_fi}=NULL, {col_m}='-' WHERE id=%s",
                            (opc[sel],)
                        )
                        st.warning(f"Actividad eliminada: {nombre_t}")
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
