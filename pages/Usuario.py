# Importar los módulos necesarios
import sqlite3
import pandas as pd
import streamlit as st
import psycopg2
import base64

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

#Interfaz Streamlit

st.title("Búsqueda de farmacias con medicamentos en stock")


def obtener_farmacias(codigo_postal, medicamento, id_user):
    conn = get_db_connection()
    query = """
    SELECT f.nombre AS "Nombre de la Farmacia", f.calle AS "Dirección", f.telefono AS "Teléfono", f.horario AS "Horario", d.stock AS "Stock Disponible", f.ID_F
    FROM medpoint.farmacia f
    JOIN medpoint.disponibilidad d ON f.ID_F = d.ID_F
    JOIN medpoint.medicamentos m ON m.ID_medicamento = d.ID_medicamento
    WHERE f.cp = %s AND m.nombre = %s 
    """
    df = pd.read_sql_query(query, conn, params=(codigo_postal, medicamento))
    conn.close()
    
    # Ocultar la columna 'id_f'
    if 'id_f' in df.columns:
        # Añadir la columna del precio calculado
        df['Precio Final ($)'] = df.apply(lambda row: get_price(medicamento, id_user, row['id_f']), axis=1)
        df.drop(columns=['id_f'], inplace=True)
    
    return df

# Función para obtener el precio corregido según el descuento y ganancia
def get_price(med, id_user, id_f):
    conn = get_db_connection()
    try:
        query1 = "SELECT precio FROM medpoint.medicamentos WHERE nombre = %s"
        precio_lista_result = pd.read_sql_query(query1, conn, params=(med,))
        if precio_lista_result.empty:
            return None
        precio_lista = precio_lista_result.iloc[0]['precio']

        query2 = "SELECT ganancia FROM medpoint.farmacia WHERE ID_F = %s"
        profit_result = pd.read_sql_query(query2, conn, params=(id_f,))
        if profit_result.empty:
            return None
        profit = profit_result.iloc[0]['ganancia']

        query3 = """
        SELECT os.descuento
        FROM medpoint.obras_sociales os
        JOIN medpoint.usuarios u ON os.ID_OS = u.ID_OS
        WHERE u.dni = %s
        """
        descuento_result = pd.read_sql_query(query3, conn, params=(id_user,))
        if descuento_result.empty:
            return None
        descuento = descuento_result.iloc[0]['descuento']
    finally:
        conn.close()

    precio_final = (precio_lista + precio_lista * (profit / 100)) * (descuento / 100)
    return precio_final

def cp_exist(cp):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            query = "SELECT * FROM medpoint.farmacia WHERE CP = %s"
            cur.execute(query, (cp,))
            result = cur.fetchone()
            return result 
    finally:
        conn.close()

# Manejo del estado de sesión
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'id_us' not in st.session_state:
    st.session_state.id_us = "id_us"

# Inicio de sesión
if not st.session_state.logged_in:
    st.subheader("Iniciar sesión")
    id_nbr = st.text_input("Ingrese su número de documento", value=None)
    user_password = st.text_input("Ingrese su contraseña", type="password")

    if st.button("Iniciar Sesión"):
        query = "SELECT DNI FROM medpoint.usuarios WHERE DNI=%s AND contraseña=%s"
        cursor.execute(query, (id_nbr, user_password))
        result = cursor.fetchone()
    
        if result:
            st.session_state.logged_in = True
            st.session_state.id_us = result[0]  # Asegúrate de que solo el DNI se guarde en la sesión
            st.success("Inicio de sesión exitoso")
        else:
            st.error("DNI o contraseña incorrectos")

if st.session_state.logged_in:  # buscar farmacias con medicamento en stock
    st.subheader("Buscar Medicamento")
    cp = st.text_input("Ingrese el código postal de su zona")
    med = st.selectbox(
        "Medicamentos",
        ("Albuterol", "Amlodipina", "Amoxicilina", "Aspirina", "Azitromicina", "Clonazepam", "Diclofenac", "Diazepam", "Fluoxetina", "Furosemida", "Glimepirida", "Ibuprofeno",
         "Insulina glargina", "Levotiroxina", "Lisinopril", "Loratadina", "Losartán", "Metformina", "Omeprazol", "Paracetamol", "Propranolol", "Tramadol", "Valsartán", "Warfarina",
         "Zolpidem"))
        
    if st.button("Buscar"):
        if cp_exist(cp):
            farmacias_df = obtener_farmacias(cp, med, st.session_state.id_us)
            if not farmacias_df.empty:
                st.write(f"Farmacias en tu zona con {med} en stock:")
                st.dataframe(farmacias_df)


# Pie de página
st.markdown("---")
st.markdown('<div class="footer">© 2024 MedPoint. Todos los derechos reservados.</div>', unsafe_allow_html=True)
