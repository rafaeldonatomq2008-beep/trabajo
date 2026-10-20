import streamlit as st
from controllers.cliente_controller import ClienteController

def mostrar_vista_clientes():
    st.title("Gestión de Clientes")

    # --- SECCIÓN: REGISTRAR CLIENTE ---
    st.subheader("Registrar Nuevo Cliente")
    with st.form("form_registro", clear_on_submit=True):
        nombre = st.text_input("Nombre")
        telefono = st.text_input("Teléfono")
        direccion = st.text_input("Dirección")
        submit_registro = st.form_submit_button("Registrar")

        if submit_registro:
            exito, mensaje = ClienteController.registrar_cliente(nombre, telefono, direccion)
            if exito:
                st.success(mensaje)
                st.rerun()
            else:
                st.error(mensaje)

    # --- SECCIÓN: CONSULTAR Y ACTUALIZAR CLIENTES ---
    st.subheader("Clientes Registrados")
    clientes = ClienteController.listar_clientes()

    if clientes:
        st.dataframe(clientes)

        st.subheader("Actualizar Cliente")
        cliente_seleccionado = st.selectbox(
            "Seleccionar cliente para actualizar",
            clientes,
            format_func=lambda c: f"{c[0]} - {c[1]}"
        )

        if cliente_seleccionado:
            with st.form("form_actualizar"):
                nuevo_nombre = st.text_input("Nuevo nombre", value=cliente_seleccionado[1])
                nuevo_telefono = st.text_input("Nuevo teléfono", value=cliente_seleccionado[2] or "")
                nueva_direccion = st.text_input("Nueva dirección", value=cliente_seleccionado[3] or "")
                submit_actualizar = st.form_submit_button("Actualizar")

                if submit_actualizar:
                    exito, mensaje = ClienteController.actualizar_cliente(
                        cliente_seleccionado[0], nuevo_nombre, nuevo_telefono, nueva_direccion
                    )
                    if exito:
                        st.success(mensaje)
                        st.rerun()
                    else:
                        st.error(mensaje)
    else:
        st.info("No hay clientes registrados todavía.")