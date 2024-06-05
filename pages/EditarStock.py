import streamlit as st
import sqlite3
import pandas as pd
import psycopg2
import base64
import matplotlib.pyplot as plt
import plotly.express as px
import time

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


cursor = get_db_connection().cursor()

def stock_exists(id_f, id_med):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            query = "SELECT * FROM medpoint.disponibilidad WHERE ID_F = %s AND ID_medicamento = %s"
            cur.execute(query, (int(id_f), int(id_med),))
            result = cur.fetchone()
            return result 
    finally:
        conn.close()

def delete_stock(id_f, id_med):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            query = "DELETE FROM medpoint.disponibilidad WHERE ID_medicamento = %s AND ID_F = %s"
            cur.execute(query, (int(id_med), int(id_f),))
            conn.commit()
    finally:
        conn.close()



def edit_stock(stock, id_f, id_m):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            query = "INSERT INTO medpoint.disponibilidad (ID_medicamento, ID_F, stock) VALUES (%s, %s, %s)"
            cur.execute(query, (int(id_m), int(id_f), int(stock),))
            conn.commit()
    finally:
        conn.close()



def search_idmed(med_name):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            query = "SELECT ID_medicamento FROM medpoint.medicamentos WHERE nombre = '{}'".format(med_name)
            cur.execute(query, (med_name,))
            result = cur.fetchone()
            return result 
    finally:
        conn.close()


st.title('Gestión de medicamentos')

# Manejo del estado de sesión
if 'l_in' not in st.session_state:
    st.session_state.l_in = False

if 'id_f' not in st.session_state:
    st.session_state.id_f = 0

# Inicio de sesión
if not st.session_state.l_in:
    st.subheader("Iniciar sesión")
    ph_name = st.text_input("Ingrese el nombre de su farmacia",  value=None)
    ph_street = st.text_input("Ingrese la calle y altura de su farmacia", value=None)
    pharmacy_password = st.text_input("Ingrese su contraseña", type="password")
    

    if st.button("Iniciar Sesión"):
        query = "SELECT nombre, calle, contraseña FROM medpoint.farmacia WHERE nombre='{}' AND calle='{}' AND contraseña='{}'".format(ph_name, ph_street, pharmacy_password)
        cursor.execute(query, (ph_name, ph_street, pharmacy_password))
        result = cursor.fetchone()
    
        if result:
            st.session_state.l_in = True
            query = "SELECT ID_F FROM medpoint.farmacia WHERE nombre='{}' AND calle='{}' AND contraseña='{}'".format(ph_name, ph_street, pharmacy_password)
            cursor.execute(query, (ph_name, ph_street, pharmacy_password))
            id_f = cursor.fetchone()
            st.session_state.id_f = id_f
            st.success("Inicio de sesión exitoso")
        else:
            st.error("Datos incorrectos")

if st.session_state.l_in:
    st.subheader("Editar stock")
    
    data_df = pd.DataFrame(
    {"Medicamentos" : ["Albuterol", "Amlodipina", "Amoxicilina", "Aspirina", "Azitromicina", "Clonazepam", "Diclofenac", "Diazepam", "Fluoxetina", "Furosemida", "Glimepirida", "Ibuprofeno", "Insulina glargina", "Levotiroxina", "Lisinopril", "Loratadina", "Losartán", "Metformina", "Omeprazol", "Paracetamol", "Propranolol", "Tramadol", "Valsartán", "Warfarina", "Zolpidem"],
        "Stock" : [0] * 25})

    edited_df = st.data_editor(
        data_df,
        column_config={
            "Stock": st.column_config.NumberColumn(
                "Stock",
                help="Haz doble click en el casillero e indica el stock de tu producto",
                min_value=0,
                step=1,
            )
        },
        hide_index=True,
    )

    if st.button('Guardar'):
        bar = st.progress(5, text = "Comenzando la actualización de stock...")
        time.sleep(0.725)
        t = 5
        for i in range(1, 26):
            n = i - 1 
            t = t + 3
            med = edited_df["Medicamentos"].iloc[n]
            bar.progress(t, text = f"Guardando stock de {med}...")
            time.sleep(0.05)
            id_med = search_idmed(med)
            if stock_exists(st.session_state.id_f[0] , id_med[0]):
                delete_stock(st.session_state.id_f[0] , id_med[0])
            stock = edited_df["Stock"].iloc[n]
            if stock > 0:
                edit_stock(stock, st.session_state.id_f[0] , id_med[0])
            elif stock < 0:
                st.error("No se aceptan cantidades negativas de medicamentos.")
        bar.progress(95, text = "Completando actualización de stock...")
        time.sleep(0.725)
        bar.progress(100, text = "Proceso completado")
        bar.empty()
        st.success('Tu stock ha sido actualizado correctamente', icon="✅")
        # Visualización del stock en gráficos
        st.subheader("Visualización del Stock")
        # Gráfico de pastel
        fig_pie = px.pie(edited_df, names='Medicamentos', values='Stock', title='Distribución de Stock',
                         labels={'Medicamentos':''})
        st.plotly_chart(fig_pie)


# Pie de página
st.markdown("---")
st.markdown('<div class="footer">© 2024 MedPoint. Todos los derechos reservados.</div>', unsafe_allow_html=True)