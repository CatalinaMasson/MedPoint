import streamlit as st
import psycopg2
import base64
import time
import pandas as pd
import re

# Configuración de la página
st.set_page_config(page_title='MedPoint', page_icon='logoMedPoint.jpg', layout='wide')

# Función para convertir una imagen en base64
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Ruta a la imagen de fondo
image_path = 'Logo-esquina.jpg'  # Asegúrate de que la imagen esté en el mismo directorio que tu script

# Convierte la imagen a base64
image_base64 = get_base64_of_bin_file(image_path)

# CSS para cambiar el fondo de la barra lateral con una imagen en base64
sidebar_style = f"""
    <style>
    [data-testid="stSidebar"] {{
        background-image: url("data:image/png;base64,{image_base64}");
        background-size: cover;
        background-repeat: no-repeat;
        background-position: top left;
    }}
    </style>
    """

# Agregar el CSS al HTML de la app
st.markdown(sidebar_style, unsafe_allow_html=True)

# CSS para cambiar el color de fondo de toda la aplicación
background_color_style = """
    <style>
    body {
        background-color: #D6EAEA;  
    }
    </style>
    """

# Agregar el CSS al HTML de la app
st.markdown(background_color_style, unsafe_allow_html=True)

# Configuración de la conexión
def get_db_connection():
    user = 'postgres.milzajyelkzaboqmffzw'
    password = 'cienciadedatos'
    host = 'aws-0-us-west-1.pooler.supabase.com'
    port = '5432'
    dbname = 'postgres'
    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )
    return conn

def pharmacy_exists(pharmacy_name,street_name):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            query = "SELECT * FROM medpoint.farmacia WHERE nombre = '{}' AND calle = '{}'".format(pharmacy_name,street_name)
            cur.execute(query, (pharmacy_name,street_name,))
            result = cur.fetchone()
            return result 
    finally:
        conn.close()

def create_idf():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            query = "SELECT COUNT(*) FROM medpoint.farmacia"
            cur.execute(query, ())
            result = cur.fetchone()[0]
            return result + 1
    finally:
        conn.close()


def create_horario(time_open, time_close):
    return f"{time_open} - {time_close}"


def insert_pharmacy(pharmacy_name,cp,street_name,phone_nbr ,pharmacy_password , time_open, time_close,profit,id_f):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            horario = create_horario(time_open,time_close)
            query = "INSERT INTO medpoint.farmacia (ID_F,nombre, CP, calle, telefono, horario, ganancia, contraseña) VALUES ({},'{}','{}','{}','{}','{}',{},'{}')".format(id_f, pharmacy_name,cp, street_name,phone_nbr, horario,profit, pharmacy_password)
            cur.execute(query, (id_f, pharmacy_name,cp, street_name,phone_nbr, horario,profit,pharmacy_password))
            conn.commit()
    except psycopg2.Error as e:
        st.error(f"Se produjo un error al guardar el usuario: {e}")
    finally:
        conn.close()

def id_f(f_name, cp, street_name):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            query = "SELECT ID_F FROM medpoint.farmacia WHERE nombre = '{}' AND CP = '{}' AND calle = '{}'".format(f_name, cp, street_name)
            cur.execute(query, (f_name, cp, street_name,))
            result = cur.fetchone()
            return result 
    finally:
        conn.close()


def insert_cobertura(id_os, id_f):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            horario = create_horario(time_open,time_close)
            query = "INSERT INTO medpoint.cobertura (ID_OS,ID_F) VALUES ({},{})".format(id_os, id_f)
            cur.execute(query, (id_os, id_f,))
            conn.commit()
    except psycopg2.Error as e:
        st.error(f"Se produjo un error al guardar la cobertura: {e}")
    finally:
        conn.close()

if 'state_initialized' not in st.session_state:
    st.session_state.state_initialized = False

if 'selected_obras_sociales' not in st.session_state:
    st.session_state.selected_obras_sociales = {}

st.title('Registra tu farmacia')

