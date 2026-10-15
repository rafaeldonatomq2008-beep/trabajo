# Streamlit permite crear la interfaz gráfica del sistema
import streamlit as st

# Pandas permite mostrar los datos en tablas
import pandas as pd

# Permite establecer la conexión con MySQL
from database import obtener_conexion

st.title("Gestión de Pedidos y Comandas")

conn = obtener_conexion()

try:
    # ==========================================
    # 1. REGISTRAR PEDIDO
    # ==========================================
    st.subheader("Registrar pedido")

    mesas = pd.read_sql("""
        SELECT ID_Mesa, Numero_Mesa
        FROM Mesas
        WHERE Estado = 'Disponible'
        ORDER BY Numero_Mesa ASC
    """, conn)

    empleados = pd.read_sql("""
        SELECT ID_Empleado, Nombre, Apellido
        FROM Empleados
        WHERE Estado_Activo = TRUE
        ORDER BY Apellido ASC
    """, conn)

    clientes = pd.read_sql("""
        SELECT ID_Cliente, Nombre, Apellido
        FROM Clientes
        ORDER BY Apellido ASC
    """, conn)

    platos = pd.read_sql("""
        SELECT ID_Plato, Nombre_Plato, Precio_Unitario
        FROM Platos
        WHERE Disponibilidad = 'Disponible'
        ORDER BY Nombre_Plato ASC
    """, conn)

    if not mesas.empty and not empleados.empty and not platos.empty:

        # Seleccionar mesa
        mesa = st.selectbox(
            "Mesa",
            options=mesas["ID_Mesa"].tolist(),
            format_func=lambda x: (
                "Mesa " + str(
                    mesas.loc[
                        mesas["ID_Mesa"] == x, "Numero_Mesa"
                    ].iloc[0]
                )
            )
        )

        # Seleccionar empleado
        empleado = st.selectbox(
            "Empleado",
            options=empleados["ID_Empleado"].tolist(),
            format_func=lambda x: (
                empleados.loc[
                    empleados["ID_Empleado"] == x, "Nombre"
                ].iloc[0]
                + " "
                + empleados.loc[
                    empleados["ID_Empleado"] == x, "Apellido"
                ].iloc[0]
            )
        )

        # Seleccionar cliente (opcional)
        cliente_opciones = [0] + clientes["ID_Cliente"].tolist()

        def mostrar_cliente(x):
            if x == 0:
                return "Sin cliente"

            fila = clientes.loc[
                clientes["ID_Cliente"] == x
            ].iloc[0]

            return fila["Nombre"] + " " + fila["Apellido"]

        cliente = st.selectbox(
            "Cliente (opcional)",
            options=cliente_opciones,
            format_func=mostrar_cliente
        )

        # Seleccionar plato
        plato = st.selectbox(
            "Plato",
            options=platos["ID_Plato"].tolist(),
            format_func=lambda x: platos.loc[
                platos["ID_Plato"] == x, "Nombre_Plato"
            ].iloc[0]
        )

        # Cantidad y precio
        cantidad = st.number_input(
            "Cantidad",
            min_value=1,
            step=1
        )

        precio = float(
            platos.loc[
                platos["ID_Plato"] == plato,
                "Precio_Unitario"
            ].iloc[0]
        )

        total = precio * cantidad

        st.write(f"Precio unitario: S/ {precio:.2f}")
        st.write(f"Total del pedido: S/ {total:.2f}")

        if st.button("Registrar pedido"):

            cursor = conn.cursor()

            try:
                # Crear el pedido
                cursor.execute("""
                    INSERT INTO Pedidos
                    (ID_Mesa, ID_Cliente, ID_Empleado)
                    VALUES (%s, %s, %s)
                """, (
                    int(mesa),
                    int(cliente) if cliente != 0 else None,
                    int(empleado)
                ))

                id_pedido = cursor.lastrowid

                # Registrar el detalle del pedido
                cursor.execute("""
                    INSERT INTO DetallePedido
                    (ID_Pedido, ID_Plato, Cantidad, Precio_Unitario)
                    VALUES (%s, %s, %s, %s)
                """, (
                    id_pedido,
                    int(plato),
                    int(cantidad),
                    precio
                ))

                # Ocupar la mesa
                cursor.execute("""
                    UPDATE Mesas
                    SET Estado = 'Ocupada'
                    WHERE ID_Mesa = %s
                """, (int(mesa),))

                conn.commit()

                st.success(
                    f"Pedido registrado correctamente. "
                    f"Código: {id_pedido}"
                )

                st.rerun()

            except Exception as e:
                conn.rollback()
                st.error(f"No se pudo registrar el pedido: {e}")

            finally:
                cursor.close()

    else:
        st.warning(
            "Necesitas al menos una mesa disponible, "
            "un empleado activo y un plato disponible."
        )

    # ==========================================
    # 2. CONSULTAR PEDIDOS
    # ==========================================
    st.subheader("Consultar pedidos")

    pedidos = pd.read_sql("""
        SELECT
            p.ID_Pedido,
            p.Fecha_Hora,
            m.Numero_Mesa,
            p.Estado_Pedido,
            COALESCE(SUM(d.Subtotal), 0) AS Total
        FROM Pedidos p
        JOIN Mesas m
            ON p.ID_Mesa = m.ID_Mesa
        LEFT JOIN DetallePedido d
            ON p.ID_Pedido = d.ID_Pedido
        GROUP BY
            p.ID_Pedido,
            p.Fecha_Hora,
            m.Numero_Mesa,
            p.Estado_Pedido
        ORDER BY p.ID_Pedido DESC
    """, conn)

    st.dataframe(pedidos, use_container_width=True)

    # ==========================================
    # 3. CONSULTAR COMANDAS
    # ==========================================
    st.subheader("Comandas pendientes")

    comandas = pd.read_sql("""
        SELECT
            p.ID_Pedido,
            m.Numero_Mesa,
            pl.Nombre_Plato,
            d.Cantidad,
            p.Estado_Pedido
        FROM Pedidos p
        JOIN Mesas m
            ON p.ID_Mesa = m.ID_Mesa
        JOIN DetallePedido d
            ON p.ID_Pedido = d.ID_Pedido
        JOIN Platos pl
            ON d.ID_Plato = pl.ID_Plato
        WHERE p.Estado_Pedido IN (
            'Pendiente',
            'En Preparacion'
        )
        ORDER BY p.ID_Pedido ASC
    """, conn)

    if comandas.empty:
        st.info("No hay comandas pendientes de preparación.")
    else:
        st.dataframe(comandas, use_container_width=True)

    # ==========================================
    # 4. ACTUALIZAR ESTADO DEL PEDIDO
    # ==========================================
    st.subheader("Actualizar estado del pedido")

    # No permitir marcar Pagado desde este módulo.
    # Los pedidos pagados o cancelados no se modifican aquí.
    pedidos_actualizables = pedidos[
        ~pedidos["Estado_Pedido"].isin(["Pagado", "Cancelado"])
    ]

    if not pedidos_actualizables.empty:

        id_pedido = st.selectbox(
            "Pedido a actualizar",
            options=pedidos_actualizables["ID_Pedido"].tolist(),
            format_func=lambda x: (
                f"Pedido {x} - "
                f"{pedidos_actualizables.loc[
                    pedidos_actualizables['ID_Pedido'] == x,
                    'Estado_Pedido'
                ].iloc[0]}"
            )
        )

        estado_actual = pedidos_actualizables.loc[
            pedidos_actualizables["ID_Pedido"] == id_pedido,
            "Estado_Pedido"
        ].iloc[0]

        estados = [
            "Pendiente",
            "En Preparacion",
            "Entregado",
            "Cancelado"
        ]

        estado = st.selectbox(
            "Nuevo estado",
            options=estados,
            index=(
                estados.index(estado_actual)
                if estado_actual in estados else 0
            )
        )

        if st.button("Actualizar pedido"):

            cursor = conn.cursor()

            try:
                cursor.execute("""
                    UPDATE Pedidos
                    SET Estado_Pedido = %s
                    WHERE ID_Pedido = %s
                      AND Estado_Pedido NOT IN ('Pagado', 'Cancelado')
                """, (estado, int(id_pedido)))

                # Si se cancela, liberar la mesa solamente
                # cuando no queden otros pedidos activos.
                if estado == "Cancelado":

                    cursor.execute("""
                        SELECT ID_Mesa
                        FROM Pedidos
                        WHERE ID_Pedido = %s
                    """, (int(id_pedido),))

                    resultado = cursor.fetchone()
                    id_mesa = resultado[0]

                    cursor.execute("""
                        UPDATE Mesas
                        SET Estado = 'Disponible'
                        WHERE ID_Mesa = %s
                          AND NOT EXISTS (
                              SELECT 1
                              FROM Pedidos
                              WHERE ID_Mesa = %s
                                AND Estado_Pedido NOT IN (
                                    'Pagado',
                                    'Cancelado'
                                )
                          )
                    """, (id_mesa, id_mesa))

                conn.commit()

                st.success("Estado del pedido actualizado.")
                st.rerun()

            except Exception as e:
                conn.rollback()
                st.error(f"No se pudo actualizar el pedido: {e}")

            finally:
                cursor.close()

    else:
        st.info("No hay pedidos pendientes de actualización.")

finally:
    conn.close()