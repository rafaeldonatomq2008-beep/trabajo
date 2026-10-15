
import streamlit as st
from database import obtener_conexion

st.title("Registro de categorías")

nombre = st.text_input("Nombre de la categoría")
descripcion = st.text_input("Descripción")

if st.button("Guardar categoría"):

    conexion = obtener_conexion()

    if conexion:
        cursor = conexion.cursor()

        sql = """
            INSERT INTO Categorias
            (Nombre_Categoria, Descripcion)
            VALUES (%s, %s)
        """

        cursor.execute(sql, (nombre, descripcion))
        conexion.commit()

        cursor.close()
        conexion.close()

        st.success("Categoría registrada correctamente")
    else:
        st.error("Error de conexión")

st.subheader("Categorías registradas")

conexion = obtener_conexion()

if conexion:
    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM Categorias")

    st.dataframe(cursor.fetchall())

    cursor.close()
    conexion.close()
