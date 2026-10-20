import streamlit as st
from views.cliente_view import mostrar_vista_clientes

# Configuración global
st.set_page_config(
    page_title="Sistema de Gestión",
    page_icon="📊",
    layout="centered"
)

# Menú lateral (Enrutador)
st.sidebar.title("Menú Principal")
menu = st.sidebar.radio("Seleccione un módulo:", ["Inicio", "Clientes"])

# Lógica de navegación (Router)
if menu == "Inicio":
    st.title("Bienvenido al Sistema")
    st.write("Selecciona un módulo en el menú lateral izquierdo para comenzar.")

elif menu == "Clientes":
    mostrar_vista_clientes()
    
# Cuando agregues productos, solo harás:
# elif menu == "Productos":
#     mostrar_vista_productos()