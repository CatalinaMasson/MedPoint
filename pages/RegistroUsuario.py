import streamlit as st
import psycopg2
import base64
import time
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

def dni_exists(dni):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            query = "SELECT * FROM medpoint.usuarios WHERE DNI = %s"
            cur.execute(query, (dni,))
            result = cur.fetchone()
            return result 
    finally:
        conn.close()

def id_os(os_user, plan_user):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            query = "SELECT id_os FROM medpoint.obras_sociales WHERE nombre = '{}' AND plan = '{}'".format(os_user, plan_user)
            cur.execute(query, (os_user,plan_user,))
            result = cur.fetchone()
            return result 
    finally:
        conn.close()

def insert_user(user_name, dni_user, id_os, user_password):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            query = "INSERT INTO medpoint.usuarios (nombre, DNI, ID_OS, contraseña) VALUES (%s, %s, %s, %s)"
            cur.execute(query, (user_name, dni_user, id_os, user_password,))
            conn.commit()
    except psycopg2.Error as e:
        st.error(f"Se produjo un error al guardar el usuario: {e}")
    finally:
        conn.close()

def is_valid_name(name):
    return bool(re.match(r'^[A-Za-z\s]+$', name))

def is_valid_dni(dni):
    return dni.isdigit()

# Interfaz de Streamlit
# Título y foto en la misma fila
st.title('Registra tu usuario')
user_name = st.text_input("Apellido y Nombre", placeholder="Ejemplo: Rodriguez Juan")
dni_user = st.text_input("DNI", placeholder="Ejemplo: 46897546")
user_password = st.text_input("Contraseña", type="password")
os_user = st.selectbox(
    "Obra Social",
    ("OSDE", "Medifé", "Swiss Medical", "Jerárquicos", "OSDIPP", "Galeno", "MEDICUS", "Omint"), 
    index=None,
    placeholder="Seleccioná tu obra social",)
if os_user == "OSDE":
    plan_user = st.selectbox("Plan", ("210", "420" , "450"), index=None,placeholder="Selecciona tu plan...",)
elif os_user == "Medifé":
    plan_user = st.selectbox("Plan", ("Bronce","Oro", "Platinum"), index=None,placeholder="Selecciona tu plan...",)
elif os_user == "Swiss Medical":
    plan_user = st.selectbox("Plan", ("SMG02", "SMG20", "SMG50"), index=None,placeholder="Selecciona tu plan...",)  
elif os_user == "Jerárquicos":
    plan_user = st.selectbox("Plan", ("2000", "2886", "3000"), index=None,placeholder="Selecciona tu plan...",)  
elif os_user == "OSDIPP":
    plan_user = st.selectbox("Plan", ("1D", "2D", "3E"), index=None,placeholder="Selecciona tu plan...",)  
elif os_user == "Galeno":
    plan_user = st.selectbox("Plan", ("220", "330", "550"), index=None,placeholder="Selecciona tu plan...",)  
elif os_user == "MEDICUS":
    plan_user = st.selectbox("Plan", ("Azul", "Celeste", "Family"), index=None,placeholder="Selecciona tu plan...",)  
elif os_user == "Omint":
    plan_user = st.selectbox("Plan", ("Premium", "Clásico", "Global"), index=None,placeholder="Selecciona tu plan...",)  


if st.button('Guardar'):
    bar = st.progress(10, text = "Comprobando que los campos estén completos correctamente...")
    time.sleep(0.725)
    if not user_name or not dni_user or not os_user or not plan_user or not user_password:
        st.error("Por favor, completa todos los campos.")
    elif dni_exists(dni_user):
        st.error("Ya existe otro usuario con este DNI.")
    elif not is_valid_name(user_name):
        st.error("El nombre solo puede contener letras.")
    elif not is_valid_dni(dni_user):
        st.error("El DNI solo puede contener números.")
    else:
        bar.progress(35, text = "Creando usuario...")
        time.sleep(0.725)
        insert_user(user_name, dni_user, id_os(os_user, plan_user), user_password)
        bar.progress(100, text = "Registro concluido")
        bar.empty()
        st.success('Tu usuario ha sido creado correctamente', icon="✅")
        st.write('Ahora inicia sesión para buscar medicamentos en tu zona')
        if st.button("Inicia sesión"):
            st.switch_page(r"pages\Usuario.py")

# Pie de página
st.markdown("---")
st.markdown('<div class="footer">© 2024 MedPoint. Todos los derechos reservados.</div>', unsafe_allow_html=True)
