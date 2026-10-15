
# Streamlit permite crear la interfaz gráfica del sistema
import streamlit as st

# Pandas permite mostrar los datos en tablas
import pandas as pd

# Permite establecer la conexión con MySQL
from database import obtener_conexion

st.title("Gestión de Pedidos y Comandas")

conn = obtener_conexion()

# Registrar pedidos seleccionando mesa, empleado, cliente y plato
st.subheader("Registrar pedido")

mesas = pd.read_sql(
    "SELECT * FROM Mesas WHERE Estado='Disponible'", conn
)
empleados = pd.read_sql(
    "SELECT * FROM Empleados WHERE Estado_Activo=TRUE", conn
)
clientes = pd.read_sql("SELECT * FROM Clientes", conn)
platos = pd.read_sql(
    "SELECT * FROM Platos WHERE Disponibilidad='Disponible'", conn
)

if not mesas.empty and not empleados.empty and not platos.empty:
    mesa = st.selectbox(
        "Mesa", mesas["ID_Mesa"],
        format_func=lambda x: mesas.loc[
            mesas["ID_Mesa"] == x, "Numero_Mesa"
        ].iloc[0]
    )

    empleado = st.selectbox(
        "Empleado", empleados["ID_Empleado"],
        format_func=lambda x: empleados.loc[
            empleados["ID_Empleado"] == x, "Nombre"
        ].iloc[0] + " " + empleados.loc[
            empleados["ID_Empleado"] == x, "Apellido"
        ].iloc[0]
    )

    cliente_opciones = [0] + list(clientes["ID_Cliente"])
    cliente = st.selectbox(
        "Cliente (opcional)", cliente_opciones,
        format_func=lambda x: "Sin cliente" if x == 0 else (
            clientes.loc[clientes["ID_Cliente"] == x, "Nombre"].iloc[0]
            + " " + clientes.loc[
                clientes["ID_Cliente"] == x, "Apellido"
            ].iloc[0]
        )
    )

    plato = st.selectbox(
        "Plato", platos["ID_Plato"],
        format_func=lambda x: platos.loc[
            platos["ID_Plato"] == x, "Nombre_Plato"
        ].iloc[0]
    )

    cantidad = st.number_input("Cantidad", min_value=1, step=1)
    precio = float(platos.loc[
        platos["ID_Plato"] == plato, "Precio_Unitario"
    ].iloc[0])

    st.write(f"Total: S/ {precio * cantidad:.2f}")

    if st.button("Registrar pedido"):
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO Pedidos (ID_Mesa, ID_Cliente, ID_Empleado)
                VALUES (%s, %s, %s)
            """, (
                int(mesa), int(cliente) if cliente != 0 else None,
                int(empleado)
            ))

            id_pedido = cursor.lastrowid

            cursor.execute("""
                INSERT INTO DetallePedido
                (ID_Pedido, ID_Plato, Cantidad, Precio_Unitario)
                VALUES (%s, %s, %s, %s)
            """, (id_pedido, int(plato), int(cantidad), precio))

            cursor.execute(
                "UPDATE Mesas SET Estado='Ocupada' WHERE ID_Mesa=%s",
                (int(mesa),)
            )

            conn.commit()
            st.success(f"Pedido registrado. Código: {id_pedido}")
            st.rerun()
        except Exception as e:
            conn.rollback()
            st.error(f"No se pudo registrar: {e}")
        finally:
            cursor.close()
else:
    st.warning("Necesitas mesas disponibles, empleados activos y platos disponibles")

# Consultar los pedidos registrados y calcular sus totales
st.subheader("Consultar pedidos")

pedidos = pd.read_sql("""
    SELECT p.ID_Pedido, p.Fecha_Hora, m.Numero_Mesa,
           p.Estado_Pedido, COALESCE(SUM(d.Subtotal), 0) AS Total
    FROM Pedidos p
    JOIN Mesas m ON p.ID_Mesa = m.ID_Mesa
    LEFT JOIN DetallePedido d ON p.ID_Pedido = d.ID_Pedido
    GROUP BY p.ID_Pedido, p.Fecha_Hora, m.Numero_Mesa, p.Estado_Pedido
    ORDER BY p.ID_Pedido DESC
""", conn)

st.dataframe(pedidos, use_container_width=True)

# Mostrar las comandas pendientes y en preparación
st.subheader("Comandas pendientes")

comandas = pd.read_sql("""
    SELECT p.ID_Pedido, m.Numero_Mesa, pl.Nombre_Plato,
           d.Cantidad, p.Estado_Pedido
    FROM Pedidos p
    JOIN Mesas m ON p.ID_Mesa = m.ID_Mesa
    JOIN DetallePedido d ON p.ID_Pedido = d.ID_Pedido
    JOIN Platos pl ON d.ID_Plato = pl.ID_Plato
    WHERE p.Estado_Pedido IN ('Pendiente', 'En Preparacion')
""", conn)

st.dataframe(comandas, use_container_width=True)

# Actualizar el estado de un pedido existente
st.subheader("Actualizar estado")

if not pedidos.empty:
    id_pedido = st.selectbox("Pedido a actualizar", pedidos["ID_Pedido"])
    estado = st.selectbox(
        "Estado",
        ["Pendiente", "En Preparacion", "Entregado", "Pagado", "Cancelado"]
    )

    if st.button("Actualizar pedido"):
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Pedidos SET Estado_Pedido=%s WHERE ID_Pedido=%s
        """, (estado, int(id_pedido)))
        conn.commit()
        cursor.close()
        st.success("Pedido actualizado")
        st.rerun()

# Cerrar la conexión con la base de datos
conn.close()