pharmacy_name = st.text_input("Nombre de la farmacia", placeholder="Ejemplo: Farmacity")
cp = st.text_input("Código postal", placeholder="Ejemplo: 6600")
street_name = st.text_input("Calle y altura", placeholder="Ejemplo: Avenida Rivadavia 1600")
phone_nbr = st.text_input("Teléfono", placeholder="Ejemplo: 011-1111-1111")
pharmacy_password = st.text_input("Contraseña", type="password")
time_open = st.text_input("Horario de apertura", placeholder="Ejemplo: 08:00")
time_close = st.text_input("Horario de cierre", placeholder="Ejemplo: 20:30")
profit = st.slider("Porcentaje de ganancia", 0, 100)


def is_valid_cp(cp):
    return cp.isdigit()

def is_valid_time_format(time_str):
    return bool(re.match(r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$', time_str))

def is_valid_name(ph_name):
    return bool(re.match(r'^[A-Za-z0-9\s]+$', ph_name))

if st.button('Continuar') or st.session_state.state_initialized:
    bar = st.progress(25, text = "Comprobando que los campos estén completos correctamente...")
    time.sleep(0.725)
    if not st.session_state.state_initialized:
        if not pharmacy_name or not cp or not street_name or not phone_nbr or not pharmacy_password or not time_open or not time_close:
            st.error("Por favor, completa todos los campos.")
        elif pharmacy_exists(pharmacy_name, street_name):
            st.error("Esta farmacia ya está registrada.")
        elif not is_valid_name(pharmacy_name):
            st.error("El nombre no puede contener caracteres especiales")
        elif not is_valid_cp(cp):
            st.error("El código postal solo puede contener números.")
        elif not is_valid_time_format(time_open) or not is_valid_time_format(time_close):
            st.error("Horario de apertura o cierre inválido.")
        else:
            bar.progress(60, text = "Registrando farmacia...")
            time.sleep(0.725)
            id_f = create_idf()
            insert_pharmacy(pharmacy_name, cp, street_name, phone_nbr, pharmacy_password, time_open, time_close, profit, id_f)
            bar.progress(100, text = "Datos validados")
            bar.empty()
            st.session_state.state_initialized = True
            st.session_state.id_f = id_f

    st.write("¿Qué obras sociales recibe tu farmacia?")
    
    # Lista de obras sociales y sus IDs
    obras_sociales = {
        "OSDE": [1, 9, 17],
        "Swiss Medical": [2, 10, 18],
        "Galeno": [3, 11, 19],
        "OMINT": [4, 12, 20],
        "OSDIPP": [5, 13, 21],
        "Medifé": [6, 14, 22],
        "MEDICUS": [7, 15, 23],
        "Jerárquicos": [8, 16, 24]
    }

    # Mantener el estado de los checkboxes
    selected_obras_sociales = st.session_state.selected_obras_sociales

    for obra_social, ids in obras_sociales.items():
        checked = obra_social in selected_obras_sociales
        if st.checkbox(obra_social, value=checked):
            selected_obras_sociales[obra_social] = ids
        elif obra_social in selected_obras_sociales:
            del selected_obras_sociales[obra_social]
    
    st.session_state.selected_obras_sociales = selected_obras_sociales

    if st.button('Guardar'):
        my_bar = st.progress(30, text = "Completando registro...")
        time.sleep(0.725)
        for obra_social in st.session_state.selected_obras_sociales:
            for id in obras_sociales[obra_social]:
                insert_cobertura(id, st.session_state.id_f)
        my_bar.progress(90, text = "Aguarde un moemnto...")
        time.sleep(0.725)
        my_bar.progress(100, text = "Registro concluido")
        my_bar.empty()
        st.success('Tu farmacia ha sido registrada correctamente', icon="✅")
        st.write('Ahora inicia sesión para actualizar tu stock así los usuarios pueden encontrar tu farmacia como punto de venta')
        if st.button("Inicia sesión"):
            st.switch_page(r"pages\EditarStock.py")
        
# Pie de página
st.markdown("---")
st.markdown('<div class="footer">© 2024 MedPoint. Todos los derechos reservados.</div>', unsafe_allow_html=True)