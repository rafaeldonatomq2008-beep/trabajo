
# Streamlit permite crear la interfaz gráfica del sistema
import streamlit as st

# Pandas permite mostrar los datos en tablas
import pandas as pd

# Permite establecer la conexión con MySQL
from database import obtener_conexion

st.title("Gestión de Clientes")

conn = obtener_conexion()

# Registrar nuevos clientes en la base de datos
st.subheader("Registrar cliente")

nombre = st.text_input("Nombre")
apellido = st.text_input("Apellido")
telefono = st.text_input("Teléfono")
direccion = st.text_input("Dirección")
correo = st.text_input("Correo")

if st.button("Registrar cliente"):
    if nombre and apellido:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Clientes
            (Nombre, Apellido, Telefono, Direccion, Correo)
            VALUES (%s, %s, %s, %s, %s)
        """, (nombre, apellido, telefono, direccion, correo))
        conn.commit()
        cursor.close()
        st.success("Cliente registrado")
        st.rerun()
    else:
        st.warning("Ingresa nombre y apellido")


# Consultar y mostrar los clientes registrados
st.subheader("Consultar clientes")

clientes = pd.read_sql("SELECT * FROM Clientes", conn)
st.dataframe(clientes, use_container_width=True)


# Actualizar los datos de un cliente existente
st.subheader("Actualizar cliente")

if not clientes.empty:
    id_cliente = st.selectbox("ID del cliente", clientes["ID_Cliente"])
    fila = clientes[clientes["ID_Cliente"] == id_cliente].iloc[0]

    nuevo_nombre = st.text_input("Nuevo nombre", str(fila["Nombre"]))
    nuevo_apellido = st.text_input("Nuevo apellido", str(fila["Apellido"]))
    nuevo_telefono = st.text_input("Nuevo teléfono", str(fila["Telefono"] or ""))
    nueva_direccion = st.text_input("Nueva dirección", str(fila["Direccion"] or ""))
    nuevo_correo = st.text_input("Nuevo correo", str(fila["Correo"] or ""))

    if st.button("Actualizar cliente"):
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Clientes
            SET Nombre=%s, Apellido=%s, Telefono=%s,
                Direccion=%s, Correo=%s
            WHERE ID_Cliente=%s
        """, (nuevo_nombre, nuevo_apellido, nuevo_telefono,
              nueva_direccion, nuevo_correo, int(id_cliente)))
        conn.commit()
        cursor.close()
        st.success("Cliente actualizado")
        st.rerun()

    # Eliminar un cliente mediante su ID
    st.subheader("Eliminar cliente")

    if st.button("Eliminar cliente"):
        cursor = conn.cursor()
        try:
            cursor.execute(
                "DELETE FROM Clientes WHERE ID_Cliente=%s",
                (int(id_cliente),)
            )
            conn.commit()
            st.success("Cliente eliminado")
            st.rerun()
        except Exception:
            conn.rollback()
            st.error("No se puede eliminar: puede tener pedidos relacionados")
        cursor.close()

# Cerrar la conexión con la base de datos
conn.close()
