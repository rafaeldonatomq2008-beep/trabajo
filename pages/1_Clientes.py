
import streamlit as st
from database import obtener_conexion

# Título de la página
st.title("Registro de Clientes")

# Campos para ingresar los datos del cliente
nombre = st.text_input("Nombre")
telefono = st.text_input("Teléfono")
direccion = st.text_input("Dirección")

# Registrar un nuevo cliente
if st.button("Registrar"):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    # Guarda los datos; MySQL genera el ID automáticamente
    cursor.execute(
        "INSERT INTO CLIENTES (nombre, telefono, direccion) VALUES (%s, %s, %s)",
        (nombre, telefono, direccion)
    )

    conexion.commit()  # Guarda los cambios en la base de datos
    conexion.close()  # Cierra la conexión
    st.success("Cliente registrado")

# Consultar todos los clientes registrados

conexion = obtener_conexion()
cursor = conexion.cursor()
cursor.execute("SELECT * FROM CLIENTES")
clientes = cursor.fetchall()  # Obtiene todos los resultados
conexion.close()

# Mostrar los clientes en una tabla
st.subheader("Clientes registrados")
st.dataframe(clientes)

# Mostrar una lista para elegir qué cliente actualizar
if clientes:
    cliente = st.selectbox(
        "Seleccionar cliente para actualizar",
        clientes,
        format_func=lambda c: f"{c[0]} - {c[1]}"
    )

    # Mostrar los datos actuales del cliente seleccionado
    nuevo_nombre = st.text_input("Nuevo nombre", value=cliente[1])
    nuevo_telefono = st.text_input("Nuevo teléfono", value=cliente[2] or "")
    nueva_direccion = st.text_input("Nueva dirección", value=cliente[3] or "")

    # Actualizar los datos del cliente seleccionado
    if st.button("Actualizar"):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            "UPDATE CLIENTES SET nombre=%s, telefono=%s, direccion=%s WHERE idcliente=%s",
            (nuevo_nombre, nuevo_telefono, nueva_direccion, cliente[0])
        )

        conexion.commit()  # Guarda la actualización
        conexion.close()  # Cierra la conexión
        st.success("Cliente actualizado")
        st.rerun()  # Recarga la página para mostrar los cambios
