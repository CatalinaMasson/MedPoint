import streamlit as st
import pandas as pd
import psycopg2
import base64
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
image_path = 'Logo-esquina.jpg'

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
st.markdown(sidebar_style, unsafe_allow_html=True)

# Configuración de la conexión
def get_db_connection():
    conn = psycopg2.connect(
        dbname='postgres',
        user='postgres.milzajyelkzaboqmffzw',
        password='cienciadedatos',
        host='aws-0-us-west-1.pooler.supabase.com',
        port='5432'
    )
    return conn

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
            query = "SELECT ID_medicamento FROM medpoint.medicamentos WHERE nombre = %s"
            cur.execute(query, (med_name,))
            result = cur.fetchone()
            return result 
    finally:
        conn.close()

def get_available_meds(id_f):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            query = """
            SELECT nombre FROM medpoint.medicamentos 
            WHERE ID_medicamento NOT IN (SELECT ID_medicamento FROM medpoint.disponibilidad WHERE ID_F = %s)
            """
            cur.execute(query, (id_f,))
            result = cur.fetchall()
            return [r[0] for r in result]
    finally:
        conn.close()

def get_current_meds(id_f):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            query = """
            SELECT m.nombre, d.stock
            FROM medpoint.medicamentos m
            JOIN medpoint.disponibilidad d ON m.ID_medicamento = d.ID_medicamento
            WHERE d.ID_F = %s
            """
            cur.execute(query, (id_f,))
            result = cur.fetchall()
            return [(r[0], r[1]) for r in result]
    finally:
        conn.close()

st.title('Gestión de medicamentos')

# Manejo del estado de sesión
if 'l_in' not in st.session_state:
    st.session_state.l_in = False

if 'id_f' not in st.session_state:
    st.session_state.id_f = 0

if 'refresh' not in st.session_state:
    st.session_state.refresh = False

if 'success_message' not in st.session_state:
    st.session_state.success_message = ""

# Mostrar mensaje de éxito si existe
if st.session_state.success_message:
    st.success(st.session_state.success_message)
    # Agregar JavaScript para recargar la página después de 2 segundos
    st.markdown(
        """
        <script>
        setTimeout(function(){
            window.location.reload(1);
        }, 2000);
        </script>
        """,
        unsafe_allow_html=True
    )
    st.session_state.success_message = ""

# Inicio de sesión
if not st.session_state.l_in:
    st.subheader("Iniciar sesión")
    ph_name = st.text_input("Ingrese el nombre de su farmacia",  value=None)
    ph_street = st.text_input("Ingrese la calle y altura de su farmacia", value=None)
    pharmacy_password = st.text_input("Ingrese su contraseña", type="password")
    
    if st.button("Iniciar Sesión"):
        query = "SELECT nombre, calle, contraseña FROM medpoint.farmacia WHERE nombre=%s AND calle=%s AND contraseña=%s"
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, (ph_name, ph_street, pharmacy_password))
        result = cursor.fetchone()
        if result:
            st.session_state.l_in = True
            query = "SELECT ID_F FROM medpoint.farmacia WHERE nombre=%s AND calle=%s AND contraseña=%s"
            cursor.execute(query, (ph_name, ph_street, pharmacy_password))
            id_f = cursor.fetchone()[0]
            st.session_state.id_f = id_f
            st.success("Inicio de sesión exitoso")
        else:
            st.error("Datos incorrectos")
        conn.close()

if st.session_state.l_in:
    selected_tab = st.radio("Seleccione una pestaña", ["Visualizar Stock", "Editar Stock", "Agregar Medicamentos"])
    
    if selected_tab == "Visualizar Stock":
        st.subheader("Visualizar Stock")
        
        conn = get_db_connection()
        query = """
        SELECT m.nombre, d.stock
        FROM medpoint.medicamentos m
        JOIN medpoint.disponibilidad d ON m.ID_medicamento = d.ID_medicamento
        WHERE d.ID_F = %s
        """
        stock_df = pd.read_sql_query(query, conn, params=(st.session_state.id_f,))
        conn.close()
        
        if stock_df.empty:
            st.info("No tiene ningún medicamento en stock. Por favor, vaya a la pestaña 'Agregar Medicamentos'.")
        else:
            col1, col2 = st.columns([1,2])
        
            with col1:
                st.write("Stock de Medicamentos")
                st.dataframe(stock_df)

            with col2:
                fig_pie = px.pie(stock_df, names='nombre', values='stock', 
                                labels={'nombre':''})
                st.plotly_chart(fig_pie)

    elif selected_tab == "Editar Stock":
        st.subheader("Editar Stock")
        current_meds = get_current_meds(st.session_state.id_f)
        
        if not current_meds:
            st.info("No tiene ningún medicamento en stock. Por favor, vaya a la pestaña 'Agregar Medicamentos'.")
        else:
            med_to_edit = st.selectbox("Seleccione un medicamento para editar", [med[0] for med in current_meds], key="edit_stock")
            current_stock = next((med[1] for med in current_meds if med[0] == med_to_edit), 0)
            new_stock = st.number_input("Ingrese la nueva cantidad de stock", value=current_stock, min_value=0, step=1)

            if st.button("Actualizar Stock"):
                id_med = search_idmed(med_to_edit)[0]
                delete_stock(st.session_state.id_f, id_med)
                if new_stock > 0:
                    edit_stock(new_stock, st.session_state.id_f, id_med)
                    st.session_state.success_message = f'Stock de {med_to_edit} actualizado a {new_stock}.'
                else:
                    st.session_state.success_message = f'{med_to_edit} ha sido eliminado del stock.'
                
                st.experimental_rerun()

    elif selected_tab == "Agregar Medicamentos":
        st.subheader("Agregar Medicamentos")
        available_meds = get_available_meds(st.session_state.id_f)
        med_to_add = st.selectbox("Seleccione un medicamento para agregar", available_meds, key="add_stock")
        stock_to_add = st.number_input("Ingrese la cantidad de stock", min_value=0, step=1)
        
        if st.button("Agregar Medicamento"):
            if stock_to_add == 0:
                st.error("No se puede agregar un medicamento con stock 0.")
            else:
                id_med = search_idmed(med_to_add)[0]
                edit_stock(stock_to_add, st.session_state.id_f, id_med)
                st.session_state.success_message = f'{med_to_add} ha sido agregado con {stock_to_add} en stock.'
                
                st.experimental_rerun()
