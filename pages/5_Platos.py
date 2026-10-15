
# Streamlit permite crear la interfaz gráfica del sistema
import streamlit as st

# Pandas permite mostrar los datos en tablas
import pandas as pd

# Permite establecer la conexión con MySQL
from database import obtener_conexion

st.title("Gestión de Platos")

conn = obtener_conexion()

categorias = pd.read_sql(
    "SELECT * FROM Categorias", conn
)

# Registrar nuevos platos en la base de datos
st.subheader("Registrar plato")

if not categorias.empty:
    nombre = st.text_input("Nombre del plato")
    categoria = st.selectbox(
        "Categoría",
        categorias["ID_Categoria"],
        format_func=lambda x: categorias.loc[
            categorias["ID_Categoria"] == x,
            "Nombre_Categoria"
        ].iloc[0]
    )
    precio = st.number_input("Precio unitario", min_value=0.0, step=1.0)
    disponibilidad = st.selectbox(
        "Disponibilidad", ["Disponible", "Agotado"]
    )

    if st.button("Registrar plato"):
        if nombre:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Platos
                (ID_Categoria, Nombre_Plato, Precio_Unitario, Disponibilidad)
                VALUES (%s, %s, %s, %s)
            """, (int(categoria), nombre, precio, disponibilidad))
            conn.commit()
            cursor.close()
            st.success("Plato registrado")
            st.rerun()
        else:
            st.warning("Ingresa el nombre del plato")
else:
    st.warning("Primero registra una categoría")

# Consultar y mostrar los platos con sus categorías
st.subheader("Consultar platos")

platos = pd.read_sql("""
    SELECT p.ID_Plato, p.Nombre_Plato, c.Nombre_Categoria,
           p.ID_Categoria, p.Precio_Unitario, p.Disponibilidad
    FROM Platos p
    JOIN Categorias c ON p.ID_Categoria = c.ID_Categoria
""", conn)

st.dataframe(platos, use_container_width=True)

if not platos.empty:

    # Actualizar los datos de un plato existente
    st.subheader("Actualizar plato")
    id_plato = st.selectbox("ID del plato", platos["ID_Plato"])
    fila = platos[platos["ID_Plato"] == id_plato].iloc[0]

    nuevo_nombre = st.text_input("Nuevo nombre", str(fila["Nombre_Plato"]))
    nuevo_precio = st.number_input(
        "Nuevo precio", min_value=0.0,
        value=float(fila["Precio_Unitario"]), step=1.0
    )
    nuevo_estado = st.selectbox(
        "Nuevo estado",
        ["Disponible", "Agotado"],
        index=["Disponible", "Agotado"].index(fila["Disponibilidad"])
    )

    if st.button("Actualizar plato"):
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Platos
            SET Nombre_Plato=%s, Precio_Unitario=%s, Disponibilidad=%s
            WHERE ID_Plato=%s
        """, (nuevo_nombre, nuevo_precio, nuevo_estado, int(id_plato)))
        conn.commit()
        cursor.close()
        st.success("Plato actualizado")
        st.rerun()

    # Eliminar un plato mediante su ID
    st.subheader("Eliminar plato")
    if st.button("Eliminar plato"):
        cursor = conn.cursor()
        try:
            cursor.execute(
                "DELETE FROM Platos WHERE ID_Plato=%s",
                (int(id_plato),)
            )
            conn.commit()
            st.success("Plato eliminado")
            st.rerun()
        except Exception:
            conn.rollback()
            st.error("No se puede eliminar: el plato puede tener pedidos")
        finally:
            cursor.close()

# Cerrar la conexión con la base de datos
conn.close()
