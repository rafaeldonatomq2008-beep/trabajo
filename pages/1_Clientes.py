
import streamlit as st
from database import obtener_conexion

st.title("Registro de clientes")

nombre = st.text_input("Nombre")
apellido = st.text_input("Apellido")
telefono = st.text_input("Teléfono")
correo = st.text_input("Correo")

if st.button("Guardar cliente"):

    conexion = obtener_conexion()

    if conexion:
        cursor = conexion.cursor()

        sql = """
            INSERT INTO Clientes
            (Nombre, Apellido, Telefono, Correo)
            VALUES (%s, %s, %s, %s)
        """

        cursor.execute(
            sql,
            (nombre, apellido, telefono, correo)
        )

        conexion.commit()
        cursor.close()
        conexion.close()

        st.success("Cliente registrado correctamente")
    else:
        st.error("Error de conexión")

st.subheader("Clientes registrados")

conexion = obtener_conexion()

if conexion:
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM Clientes")

    st.dataframe(cursor.fetchall())

    cursor.close()
    conexion.close()
