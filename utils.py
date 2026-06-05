import streamlit as st
from datetime import datetime, timezone, timedelta
from db import db_query

AZ_TZ = timezone(timedelta(hours=-7))

def now_az():
    return datetime.now(AZ_TZ).replace(tzinfo=None)

def asegurar_valor_en_lista(lista, valor):
    valor = str(valor).strip().upper() if valor else "-"
    opciones = list(lista)
    if valor not in opciones: opciones.append(valor)
    return opciones, opciones.index(valor)

def cerrar_actividades_completadas(tid, nombre, fi1, fi2, fi3, fi4, fi5,
                                   t1, a1, m1, t2, a2, m2, t3, a3, m3, t4, a4, m4, t5, a5, m5):
    tareas   = [t1,t2,t3,t4,t5]
    avances  = [a1,a2,a3,a4,a5]
    fi_list  = [fi1,fi2,fi3,fi4,fi5]
    maquinas = [m1,m2,m3,m4,m5]
    slots    = [("tarea_1","avance_1","fecha_inicio_1","maquina_1"),
                ("tarea_2","avance_2","fecha_inicio_2","maquina_2"),
                ("tarea_3","avance_3","fecha_inicio_3","maquina_3"),
                ("tarea_4","avance_4","fecha_inicio_4","maquina_4"),
                ("tarea_5","avance_5","fecha_inicio_5","maquina_5")]
    cerradas = []
    hoy = now_az().date()
    for i, (t, a, fi, m) in enumerate(zip(tareas, avances, fi_list, maquinas)):
        if t and t != '-' and a == 100:
            try:
                fi_d = fi if hasattr(fi, 'year') else datetime.strptime(str(fi),'%Y-%m-%d').date()
            except ValueError:
                fi_d = hoy
            mc = str(m).strip().upper() if m else '-'
            db_query("INSERT INTO bitacora_completados (nombre,tarea,maquina,fecha_inicio,fecha_cierre,dias_duracion) VALUES (%s,%s,%s,%s,%s,%s)",
                     (nombre, t, mc, fi_d, hoy, (hoy-fi_d).days))
            ct,ca,cfi,cm = slots[i]
            db_query(f"UPDATE bitacora SET {ct}='-',{ca}=0,{cfi}=NULL,{cm}='-' WHERE id=%s", (tid,))
            cerradas.append(t)
    return cerradas

def _limpiar_estado_form_editar(wid, version):
    for i in range(1, 6):
        for k in [f'ti{i}_{wid}_v{version}', f'mi{i}_{wid}_v{version}', f'ai{i}_{wid}_v{version}']:
            if k in st.session_state:
                del st.session_state[k]