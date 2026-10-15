import streamlit as st
from database import obtener_conexion

st.title("Sistema de Gestión de Restaurante")
st.header("Crear categoría")

nombre = st.text_input("Nombre de la categoría")
descripcion = st.text_input("Descripción")

if st.button("Guardar categoría"):

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    sql = """
        INSERT INTO Categorias (Nombre_Categoria, Descripcion)
        VALUES (%s, %s)
    """

    cursor.execute(sql, (nombre, descripcion))
    conexion.commit()

    cursor.close()
    conexion.close()

    st.success("Categoría registrada correctamente")

st.header("Lista de categorías")

conexion = obtener_conexion()
cursor = conexion.cursor()

cursor.execute("SELECT * FROM Categorias")

categorias = cursor.fetchall()

st.dataframe(categorias)

cursor.close()
conexion.close()