
import streamlit as st
import pandas as pd
from database import obtener_conexion

st.title("Gestión de Empleados")

conn = obtener_conexion()
cargos = ["Mesero", "Cajero", "Administrador", "Cocinero", "Recepcionista"]

st.subheader("Registrar empleado")
nombre = st.text_input("Nombre")
apellido = st.text_input("Apellido")
cargo = st.selectbox("Cargo", cargos)
telefono = st.text_input("Teléfono")

if st.button("Registrar empleado"):
    if nombre and apellido:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Empleados (Nombre, Apellido, Cargo, Telefono)
            VALUES (%s, %s, %s, %s)
        """, (nombre, apellido, cargo, telefono))
        conn.commit()
        cursor.close()
        st.success("Empleado registrado")
        st.rerun()
    else:
        st.warning("Ingresa nombre y apellido")

st.subheader("Consultar empleados")
empleados = pd.read_sql("SELECT * FROM Empleados", conn)
st.dataframe(empleados, use_container_width=True)

if not empleados.empty:
    st.subheader("Actualizar empleado")
    id_empleado = st.selectbox("ID del empleado", empleados["ID_Empleado"])
    fila = empleados[empleados["ID_Empleado"] == id_empleado].iloc[0]

    nuevo_nombre = st.text_input("Nuevo nombre", str(fila["Nombre"]))
    nuevo_apellido = st.text_input("Nuevo apellido", str(fila["Apellido"]))
    nuevo_cargo = st.selectbox(
        "Nuevo cargo", cargos, index=cargos.index(fila["Cargo"])
    )
    nuevo_telefono = st.text_input("Nuevo teléfono", str(fila["Telefono"] or ""))
    activo = st.checkbox("Empleado activo", value=bool(fila["Estado_Activo"]))

    if st.button("Actualizar empleado"):
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Empleados
            SET Nombre=%s, Apellido=%s, Cargo=%s,
                Telefono=%s, Estado_Activo=%s
            WHERE ID_Empleado=%s
        """, (nuevo_nombre, nuevo_apellido, nuevo_cargo,
              nuevo_telefono, activo, int(id_empleado)))
        conn.commit()
        cursor.close()
        st.success("Empleado actualizado")
        st.rerun()

    st.subheader("Eliminar empleado")
    if st.button("Eliminar empleado"):
        cursor = conn.cursor()
        try:
            cursor.execute(
                "DELETE FROM Empleados WHERE ID_Empleado=%s",
                (int(id_empleado),)
            )
            conn.commit()
            st.success("Empleado eliminado")
            st.rerun()
        except Exception:
            conn.rollback()
            st.error("No se puede eliminar: puede tener pedidos relacionados")
        cursor.close()

conn.close()
