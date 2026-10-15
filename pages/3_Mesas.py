
# Streamlit permite crear la interfaz gráfica del sistema
import streamlit as st

# Pandas permite mostrar los datos en tablas
import pandas as pd

# Permite establecer la conexión con MySQL
from database import obtener_conexion

st.title("Administración de Mesas")

conn = obtener_conexion()

# Registrar nuevas mesas en la base de datos
st.subheader("Registrar mesa")
numero = st.number_input("Número de mesa", min_value=1, step=1)
capacidad = st.number_input("Capacidad", min_value=1, step=1)

if st.button("Registrar mesa"):
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO Mesas (Numero_Mesa, Capacidad)
            VALUES (%s, %s)
        """, (numero, capacidad))
        conn.commit()
        st.success("Mesa registrada")
        st.rerun()
    except Exception:
        conn.rollback()
        st.error("No se pudo registrar. Puede que el número ya exista.")
    finally:
        cursor.close()

# Consultar y mostrar las mesas registradas
st.subheader("Consultar mesas")
mesas = pd.read_sql("SELECT * FROM Mesas", conn)
st.dataframe(mesas, use_container_width=True)

if not mesas.empty:

    # Actualizar el estado de una mesa existente
    st.subheader("Actualizar estado")
    id_mesa = st.selectbox("Mesa", mesas["ID_Mesa"])
    estado = st.selectbox(
        "Estado",
        ["Disponible", "Ocupada", "Reservada", "Mantenimiento"]
    )

    if st.button("Actualizar estado"):
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE Mesas SET Estado=%s WHERE ID_Mesa=%s",
            (estado, int(id_mesa))
        )
        conn.commit()
        cursor.close()
        st.success("Estado actualizado")
        st.rerun()

    # Eliminar una mesa mediante su ID
    st.subheader("Eliminar mesa")
    id_eliminar = st.selectbox(
        "Mesa que deseas eliminar",
        mesas["ID_Mesa"],
        key="eliminar_mesa"
    )

    if st.button("Eliminar mesa"):
        cursor = conn.cursor()
        try:
            cursor.execute(
                "DELETE FROM Mesas WHERE ID_Mesa=%s",
                (int(id_eliminar),)
            )
            conn.commit()
            st.success("Mesa eliminada")
            st.rerun()
        except Exception:
            conn.rollback()
            st.error("No se puede eliminar: la mesa puede tener pedidos")
        finally:
            cursor.close()

# Cerrar la conexión con la base de datos
conn.close()
