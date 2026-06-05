import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import html
import time
from datetime import datetime

from config import R, NEG, INK, GRI, GRL, FON, BLA, VER, AMA, PEL, FH, FB, TASK_COLORS
from db import db_query, obtener_lista_maquinas
from utils import now_az, asegurar_valor_en_lista, cerrar_actividades_completadas
from components import page_header, metric_card, section_title

def render_dashboard():
    page_header("Dashboard Analitico", "Estado operativo del personal y equipos")
    
    # 1. Menú superior restaurado a su ancho completo
    vista = st.radio("Vistas del Dashboard", ["Vision General","Top Maquinas","Top Trabajadores","Control Herramientas","Taller", "Rendimiento Diesel"],
                     horizontal=True, label_visibility="collapsed")
                     
    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

    if vista == "Vision General":
        data = db_query("SELECT * FROM bitacora", fetch=True)
        if data:
            df = pd.DataFrame(data)
            df['ID_TRAB'] = df['id'].apply(lambda x: f"TRAB-{x:03d}")
            avances_prom = []
            for _, row in df.iterrows():
                vals = [row.get(f'avance_{i}', 0) for i in range(1,6)]
                act  = [v for v in vals if pd.notna(v) and v > 0]
                avances_prom.append(sum(act)/len(act) if act else 0)
            prom_g = sum(avances_prom)/len(avances_prom) if avances_prom else 0
            rc = db_query("SELECT COUNT(*) as cnt FROM bitacora_completados", fetch=True)
            total_cerradas = rc[0]['cnt'] if rc else 0

            c1, c2, c3 = st.columns(3)
            metric_card(c1, "Total Personal", str(len(df)))
            metric_card(c2, "Avance Promedio", f"{prom_g:.1f}%")
            metric_card(c3, "Actividades Cerradas", str(total_cerradas))

            section_title("Registro Completo", "Todos los trabajadores activos en el sistema")
            cols_ord = ['ID_TRAB','nombre','fecha',
                        'tarea_1','maquina_1','avance_1','fecha_inicio_1',
                        'tarea_2','maquina_2','avance_2','fecha_inicio_2',
                        'tarea_3','maquina_3','avance_3','fecha_inicio_3',
                        'tarea_4','maquina_4','avance_4','fecha_inicio_4',
                        'tarea_5','maquina_5','avance_5','fecha_inicio_5']
            st.dataframe(df[[c for c in cols_ord if c in df.columns]], use_container_width=True, hide_index=True)

            # 2. Botón movido y alineado junto al título
            c_title, c_btn = st.columns([8, 2])
            with c_title:
                section_title("Avance por Trabajador", "Progreso individual de actividades activas")
            with c_btn:
                st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)
                if st.button("ACTUALIZAR DATOS", use_container_width=True):
                    st.rerun()

            hoy  = now_az().date()

            def dias_desde(fi):
                if not fi or (isinstance(fi, float) and pd.isna(fi)): return 0
                fi_d = fi if hasattr(fi, 'year') else datetime.strptime(str(fi), '%Y-%m-%d').date()
                return (hoy - fi_d).days

            grid = st.columns(3)
            for i, (_, row) in enumerate(df.iterrows()):
                col      = grid[i % 3]
                tareas   = [row.get(f'tarea_{j}')        for j in range(1,6)]
                avs      = [row.get(f'avance_{j}', 0)    for j in range(1,6)]
                fechas   = [row.get(f'fecha_inicio_{j}') for j in range(1,6)]
                maquinas = [row.get(f'maquina_{j}', '-') for j in range(1,6)]

                bars_html  = ""
                chart_lbs  = []
                chart_vals = []
                chart_clrs = []
                hay_activa = False

                for j, (t, a, fi, m) in enumerate(zip(tareas, avs, fechas, maquinas)):
                    if pd.notna(t) and t and t != '-':
                        hay_activa = True
                        d    = dias_desde(fi)
                        ts   = html.escape(str(t)[:26])
                        ms   = html.escape(str(m)) if m and m != '-' else ""
                        av   = int(a) if pd.notna(a) and a is not None else 0
                        bc   = VER if av==100 else (AMA if av>=60 else R)
                        mxt  = f'<span style="color:{GRI};font-size:0.68rem;"> &middot; {ms}</span>' if ms else ""
                        chart_lbs.append(ts); chart_vals.append(av); chart_clrs.append(TASK_COLORS[j])
                        bars_html += f"""
                            <div style="padding:0.5rem 0;border-bottom:1px solid #F2F2F4;">
                                <div style="display:flex;justify-content:space-between;
                                            align-items:flex-start;margin-bottom:0.32rem;">
                                    <span style="font-family:{FB};font-size:0.78rem;color:{INK};
                                                 flex:1;line-height:1.4;font-weight:500;">{ts}{mxt}</span>
                                    <span style="font-family:{FB};font-size:0.7rem;color:{GRI};
                                                 margin-left:0.6rem;white-space:nowrap;font-weight:500;">{d}d</span>
                                </div>
                                <div style="display:flex;align-items:center;gap:0.5rem;">
                                    <div style="flex:1;height:4px;background:#EBEBED;border-radius:2px;overflow:hidden;">
                                        <div style="width:{av}%;height:100%;background:{bc};border-radius:2px;"></div>
                                    </div>
                                    <span style="font-family:{FB};font-size:0.68rem;font-weight:700;
                                                 color:{bc};min-width:2rem;text-align:right;">{av}%</span>
                                </div>
                            </div>"""

                nombre_s = html.escape(str(row['nombre']))
                id_s     = html.escape(str(row['ID_TRAB']))

                with col:
                    if not hay_activa:
                        st.markdown(f"""
                            <div style="background:{BLA};border:1px solid {GRL};border-radius:8px;
                                        padding:1.3rem 1.3rem;margin-bottom:1rem;box-shadow:0 1px 4px rgba(0,0,0,0.05);">
                                <p style="font-family:{FB};font-size:0.6rem;font-weight:700;letter-spacing:0.14em;
                                          text-transform:uppercase;color:{GRI};margin:0 0 0.25rem 0;">{id_s}</p>
                                <p style="font-family:{FB};font-size:1rem;font-weight:700;color:{INK};
                                          margin:0 0 0.9rem 0;letter-spacing:-0.01em;">{nombre_s}</p>
                                <div style="display:flex;align-items:center;gap:0.5rem;">
                                    <div style="width:6px;height:6px;border-radius:50%;background:{GRL};"></div>
                                    <span style="font-family:{FB};font-size:0.76rem;color:{GRI};">Sin actividades activas</span>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                            <div style="background:{BLA};border:1px solid {GRL};border-top:2px solid {R};
                                        border-radius:8px 8px 0 0;padding:1.1rem 1.3rem 0.6rem 1.3rem;
                                        box-shadow:0 1px 4px rgba(0,0,0,0.05);">
                                <p style="font-family:{FB};font-size:0.6rem;font-weight:700;letter-spacing:0.14em;
                                          text-transform:uppercase;color:{GRI};margin:0 0 0.2rem 0;">{id_s}</p>
                                <p style="font-family:{FB};font-size:1rem;font-weight:700;color:{INK};
                                          margin:0;letter-spacing:-0.01em;">{nombre_s}</p>
                            </div>
                        """, unsafe_allow_html=True)

                        if chart_vals:
                            lv = list(chart_lbs); vv = list(chart_vals); cv = list(chart_clrs)
                            lv.reverse(); vv.reverse(); cv.reverse()
                            fig = go.Figure(go.Bar(
                                x=vv, y=lv, orientation='h',
                                marker=dict(color=cv, line=dict(color='rgba(0,0,0,0)', width=0)),
                                text=[f"{v}%" for v in vv], textposition='auto',
                                textfont=dict(size=11, color='white', family='Inter'),
                                hovertemplate='<b>%{y}</b>: %{x}%<extra></extra>'
                            ))
                            fig.update_layout(
                                paper_bgcolor=BLA, plot_bgcolor=BLA,
                                margin=dict(t=4,b=4,l=6,r=6),
                                height=max(100, len(vv)*40),
                                xaxis=dict(range=[0,100],showgrid=False,zeroline=False,visible=False),
                                yaxis=dict(showgrid=False,zeroline=False,
                                           tickfont=dict(family='Inter',color=INK,size=10)),
                                showlegend=False
                            )
                            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

                        st.markdown(f"""
                            <div style="background:{BLA};border:1px solid {GRL};border-top:none;
                                        border-radius:0 0 8px 8px;padding:0.3rem 1.3rem 1rem 1.3rem;
                                        margin-bottom:1rem;box-shadow:0 1px 4px rgba(0,0,0,0.05);">
                                <p style="font-family:{FB};font-size:0.6rem;font-weight:700;letter-spacing:0.14em;
                                          text-transform:uppercase;color:{GRI};margin:0.5rem 0 0.3rem 0;">
                                    Progreso</p>
                                {bars_html}
                            </div>
                        """, unsafe_allow_html=True)

                if (i+1) % 3 == 0 and i+1 < len(df):
                    grid = st.columns(3)
        else:
            st.info("No hay registros disponibles.")

    elif vista == "Top Maquinas":
        page_header("Top Maquinas", "Equipos con mayor cantidad de servicios completados")
        data_c = db_query("""
            SELECT maquina, nombre as Empleado, tarea as Actividad,
                   fecha_inicio as `Fecha Inicio`, fecha_cierre as `Fecha Cierre`, dias_duracion as Dias
            FROM bitacora_completados WHERE maquina!='-' AND maquina IS NOT NULL
        """, fetch=True)
        if data_c:
            df_c = pd.DataFrame(data_c)
            df_c['maq'] = df_c['maquina'].astype(str).str.upper().str.strip()
            df_t = df_c.groupby('maq').size().reset_index(name='total').sort_values('total', ascending=False).head(10)
            xn, yn = df_t['maq'].tolist(), df_t['total'].tolist()
            fig = go.Figure(go.Bar(
                x=xn, y=yn, marker_color=R,
                text=[str(v) for v in yn], textposition='outside',
                textfont=dict(size=13, family='Inter', color=INK)
            ))
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(title="Maquina", type='category', categoryorder='array', categoryarray=xn,
                           tickfont=dict(family='Inter', size=11, color=INK)),
                yaxis=dict(title="Servicios", tickmode='linear', tick0=0, dtick=1,
                           rangemode='tozero', showgrid=True, gridcolor='#F0F0F0',
                           tickfont=dict(family='Inter', size=11, color=INK)),
                height=420, margin=dict(t=20, b=20, l=20, r=20)
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            section_title("Historial por Maquina")
            maq_sel = st.selectbox("Selecciona una maquina:", xn)
            if maq_sel:
                det = df_c[df_c['maq']==maq_sel][['Empleado','Actividad','Fecha Inicio','Fecha Cierre','Dias']]
                st.markdown(f"<p style='font-size:0.8rem;color:{GRI};margin-bottom:0.5rem;'><b>{len(det)}</b> registro(s) encontrado(s).</p>", unsafe_allow_html=True)
                st.dataframe(det, use_container_width=True, hide_index=True)
        else:
            st.info("Aun no hay suficientes servicios completados para este analisis.")

    elif vista == "Top Trabajadores":
        page_header("Top Trabajadores", "Personal con mayor cantidad de tareas completadas")
        data_t = db_query("""
            SELECT nombre as Empleado, maquina as Maquina, tarea as Actividad,
                   fecha_inicio as `Fecha Inicio`, fecha_cierre as `Fecha Cierre`, dias_duracion as Dias
            FROM bitacora_completados
        """, fetch=True)
        if data_t:
            df_t = pd.DataFrame(data_t)
            df_t['emp'] = df_t['Empleado'].astype(str).str.strip()
            df_top = df_t.groupby('emp').size().reset_index(name='total').sort_values('total', ascending=False).head(10)
            xt, yt = df_top['emp'].tolist(), df_top['total'].tolist()
            fig = go.Figure(go.Bar(
                x=xt, y=yt, marker_color=R,
                text=[str(v) for v in yt], textposition='outside',
                textfont=dict(size=13, family='Inter', color=INK)
            ))
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(title="Trabajador", type='category', categoryorder='array', categoryarray=xt,
                           tickfont=dict(family='Inter', size=11, color=INK)),
                yaxis=dict(title="Tareas", tickmode='linear', tick0=0, dtick=1,
                           rangemode='tozero', showgrid=True, gridcolor='#F0F0F0',
                           tickfont=dict(family='Inter', size=11, color=INK)),
                height=420, margin=dict(t=20, b=20, l=20, r=20)
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            section_title("Historial por Trabajador")
            tr_sel = st.selectbox("Selecciona un trabajador:", xt)
            if tr_sel:
                det = df_t[df_t['emp']==tr_sel][['Actividad','Maquina','Fecha Inicio','Fecha Cierre','Dias']]
                st.markdown(f"<p style='font-size:0.8rem;color:{GRI};margin-bottom:0.5rem;'><b>{len(det)}</b> registro(s) encontrado(s).</p>", unsafe_allow_html=True)
                st.dataframe(det, use_container_width=True, hide_index=True)
        else:
            st.info("Aun no hay tareas completadas suficientes para este analisis.")

    elif vista == "Control Herramientas":
        page_header("Control de Herramientas", "Registro de salidas y devoluciones del almacen")
        rt = db_query("SELECT nombre FROM bitacora ORDER BY nombre ASC", fetch=True)
        lista_trab = [r['nombre'] for r in rt] if rt else []
        with st.form("form_herramienta"):
            c1, c2, c3 = st.columns(3)
            trab_h = c1.selectbox("Trabajador", lista_trab if lista_trab else ["Sin trabajadores"])
            herr   = c2.text_input("Herramienta", placeholder="")
            tarea  = c3.text_input("Tarea / Motivo", placeholder="Opcional")
            st.markdown("<div style='height:0.3rem'></div>", unsafe_allow_html=True)
            if st.form_submit_button("REGISTRAR SALIDA", use_container_width=True):
                if not lista_trab:
                    st.error("Primero da de alta trabajadores en el sistema.")
                elif not herr.strip():
                    st.error("El nombre de la herramienta es obligatorio.")
                else:
                    db_query("INSERT INTO prestamo_herramientas (trabajador,herramienta,tarea,fecha_prestamo,estado) VALUES (%s,%s,%s,%s,'Prestado')",
                             (trab_h, herr.strip(), tarea.strip() or "Sin especificar", now_az()))
                    st.success(f"Herramienta registrada: {herr.strip()} entregada a {trab_h}.")
                    time.sleep(0.7); st.rerun()

        section_title("Herramientas en Uso", "Pendientes de devolucion al almacen")
        prestadas = db_query("SELECT * FROM prestamo_herramientas WHERE estado='Prestado' ORDER BY fecha_prestamo DESC", fetch=True)
        if prestadas:
            for row in prestadas:
                fecha_s = row['fecha_prestamo'].strftime("%d/%m/%Y %H:%M") if isinstance(row['fecha_prestamo'], datetime) else str(row['fecha_prestamo'])
                hs = html.escape(str(row['herramienta']))
                ts = html.escape(str(row['trabajador']))
                ps = html.escape(str(row['tarea']))
                ci, cb = st.columns([5, 1])
                ci.markdown(f"""
                    <div style="background:{BLA};border:1px solid {GRL};border-left:3px solid {AMA};
                                border-radius:8px;padding:1rem 1.3rem;margin-bottom:0.5rem;
                                box-shadow:0 1px 4px rgba(0,0,0,0.05);">
                        <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:0.5rem;">
                            <div>
                                <p style="font-family:{FB};font-size:0.6rem;font-weight:700;letter-spacing:0.14em;
                                          text-transform:uppercase;color:{GRI};margin:0 0 0.2rem 0;">En uso &middot; {ts}</p>
                                <p style="font-family:{FB};font-size:0.95rem;font-weight:700;color:{INK};margin:0;">
                                    {hs}<span style="font-weight:400;color:{GRI};font-size:0.84rem;"> &mdash; {ps}</span>
                                </p>
                            </div>
                            <span style="font-family:{FB};font-size:0.72rem;color:{AMA};font-weight:600;">{fecha_s}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                with cb:
                    st.markdown("<div style='margin-top:0.6rem'></div>", unsafe_allow_html=True)
                    if st.button("DEVOLVER", key=f"dev_{row['id']}", use_container_width=True):
                        db_query("UPDATE prestamo_herramientas SET estado='Devuelto',fecha_devolucion=%s WHERE id=%s",
                                 (now_az(), row['id']))
                        st.success(f"{hs} devuelta al almacen.")
                        time.sleep(0.6); st.rerun()
        else:
            st.info("No hay herramientas prestadas actualmente.")

        section_title("Historial de Devoluciones")
        dev = db_query("""
            SELECT trabajador as Trabajador, herramienta as Herramienta, tarea as Tarea,
                   fecha_prestamo as `Fecha Salida`, fecha_devolucion as `Fecha Entrega`
            FROM prestamo_herramientas WHERE estado='Devuelto' ORDER BY fecha_devolucion DESC LIMIT 100
        """, fetch=True)
        if dev: st.dataframe(pd.DataFrame(dev), use_container_width=True, hide_index=True)
        else:   st.info("Sin historial de devoluciones aun.")

    elif vista == "Taller":
        page_header("Gestion de Taller", "Equipos en reparacion y control de ingresos")
        lm   = obtener_lista_maquinas()
        lm_c = [m for m in lm if m != '-']
        with st.form("form_taller"):
            c1, c2 = st.columns([1, 2])
            maq_t  = c1.selectbox("Maquina", lm_c if lm_c else ["Sin maquinas"])
            mot_t  = c2.text_input("Falla reportada / Motivo de ingreso")
            st.markdown("<div style='height:0.3rem'></div>", unsafe_allow_html=True)
            if st.form_submit_button("REGISTRAR INGRESO A TALLER", use_container_width=True):
                if not lm_c:
                    st.error("Primero da de alta maquinas en el sistema.")
                elif not mot_t.strip():
                    st.error("Debes especificar la falla o motivo de ingreso.")
                else:
                    db_query("INSERT INTO taller (maquina,motivo,fecha_ingreso,estado) VALUES (%s,%s,%s,'En Taller')",
                             (maq_t, mot_t.strip(), now_az()))
                    st.success(f"Maquina {maq_t} ingresada al taller.")
                    time.sleep(0.7); st.rerun()

        section_title("Equipos en Taller", "Maquinas actualmente fuera de servicio")
        en_t  = db_query("SELECT * FROM taller WHERE estado='En Taller' ORDER BY fecha_ingreso DESC", fetch=True)
        bita  = db_query("SELECT * FROM bitacora", fetch=True)
        ahora = now_az()

        if en_t:
            for row in en_t:
                dias_t  = (ahora - row['fecha_ingreso']).days
                dias_s  = "Ingreso hoy" if dias_t==0 else (f"1 dia en taller" if dias_t==1 else f"{dias_t} dias en taller")
                bc      = PEL if dias_t>7 else (AMA if dias_t>3 else GRI)
                maq_s   = html.escape(str(row['maquina']))
                mot_s   = html.escape(str(row['motivo']))
                act_html = ""
                if bita:
                    procs = []
                    for rb in bita:
                        for i in range(1,6):
                            bm = str(rb.get(f'maquina_{i}','')).strip().upper()
                            bt = rb.get(f'tarea_{i}')
                            if bm == maq_s and bt and bt != '-':
                                procs.append({'trab': rb['nombre'], 'tarea': bt, 'av': rb.get(f'avance_{i}',0)})
                    if procs:
                        act_html = f"<div style='margin-top:0.8rem;padding-top:0.8rem;border-top:1px solid #F0F0F2;'>"
                        act_html += f"<p style='font-family:{FB};font-size:0.6rem;font-weight:700;letter-spacing:0.14em;text-transform:uppercase;color:{GRI};margin:0 0 0.4rem 0;'>Actividades en proceso</p>"
                        for p in procs:
                            act_html += f"<p style='font-family:{FB};font-size:0.82rem;color:{INK};margin:0.15rem 0;font-weight:500;'>&middot; {html.escape(str(p['trab']))} &mdash; {html.escape(str(p['tarea']))} <span style='color:{R};font-weight:700;'>({p['av']}%)</span></p>"
                        act_html += "</div>"
                    else:
                        act_html = f"<div style='margin-top:0.8rem;padding-top:0.8rem;border-top:1px solid #F0F0F2;'><p style='font-family:{FB};font-size:0.78rem;color:{GRL};font-style:italic;margin:0;'>Sin actividades activas asignadas.</p></div>"
                ci, cb = st.columns([5, 1])
                ci.markdown(f"""
                    <div style="background:{BLA};border:1px solid {GRL};border-left:3px solid {PEL};
                                border-radius:8px;padding:1.1rem 1.3rem;margin-bottom:0.6rem;
                                box-shadow:0 1px 4px rgba(0,0,0,0.05);">
                        <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:0.5rem;margin-bottom:0.3rem;">
                            <p style="font-family:{FB};font-size:1.05rem;font-weight:700;color:{INK};margin:0;letter-spacing:-0.01em;">{maq_s}</p>
                            <span style="background:{bc};color:{BLA};padding:3px 12px;border-radius:20px;
                                         font-family:{FB};font-size:0.68rem;font-weight:700;letter-spacing:0.04em;">{dias_s}</span>
                        </div>
                        <p style="font-family:{FB};font-size:0.84rem;color:{GRI};margin:0;">
                            <span style="font-weight:600;color:{INK};">Reporte:</span> {mot_s}
                        </p>
                        {act_html}
                    </div>
                """, unsafe_allow_html=True)
                with cb:
                    st.markdown("<div style='margin-top:1.2rem'></div>", unsafe_allow_html=True)
                    if st.button("REPARADA", key=f"rep_{row['id']}", use_container_width=True):
                        db_query("UPDATE taller SET estado='Reparado',fecha_salida=%s WHERE id=%s",
                                 (now_az(), row['id']))
                        st.success(f"{maq_s} dada de alta del taller.")
                        time.sleep(0.6); st.rerun()
        else:
            st.info("Todas las maquinas estan operativas. No hay equipos en taller.")

        section_title("Historial de Reparaciones")
        rep = db_query("""
            SELECT maquina as Maquina, motivo as Falla,
                   fecha_ingreso as Ingreso, fecha_salida as Alta
            FROM taller WHERE estado='Reparado' ORDER BY fecha_salida DESC LIMIT 100
        """, fetch=True)
        if rep:
            df_r = pd.DataFrame(rep)
            df_r['Dias en Taller'] = (pd.to_datetime(df_r['Alta']) - pd.to_datetime(df_r['Ingreso'])).dt.days
            st.dataframe(df_r, use_container_width=True, hide_index=True)
        else:
            st.info("Sin historial de reparaciones aun.")

    elif vista == "Rendimiento Diesel":
        page_header("Rendimiento de Diesel", "Analitica de consumo y eficiencia de combustible")
        
        # Pega el src/iframe de tu reporte de Power BI en el atributo src
        st.markdown(f"""
            <div style="background:{BLA}; border:1px solid {GRL}; border-radius:8px; padding:0.5rem; box-shadow:0 1px 4px rgba(0,0,0,0.05);">
                <iframe title="Dashboard Rendimiento Diesel" 
                        width="100%" 
                        height="700" 
                        src="Pendiente Iframe de power bi" 
                        frameborder="0" 
                        allowFullScreen="true">
                </iframe>
            </div>
        """, unsafe_allow_html=True)

def render_alta_trabajador():
    page_header("Alta de Trabajador", "Registra nuevo personal en el sistema")
    with st.form("alta_trabajador"):
        nom = st.text_input("Nombre Completo", placeholder="Ej. Juan Garcia Lopez")
        st.markdown("<div style='height:0.3rem'></div>", unsafe_allow_html=True)
        if st.form_submit_button("REGISTRAR TRABAJADOR", use_container_width=True):
            if nom.strip():
                db_query("INSERT INTO bitacora (nombre,fecha) VALUES (%s,%s)", (nom.strip(), now_az().date()))
                st.success(f"Trabajador registrado: {nom.strip()}")
                time.sleep(0.7); st.rerun()
            else:
                st.error("El nombre no puede estar vacio.")

def render_alta_maquina():
    page_header("Alta de Maquina", "Agrega un nuevo equipo al catalogo del sistema")
    with st.form("alta_maquina"):
        nom_m = st.text_input("Nombre de la Maquina", placeholder="Ej. EXCAVADORA CAT 320")
        st.markdown("<div style='height:0.3rem'></div>", unsafe_allow_html=True)
        if st.form_submit_button("REGISTRAR MAQUINA", use_container_width=True):
            if nom_m.strip():
                try:
                    import mysql.connector
                    db_query("INSERT INTO maquinas (nombre) VALUES (%s)", (nom_m.strip().upper(),))
                    st.success(f"Maquina registrada: {nom_m.strip().upper()}")
                    time.sleep(0.7); st.rerun()
                except mysql.connector.IntegrityError:
                    st.error("Esta maquina ya se encuentra registrada.")
            else:
                st.error("El nombre no puede estar vacio.")

def render_asignar_tarea():
    page_header("Asignar Tarea", "Asigna nuevas actividades al personal activo")
    res = db_query("SELECT * FROM bitacora", fetch=True)
    lm  = obtener_lista_maquinas()
    if res:
        opc = {f"{r['nombre']}  -  TRAB-{r['id']:03d}": r for r in res}
        with st.form("asignar_tarea"):
            sel = st.selectbox("Trabajador", list(opc.keys()))
            c1, c2 = st.columns([2, 1])
            tar = c1.text_input("Descripcion de la Tarea", placeholder="Ej. Mantenimiento preventivo motor")
            maq = c2.selectbox("Maquina (Opcional)", lm)
            st.markdown("<div style='height:0.3rem'></div>", unsafe_allow_html=True)
            if st.form_submit_button("ASIGNAR TAREA", use_container_width=True):
                if tar.strip():
                    curr = opc[sel]
                    hoy  = now_az().date()
                    vm   = maq.strip().upper() if maq else '-'
                    asig = False
                    for i in range(1, 6):
                        if curr.get(f'tarea_{i}') in (None, '-', ''):
                            db_query(f"UPDATE bitacora SET tarea_{i}=%s,maquina_{i}=%s,avance_{i}=0,fecha_inicio_{i}=%s WHERE id=%s",
                                     (tar.strip(), vm, hoy, curr['id']))
                            st.success(f"Tarea asignada en el espacio {i}.")
                            asig = True; time.sleep(0.6); st.rerun(); break
                    if not asig:
                        st.error("El trabajador ya tiene 5 tareas activas. Cierra una antes de asignar otra.")
                else:
                    st.error("La descripcion de la tarea no puede estar vacia.")
    else:
        st.info("Primero da de alta un trabajador en 'Alta de Trabajador'.")

def render_editar_avances():
    page_header("Editar Avances", "Actualiza el progreso de las actividades por trabajador")

    if 'edit_form_v' not in st.session_state:
        st.session_state['edit_form_v'] = 0

    res = db_query("SELECT * FROM bitacora", fetch=True)
    lm  = obtener_lista_maquinas()
    if res:
        opc  = {r['nombre']: r for r in res}
        sel  = st.selectbox("Trabajador", list(opc.keys()))
        curr = opc[sel]
        wid  = curr['id']
        form_v = st.session_state['edit_form_v']

        st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
        with st.form(f"upd_{wid}_{form_v}"):
            inputs = {}
            for i in range(1, 6):
                st.markdown(f"""
                    <div style="background:{FON};border:1px solid {GRL};border-left:2px solid {R};
                                border-radius:6px;padding:0.55rem 1rem 0.15rem 1rem;margin-bottom:0.5rem;">
                        <p style="font-family:{FB};font-size:0.6rem;font-weight:700;letter-spacing:0.14em;
                                  text-transform:uppercase;color:{GRI};margin:0;">Espacio {i}</p>
                    </div>
                """, unsafe_allow_html=True)
                ca, cb, cc = st.columns([2, 2, 1])
                opts, ix = asegurar_valor_en_lista(lm, curr.get(f'maquina_{i}', '-'))
                inputs[f't{i}'] = ca.text_input(f"Tarea {i}",    value=curr.get(f'tarea_{i}', '-'),   key=f'ti{i}_{wid}_v{form_v}')
                inputs[f'm{i}'] = cb.selectbox(f"Maquina {i}",   opts, index=ix,                      key=f'mi{i}_{wid}_v{form_v}')
                inputs[f'a{i}'] = cc.number_input(f"Avance {i}%", 0, 100, int(curr.get(f'avance_{i}', 0) or 0), step=5, key=f'ai{i}_{wid}_v{form_v}')

            t1,t2,t3,t4,t5 = inputs['t1'],inputs['t2'],inputs['t3'],inputs['t4'],inputs['t5']
            m1,m2,m3,m4,m5 = inputs['m1'],inputs['m2'],inputs['m3'],inputs['m4'],inputs['m5']
            a1,a2,a3,a4,a5 = inputs['a1'],inputs['a2'],inputs['a3'],inputs['a4'],inputs['a5']

            st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)
            if st.form_submit_button("GUARDAR CAMBIOS", use_container_width=True):
                hoy    = now_az().date()
                prev   = [(curr.get(f'tarea_{i}'), curr.get(f'fecha_inicio_{i}')) for i in range(1,6)]
                fi     = [curr.get(f'fecha_inicio_{i}') for i in range(1,6)]
                for idx, (nt, (pt, _)) in enumerate(zip([t1,t2,t3,t4,t5], prev)):
                    if nt and nt != '-' and (not pt or pt == '-'):
                        fi[idx] = hoy
                fi1,fi2,fi3,fi4,fi5 = fi
                def mc(v): return v.strip().upper() if v else '-'
                db_query("""UPDATE bitacora SET
                    tarea_1=%s,avance_1=%s,fecha_inicio_1=%s,maquina_1=%s,
                    tarea_2=%s,avance_2=%s,fecha_inicio_2=%s,maquina_2=%s,
                    tarea_3=%s,avance_3=%s,fecha_inicio_3=%s,maquina_3=%s,
                    tarea_4=%s,avance_4=%s,fecha_inicio_4=%s,maquina_4=%s,
                    tarea_5=%s,avance_5=%s,fecha_inicio_5=%s,maquina_5=%s WHERE id=%s""",
                    (t1,a1,fi1,mc(m1),t2,a2,fi2,mc(m2),t3,a3,fi3,mc(m3),
                     t4,a4,fi4,mc(m4),t5,a5,fi5,mc(m5),curr['id']))
                cerradas = cerrar_actividades_completadas(
                    curr['id'],sel,fi1,fi2,fi3,fi4,fi5,
                    t1,a1,mc(m1),t2,a2,mc(m2),t3,a3,mc(m3),t4,a4,mc(m4),t5,a5,mc(m5))
                if cerradas:
                    for c in cerradas:
                        st.success(f"Actividad cerrada y enviada a Bitacora: {c}")
                    st.session_state['edit_form_v'] += 1
                else:
                    st.success("Registro actualizado correctamente.")
                time.sleep(0.6)
                st.rerun()

        curr_fresh = db_query("SELECT * FROM bitacora WHERE id=%s", (wid,), fetch=True)
        curr_fresh = curr_fresh[0] if curr_fresh else curr

        acts    = [(f"tarea_{i}",f"avance_{i}",f"fecha_inicio_{i}",f"maquina_{i}",
                    curr_fresh.get(f'tarea_{i}','-'), curr_fresh.get(f'avance_{i}',0)) for i in range(1,6)]
        activas = [(ct,ca,cfi,cm,t,a) for ct,ca,cfi,cm,t,a in acts if t and t != '-']

        if activas:
            st.markdown(f"""
                <div style="margin-top:2.5rem;padding-top:1.5rem;border-top:1px solid {GRL};">
                    <h2 style="margin:0 0 0.25rem 0;">Eliminar Actividad</h2>
                    <p style="font-family:{FB};font-size:0.8rem;color:{GRI};margin:0 0 1rem 0;">
                        Elimina una actividad por error. Esta accion no se puede deshacer.
                    </p>
                </div>
            """, unsafe_allow_html=True)
            for ct,ca,cfi,cm,nom_t,av_t in activas:
                ns   = html.escape(str(nom_t))
                aclr = VER if av_t==100 else (AMA if av_t>=60 else R)
                ci, cb = st.columns([5, 1])
                ci.markdown(f"""
                    <div style="background:{BLA};border:1px solid {GRL};border-left:2px solid {R};
                                border-radius:8px;padding:0.85rem 1.2rem;margin-bottom:0.5rem;
                                box-shadow:0 1px 3px rgba(0,0,0,0.04);">
                        <p style="font-family:{FB};font-size:0.6rem;font-weight:700;letter-spacing:0.14em;
                                  text-transform:uppercase;color:{GRI};margin:0 0 0.15rem 0;">
                            {ct.replace('_',' ').upper()}</p>
                        <p style="font-family:{FB};font-size:0.92rem;font-weight:600;color:{INK};margin:0;">
                            {ns}<span style="color:{aclr};font-weight:700;margin-left:0.5rem;">{av_t}%</span>
                        </p>
                    </div>
                """, unsafe_allow_html=True)
                with cb:
                    st.markdown("<div style='margin-top:0.45rem'></div>", unsafe_allow_html=True)
                    if st.button("BORRAR", key=f"del_{ct}_{curr['id']}_v{form_v}", use_container_width=True):
                        db_query(f"UPDATE bitacora SET {ct}='-',{ca}=0,{cfi}=NULL,{cm}='-' WHERE id=%s", (curr['id'],))
                        st.warning(f"Actividad eliminada: {ns}")
                        st.session_state['edit_form_v'] += 1
                        time.sleep(0.6)
                        st.rerun()

def render_bitacora():
    page_header("Bitacora de Actividades", "Historial completo de todas las tareas cerradas al 100%")
    data = db_query("SELECT * FROM bitacora_completados ORDER BY fecha_cierre DESC", fetch=True)
    if data:
        df_b = pd.DataFrame(data)
        df_b.rename(columns={'nombre':'Empleado','tarea':'Actividad','maquina':'Maquina',
                             'fecha_inicio':'Fecha Inicio','fecha_cierre':'Fecha Cierre',
                             'dias_duracion':'Dias'}, inplace=True)
        df_b.drop(columns=['id'], inplace=True)

        c1, c2, c3 = st.columns(3)
        metric_card(c1, "Total Cerradas",        str(len(df_b)))
        metric_card(c2, "Personal Participante", str(df_b['Empleado'].nunique()))
        metric_card(c3, "Ultimo Cierre",         str(df_b['Fecha Cierre'].iloc[0]))

        st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
        rt      = db_query("SELECT nombre FROM bitacora ORDER BY nombre ASC", fetch=True)
        lista_t = ["Todos"] + ([r['nombre'] for r in rt] if rt else [])
        cf1, cf2 = st.columns(2)
        fil_emp = cf1.selectbox("Filtrar por Empleado", lista_t)
        buscar  = cf2.text_input("Buscar Actividad o Maquina", placeholder="Ej. motor, excavadora...")

        if fil_emp != "Todos":
            df_b = df_b[df_b['Empleado'] == fil_emp]
        if buscar:
            df_b = df_b[df_b['Actividad'].str.contains(buscar, case=False, na=False) |
                        df_b['Maquina'].str.contains(buscar, case=False, na=False)]

        st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)
        if not df_b.empty:
            st.dataframe(df_b, use_container_width=True, hide_index=True)
        else:
            st.warning("No se encontraron registros con esos filtros.")
    else:
        st.info("No hay actividades completadas aun.")

def render_eliminar_registro():
    page_header("Eliminar Registro", "Baja permanente de un trabajador del sistema")
    res = db_query("SELECT id, nombre FROM bitacora", fetch=True)
    if res:
        opc = {r['nombre']: r['id'] for r in res}
        sel = st.selectbox("Seleccionar Trabajador a Eliminar", list(opc.keys()))
        st.markdown(f"""
            <div style="background:#FFF5F5;border:1px solid #FECACA;border-left:3px solid {PEL};
                        border-radius:8px;padding:1rem 1.3rem;margin:1.2rem 0;">
                <p style="font-family:{FB};font-size:0.84rem;color:#7F1D1D;margin:0;font-weight:500;">
                    <span style="font-weight:700;">Advertencia:</span> Estas a punto de eliminar permanentemente a
                    <span style="font-weight:700;">{html.escape(sel)}</span> junto con todos sus registros activos.
                    Esta accion no se puede deshacer.
                </p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("CONFIRMAR ELIMINACION", type="primary"):
            db_query("DELETE FROM bitacora WHERE id=%s", (opc[sel],))
            st.warning(f"Registro de '{sel}' eliminado del sistema.")
            time.sleep(1); st.rerun()
    else:
        st.info("No hay registros para eliminar.")
