import streamlit as st
from models.cliente import Cliente

def mostrar_vista_clientes():

    st.title("Gestión de Clientes")

    # Registrar cliente
    with st.form("form_reg"):
        nombre = st.text_input("Nombre")
        telefono = st.text_input("Teléfono")
        direccion = st.text_input("Dirección")

        guardar = st.form_submit_button("Guardar")

    if guardar:
        cliente = Cliente(nombre=nombre, telefono=telefono, direccion=direccion)
        cliente.registrar()
        st.success("Cliente registrado")
        st.rerun()

    # Listar clientes
    clientes = Cliente.obtener_todos()

    for c in clientes:
        st.write(c.idcliente, c.nombre, c.telefono, c.direccion)

    # Actualizar cliente
    if clientes:
        cliente = st.selectbox("Seleccionar cliente", clientes)

        with st.form("form_act"):
            nombre = st.text_input("Nombre", value=cliente.nombre)
            telefono = st.text_input("Teléfono", value=cliente.telefono or "")
            direccion = st.text_input("Dirección", value=cliente.direccion or "")

            actualizar = st.form_submit_button("Actualizar")

        if actualizar:
            cliente.nombre = nombre
            cliente.telefono = telefono
            cliente.direccion = direccion

            cliente.actualizar()
            st.success("Cliente actualizado")
            st.rerun()