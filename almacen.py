import streamlit as st
import pandas as pd
from datetime import datetime
import time

def inicializar_tablas(db_query):
    db_query("""
        CREATE TABLE IF NOT EXISTS almacen_inventario_v3 (
            clave VARCHAR(50) PRIMARY KEY,
            descripcion VARCHAR(255) NOT NULL,
            stock INT DEFAULT 0,
            orden VARCHAR(100),
            obra VARCHAR(100)
        )""")
    db_query("""
        CREATE TABLE IF NOT EXISTS almacen_movimientos_v3 (
            id INT AUTO_INCREMENT PRIMARY KEY,
            clave VARCHAR(50) NOT NULL,
            tipo VARCHAR(20) NOT NULL,
            piezas INT NOT NULL,
            fecha DATETIME NOT NULL,
            solicitante VARCHAR(100),
            maquina VARCHAR(100),
            obra VARCHAR(100),
            orden VARCHAR(100)
        )""")

def render_almacen(db_query, es_publico=False):
    inicializar_tablas(db_query)

    if "form_ent_key" not in st.session_state:
        st.session_state["form_ent_key"] = 0
        
    if "form_sal_key" not in st.session_state:
        st.session_state["form_sal_key"] = 0

    R = "#C8102E"
    GRL = "#E2E2E5"
    GRI = "#8A8A8A"
    FB = "'Inter', sans-serif"

    st.markdown(f"""
        <div style="margin-bottom:2rem;padding-bottom:1.5rem;border-bottom:1px solid {GRL};">
            <div style="display:flex;align-items:center;gap:0.8rem;">
                <div style="width:3px;height:1.8rem;background:{R};border-radius:2px;flex-shrink:0;"></div>
                <div>
                    <h1 style="font-family:{FB};font-size:1.6rem;font-weight:700;margin:0;color:#0F0F0F;line-height:1.2;">Control de Almacen</h1>
                    <p style="font-family:{FB};font-size:0.84rem;color:{GRI};margin:0.35rem 0 0 0;">{'Consulta de Inventario' if es_publico else 'Gestion de Entradas y Salidas'}</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if es_publico:
        busqueda_pub = st.text_input("Buscar producto (Clave o Descripcion)", placeholder="Ej. Martillo o HER-01")
        datos_pub = db_query("SELECT clave AS Clave, descripcion AS Descripcion, stock AS Stock, orden AS Orden, obra AS Obra FROM almacen_inventario_v3", fetch=True)
        if datos_pub:
            df_pub = pd.DataFrame(datos_pub)
            if busqueda_pub:
                df_pub = df_pub[df_pub['Clave'].str.contains(busqueda_pub, case=False, na=False) | 
                               df_pub['Descripcion'].str.contains(busqueda_pub, case=False, na=False)]
            st.dataframe(df_pub, use_container_width=True, hide_index=True)
        return

    tabs = st.tabs(["Stock Almacen", "Registro de Entrada", "Registro de Salida", "Historial"])

    with tabs[0]:
        st.markdown("### Inventario Stock en Almacen")
        buscador = st.text_input("Filtrar inventario", placeholder="Buscar por clave, descripcion, obra u orden...")
        datos_inv = db_query("SELECT clave AS Clave, descripcion AS Descripcion, stock AS Stock, orden AS Orden, obra AS Obra FROM almacen_inventario_v3 ORDER BY clave ASC", fetch=True)
        if datos_inv:
            df_inv = pd.DataFrame(datos_inv)
            if buscador:
                df_inv = df_inv[df_inv.apply(lambda row: row.astype(str).str.contains(buscador, case=False).any(), axis=1)]
            st.dataframe(df_inv, use_container_width=True, hide_index=True)
        else:
            st.info("El almacen esta vacio.")

    with tabs[1]:
        st.markdown("### Registrar Entrada de Material")
        productos_existentes = db_query("SELECT clave, descripcion FROM almacen_inventario_v3", fetch=True)
        opciones_prod = {"NUEVO PRODUCTO": None}
        if productos_existentes:
            for p in productos_existentes:
                opciones_prod[f"{p['clave']} - {p['descripcion']}"] = p

        prod_sel = st.selectbox("Seleccionar producto existente o registrar uno nuevo", 
                                list(opciones_prod.keys()), 
                                key=f"ent_prod_sel_{st.session_state['form_ent_key']}")
        
        with st.form(f"form_entrada_{st.session_state['form_ent_key']}"):
            if prod_sel == "NUEVO PRODUCTO":
                clave_ent = st.text_input("Clave del Producto (ID)")
                desc_ent = st.text_input("Descripcion del producto")
            else:
                p_data = opciones_prod[prod_sel]
                clave_ent = st.text_input("Clave del Producto (ID)", value=p_data['clave'], disabled=True)
                desc_ent = st.text_input("Descripcion del producto", value=p_data['descripcion'], disabled=True)
            
            c3, c4, c5 = st.columns(3)
            piezas_ent = c3.number_input("Piezas que entran", min_value=1, step=1)
            orden_ent = c4.text_input("Numero de Orden")
            obra_ent = c5.text_input("Obra")
            
            if st.form_submit_button("REGISTRAR ENTRADA", use_container_width=True):
                if clave_ent.strip() and desc_ent.strip():
                    existe = db_query("SELECT stock FROM almacen_inventario_v3 WHERE clave=%s", (clave_ent.strip(),), fetch=True)
                    if existe:
                        nuevo_stock = existe[0]['stock'] + piezas_ent
                        db_query("UPDATE almacen_inventario_v3 SET stock=%s, orden=%s, obra=%s WHERE clave=%s", 
                                 (nuevo_stock, orden_ent.strip(), obra_ent.strip(), clave_ent.strip()))
                    else:
                        db_query("INSERT INTO almacen_inventario_v3 (clave, descripcion, stock, orden, obra) VALUES (%s, %s, %s, %s, %s)", 
                                 (clave_ent.strip().upper(), desc_ent.strip(), piezas_ent, orden_ent.strip(), obra_ent.strip()))
                    
                    db_query("INSERT INTO almacen_movimientos_v3 (clave, tipo, piezas, fecha, obra, orden) VALUES (%s, 'Entrada', %s, %s, %s, %s)",
                             (clave_ent.strip().upper(), piezas_ent, datetime.now(), obra_ent.strip(), orden_ent.strip()))
                    
                    st.session_state["form_ent_key"] += 1
                    
                    st.success(f"Entrada registrada.")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Campos obligatorios vacios.")

    with tabs[2]:
        st.markdown("### Registrar Salida de Material")
        inventario = db_query("SELECT clave, descripcion, stock, orden FROM almacen_inventario_v3 WHERE stock > 0", fetch=True)
        trabajadores = db_query("SELECT nombre FROM bitacora ORDER BY nombre ASC", fetch=True)
        maquinas_db = db_query("SELECT nombre FROM maquinas ORDER BY nombre ASC", fetch=True)
        
        lista_trab = [t['nombre'] for t in trabajadores] if trabajadores else []
        lista_maq = [m['nombre'] for m in maquinas_db] if maquinas_db else []

        if inventario:
            dict_inv = {f"{r['clave']} - {r['descripcion']}": r for r in inventario}
            opciones_salida = ["-- Seleccione --"] + list(dict_inv.keys())

            prod_sal_sel = st.selectbox("Seleccionar Producto (ID y Descripcion)", 
                                        options=opciones_salida, 
                                        key=f"sal_prod_sel_{st.session_state['form_sal_key']}")
            
            with st.form(f"form_salida_{st.session_state['form_sal_key']}"):
                item_data = dict_inv.get(prod_sal_sel, {'clave': '', 'descripcion': '', 'orden': '', 'stock': 0})
                
                c1, c2 = st.columns(2)
                st.markdown(f"**Stock disponible:** `{item_data['stock']}`")
                st.text_input("Clave (ID)", value=item_data['clave'], disabled=True)
                st.text_input("Descripcion", value=item_data['descripcion'], disabled=True)
                st.text_input("Numero de Orden (Origen)", value=item_data['orden'], disabled=True)
                
                c3, c4 = st.columns(2)
                piezas_sal = c3.number_input("Piezas que salen", min_value=1, max_value=item_data['stock'] if item_data['stock'] > 0 else 1, step=1)
                obra_dest = c4.text_input("Obra destino")
                
                c5, c6 = st.columns(2)
                solicitante = c5.selectbox("Nombre del Solicitante", lista_trab)
                maquina_sal = c6.selectbox("Maquinaria asociada", ["-"] + lista_maq)
                
                if st.form_submit_button("REGISTRAR SALIDA", use_container_width=True):
                    if prod_sal_sel != "-- Seleccione --":
                        nuevo_stock = item_data['stock'] - piezas_sal
                        db_query("UPDATE almacen_inventario_v3 SET stock=%s WHERE clave=%s", (nuevo_stock, item_data['clave']))
                        db_query("INSERT INTO almacen_movimientos_v3 (clave, tipo, piezas, fecha, solicitante, maquina, obra, orden) VALUES (%s, 'Salida', %s, %s, %s, %s, %s, %s)",
                                 (item_data['clave'], piezas_sal, datetime.now(), solicitante, maquina_sal, obra_dest.strip(), item_data['orden']))
                        
                        st.session_state["form_sal_key"] += 1
                        
                        st.success("Salida registrada.")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Seleccione un producto.")
        else:
            st.warning("No hay productos con stock.")

    with tabs[3]:
        st.markdown("### Historial de Movimientos")
        bus_hist = st.text_input("Buscar en historial", placeholder="Clave, descripcion, solicitante, maquina, obra...")
        hist = db_query("""
            SELECT m.fecha AS Fecha, m.tipo AS Tipo, m.clave AS Clave, i.descripcion AS Descripcion, 
                   m.piezas AS Piezas, m.solicitante AS Solicitante, m.maquina AS Maquina, m.obra AS Obra, m.orden AS Orden
            FROM almacen_movimientos_v3 m
            LEFT JOIN almacen_inventario_v3 i ON m.clave = i.clave
            ORDER BY m.fecha DESC LIMIT 500
        """, fetch=True)
        if hist:
            df_hist = pd.DataFrame(hist)
            if bus_hist:
                df_hist = df_hist[df_hist.apply(lambda row: row.astype(str).str.contains(bus_hist, case=False).any(), axis=1)]
            st.dataframe(df_hist, use_container_width=True, hide_index=True)