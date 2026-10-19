import streamlit as st
from database import obtener_conexion

# Título de la página
st.title("Registro de Empleados")

# Campos para ingresar los datos del empleado
nombre = st.text_input("Nombre")
usuario = st.text_input("Usuario")
contrasena = st.text_input("Contraseña", type="password")
rol = st.selectbox("Rol", ["Administrador", "Mesero", "Cajero"])

# Registrar un nuevo empleado
if st.button("Registrar"):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    # Guarda los datos del empleado
    cursor.execute(
        "INSERT INTO EMPLEADOS (nombre, usuario, contrasena, rol) VALUES (%s, %s, %s, %s)",
        (nombre, usuario, contrasena, rol)
    )

    conexion.commit()
    conexion.close()
    st.success("Empleado registrado")
    st.rerun()

# Consultar todos los empleados registrados
conexion = obtener_conexion()
cursor = conexion.cursor()
cursor.execute("SELECT * FROM EMPLEADOS")
empleados = cursor.fetchall()
conexion.close()

# Mostrar los empleados en una tabla
st.subheader("Empleados registrados")
st.dataframe(empleados)

# Mostrar una lista para elegir qué empleado actualizar
if empleados:
    empleado = st.selectbox(
        "Seleccionar empleado para actualizar",
        empleados,
        format_func=lambda e: f"{e[0]} - {e[1]}"
    )

    # Mostrar los datos actuales del empleado seleccionado
    nuevo_nombre = st.text_input("Nuevo nombre", value=empleado[1])
    nuevo_usuario = st.text_input("Nuevo usuario", value=empleado[2])
    nuevo_rol = st.selectbox(
        "Nuevo rol",
        ["Administrador", "Mesero", "Cajero"],
        index=["Administrador", "Mesero", "Cajero"].index(empleado[4])
    )

    # Actualizar los datos del empleado seleccionado
    if st.button("Actualizar"):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            "UPDATE EMPLEADOS SET nombre=%s, usuario=%s, rol=%s WHERE idempleado=%s",
            (nuevo_nombre, nuevo_usuario, nuevo_rol, empleado[0])
        )

        conexion.commit()
        conexion.close()
        st.success("Empleado actualizado")
        st.rerun()