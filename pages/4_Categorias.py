
import streamlit as st
import pandas as pd
from database import obtener_conexion

st.title("Gestión de Categorías")

conn = obtener_conexion()

st.subheader("Registrar categoría")
nombre = st.text_input("Nombre de categoría")
descripcion = st.text_input("Descripción")

if st.button("Registrar categoría"):
    if nombre:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO Categorias (Nombre_Categoria, Descripcion)
                VALUES (%s, %s)
            """, (nombre, descripcion))
            conn.commit()
            st.success("Categoría registrada")
            st.rerun()
        except Exception:
            conn.rollback()
            st.error("No se pudo registrar. Comprueba que el nombre no exista.")
        finally:
            cursor.close()
    else:
        st.warning("Ingresa el nombre")

st.subheader("Consultar categorías")
categorias = pd.read_sql("SELECT * FROM Categorias", conn)
st.dataframe(categorias, use_container_width=True)

if not categorias.empty:
    st.subheader("Actualizar categoría")
    id_categoria = st.selectbox(
        "ID de categoría", categorias["ID_Categoria"]
    )
    fila = categorias[categorias["ID_Categoria"] == id_categoria].iloc[0]

    nuevo_nombre = st.text_input(
        "Nuevo nombre", str(fila["Nombre_Categoria"])
    )
    nueva_descripcion = st.text_input(
        "Nueva descripción", str(fila["Descripcion"] or "")
    )

    if st.button("Actualizar categoría"):
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE Categorias
                SET Nombre_Categoria=%s, Descripcion=%s
                WHERE ID_Categoria=%s
            """, (nuevo_nombre, nueva_descripcion, int(id_categoria)))
            conn.commit()
            st.success("Categoría actualizada")
            st.rerun()
        except Exception:
            conn.rollback()
            st.error("No se pudo actualizar. Comprueba que el nombre sea único.")
        finally:
            cursor.close()

    st.subheader("Eliminar categoría")
    if st.button("Eliminar categoría"):
        cursor = conn.cursor()
        try:
            cursor.execute(
                "DELETE FROM Categorias WHERE ID_Categoria=%s",
                (int(id_categoria),)
            )
            conn.commit()
            st.success("Categoría eliminada")
            st.rerun()
        except Exception:
            conn.rollback()
            st.error("No se puede eliminar: la categoría puede tener platos")
        finally:
            cursor.close()

conn.close()
