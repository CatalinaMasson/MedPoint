import streamlit as st
import base64

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
# Agregar el CSS al HTML de la app
st.markdown(sidebar_style, unsafe_allow_html=True)

# CSS personalizado para la app
main_style = """
    <style>
    .main {
        background-color: #DCEAF1;
        padding-top: 0 !important; /* Elimina el margen superior */
    }
    .stButton button {
        background-color: #1A7B94;
        color: white;
        border-radius: 4px;
        padding: 10px 24px;
        font-size: 16px;
        margin: 5px;
        cursor: pointer;
    }
    .stButton button:hover {
        background-color: #CEDFEC;
    }
    .stTextInput input {
        border-radius: 4px;
        padding: 10px;
    }
    .stImage {
        border-radius: 8px;
    }
    .justified-text {
        text-align: justify;
    }
    .header-text {
        font-size: 24px;
        font-weight: bold;
        color: #333;
    }
    .subheader-text {
        font-size: 20px;
        color: #555;
    }
    .footer {
        text-align: center;
        padding: 20px;
        font-size: 14px;
        color: #888;
    }
    .carousel-caption {
        text-align: center;
        font-size: 16px;
    }
    </style>
    """
st.markdown(main_style, unsafe_allow_html=True)



# Encabezado principal
st.title("Bienvenido a MedPoint")

# Sección de columnas con imagen y descripción
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    <div class="justified-text">
    MedPoint es tu compañero confiable en la búsqueda de medicamentos urgentes. 
    ¿Necesitas encontrar un medicamento específico rápidamente? Con MedPoint, nunca te preocuparás por buscar en vano. 
    Nuestra aplicación te conecta con las farmacias más cercanas que tienen el medicamento que necesitas.
    </div>
    <div class="justified-text">
    ¡Di adiós a las búsquedas interminables y a las decepciones! 
    <strong>Regístrate en MedPoint hoy y encuentra tus medicamentos con facilidad y rapidez.</strong>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.image('mapa con compu.png', use_column_width=True, output_format='auto')

# Pestañas de usuario y farmacia
tab1, tab2 = st.tabs(["Soy Usuario", "Soy Farmacia"])

with tab1:
    st.subheader("Inicie sesión o cree una cuenta")
    st.write("""
    Inicia sesión para averiguar qué farmacias cercanas cuentan con el medicamento que buscas. 
    Si todavía no tienes una cuenta, créate una.
    """)
    if st.button("Crear cuenta"):
        st.switch_page("pages/Registro - Usuarios.py")
    if st.button("Iniciar sesión"):
        st.switch_page("pages/Iniciar sesión - Usuarios.py")


with tab2:
    st.subheader("Edite su stock o registre su farmacia")
    st.write("""
    Registra tu farmacia para que te conozcan los clientes. 
    Puedes actualizar tu stock cada vez que sea necesario.
    """)
    if st.button("Registra tu farmacia"):
        st.switch_page("pages/Registro - Farmacias.py")
    if st.button("Edita tu stock"):
        st.switch_page("pages/Iniciar sesión - Farmacias.py")
                

# Carrousel de imágenes (simulado con columnas)
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("### Descubre nuestras funcionalidades")

st.markdown("""
    <div class="justified-text">
    Esta app ofrece una experiencia personalizada para simplificar la búsqueda y adquisición de medicamentos. 
    Los usuarios, una vez registrados, tienen acceso a una amplia base de datos de medicamentos, 
    pudiendo realizar búsquedas por nombre junto con un código postal para encontrar las farmacias cercanas que los tienen disponibles. 
    MedPoint proporciona información en tiempo real sobre precios y disponibilidad, permitiendo a los usuarios tomar decisiones informadas. 
    A su vez, las farmacias pueden registrarse en la plataforma, especificando su ubicación y las obras sociales que aceptan, 
    y actualizar su inventario de medicamentos, garantizando una experiencia confiable y actualizada para los usuarios.
    </div>
    """, unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)
carousel_col1, carousel_col2, carousel_col3 = st.columns(3)

with carousel_col1:
    st.image('feature5.jpg', caption='Encuentra medicamentos rápidamente', use_column_width=True)
with carousel_col2:
    st.image('feature2.jpg', caption='Conéctate con farmacias locales', use_column_width=True)
with carousel_col3:
    st.image('feature3.jpg', caption='Actualización de stock en tiempo real', use_column_width=True)

# Formulario de contacto
st.markdown("### Contáctanos")
contact_form = """
<form action="https://formspree.io/f/myyrqdkb" method="POST">
    <input type="email" name="email" placeholder="Tu correo" required style="width: 100%; padding: 10px; margin: 5px 0; border-radius: 4px; border: 1px solid #ccc;">
    <textarea name="message" placeholder="Tu mensaje" required style="width: 100%; padding: 10px; margin: 5px 0; border-radius: 4px; border: 1px solid #ccc;"></textarea>
    <button type="submit" class="button">Enviar</button>
</form>
"""
st.markdown(contact_form, unsafe_allow_html=True)

# Pie de página
st.markdown("---")
st.markdown('<div class="footer">© 2024 MedPoint. Todos los derechos reservados.</div>', unsafe_allow_html=True)