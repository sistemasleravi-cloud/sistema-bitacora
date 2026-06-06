import streamlit as st
import mysql.connector
import bcrypt
import time

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
                    nombre VARCHAR(100) NOT NULL, fecha DATE NOT NULL,
                    tarea_1 VARCHAR(255) DEFAULT '-', avance_1 INT DEFAULT 0,
                    fecha_inicio_1 DATE DEFAULT NULL, maquina_1 VARCHAR(255) DEFAULT '-',
                    tarea_2 VARCHAR(255) DEFAULT '-', avance_2 INT DEFAULT 0,
                    fecha_inicio_2 DATE DEFAULT NULL, maquina_2 VARCHAR(255) DEFAULT '-',
                    tarea_3 VARCHAR(255) DEFAULT '-', avance_3 INT DEFAULT 0,
                    fecha_inicio_3 DATE DEFAULT NULL, maquina_3 VARCHAR(255) DEFAULT '-',
                    tarea_4 VARCHAR(255) DEFAULT '-', avance_4 INT DEFAULT 0,
                    fecha_inicio_4 DATE DEFAULT NULL, maquina_4 VARCHAR(255) DEFAULT '-',
                    tarea_5 VARCHAR(255) DEFAULT '-', avance_5 INT DEFAULT 0,
                    fecha_inicio_5 DATE DEFAULT NULL, maquina_5 VARCHAR(255) DEFAULT '-'
                )""")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bitacora_completados (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(100) NOT NULL, tarea VARCHAR(255) NOT NULL,
                    maquina VARCHAR(255) DEFAULT '-', fecha_inicio DATE NOT NULL,
                    fecha_cierre DATE NOT NULL, dias_duracion INT DEFAULT 0
                )""")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    usuario VARCHAR(50) UNIQUE NOT NULL, password_hash VARCHAR(255) NOT NULL
                )""")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS maquinas (
                    id INT AUTO_INCREMENT PRIMARY KEY, nombre VARCHAR(100) UNIQUE NOT NULL
                )""")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS prestamo_herramientas (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    trabajador VARCHAR(100) NOT NULL, herramienta VARCHAR(255) NOT NULL,
                    tarea VARCHAR(255) NOT NULL, fecha_prestamo DATETIME NOT NULL,
                    fecha_devolucion DATETIME DEFAULT NULL, estado VARCHAR(20) DEFAULT 'Prestado'
                )""")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS taller (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    maquina VARCHAR(255) NOT NULL, motivo VARCHAR(255) NOT NULL,
                    fecha_ingreso DATETIME NOT NULL, fecha_salida DATETIME DEFAULT NULL,
                    estado VARCHAR(20) DEFAULT 'En Taller'
                )""")
            cursor.execute("SELECT * FROM usuarios WHERE usuario = 'Admin'")
            if not cursor.fetchone():
                hashed = bcrypt.hashpw("SistemaMantenimiento0611".encode(), bcrypt.gensalt()).decode()
                cursor.execute("INSERT INTO usuarios (usuario, password_hash) VALUES ('Admin', %s)", (hashed,))
            for q in [
                "ALTER TABLE bitacora ADD COLUMN maquina_1 VARCHAR(255) DEFAULT '-'",
                "ALTER TABLE bitacora ADD COLUMN maquina_2 VARCHAR(255) DEFAULT '-'",
                "ALTER TABLE bitacora ADD COLUMN maquina_3 VARCHAR(255) DEFAULT '-'",
                "ALTER TABLE bitacora ADD COLUMN tarea_4 VARCHAR(255) DEFAULT '-'",
                "ALTER TABLE bitacora ADD COLUMN avance_4 INT DEFAULT 0",
                "ALTER TABLE bitacora ADD COLUMN fecha_inicio_4 DATE DEFAULT NULL",
                "ALTER TABLE bitacora ADD COLUMN maquina_4 VARCHAR(255) DEFAULT '-'",
                "ALTER TABLE bitacora ADD COLUMN tarea_5 VARCHAR(255) DEFAULT '-'",
                "ALTER TABLE bitacora ADD COLUMN avance_5 INT DEFAULT 0",
                "ALTER TABLE bitacora ADD COLUMN fecha_inicio_5 DATE DEFAULT NULL",
                "ALTER TABLE bitacora ADD COLUMN maquina_5 VARCHAR(255) DEFAULT '-'",
                "ALTER TABLE bitacora_completados ADD COLUMN maquina VARCHAR(255) DEFAULT '-'"
            ]:
                try:
                    cursor.execute(q)
                    conn.commit()
                except:
                    pass
            try:
                cursor.execute("UPDATE bitacora_completados SET maquina=TRIM(UPPER(maquina)) WHERE maquina IS NOT NULL AND maquina!='-'")
                cursor.execute("UPDATE maquinas SET nombre=TRIM(UPPER(nombre)) WHERE nombre IS NOT NULL")
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
        cursor_db = conn.cursor()
        cursor_db.execute(f"USE {st.secrets['mysql']['database']}")
        cursor_db.close()
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

def check_password(pw, hashed):
    return bcrypt.checkpw(pw.encode(), hashed.encode())

def obtener_lista_maquinas():
    res = db_query("SELECT nombre FROM maquinas ORDER BY nombre ASC", fetch=True)
    lista = ["-"]
    if res:
        lista.extend([str(r['nombre']).strip().upper() for r in res])
    return sorted(list(set(lista)))
