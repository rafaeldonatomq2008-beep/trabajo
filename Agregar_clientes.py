
import streamlit as st
from database import obtener_conexion

st.title("Sistema de Gestión de Restaurante")
st.header("Crear cliente")

nombre = st.text_input("Nombre")
apellido = st.text_input("Apellido")
telefono = st.text_input("Teléfono")
direccion = st.text_input("Dirección")
correo = st.text_input("Correo")

if st.button("Guardar cliente"):

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    sql = """
        INSERT INTO Clientes (Nombre, Apellido, Telefono, Direccion, Correo)
        VALUES (%s, %s, %s, %s, %s)
    """

    cursor.execute(sql, (nombre, apellido, telefono, direccion, correo))
    conexion.commit()

    cursor.close()
    conexion.close()

    st.success("Cliente registrado correctamente")

st.header("Lista de clientes")

conexion = obtener_conexion()
cursor = conexion.cursor()

cursor.execute("SELECT * FROM Clientes")

clientes = cursor.fetchall()

st.dataframe(clientes)

cursor.close()
conexion.close()
