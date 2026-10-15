# Streamlit permite crear la interfaz gráfica del sistema
import streamlit as st

# Pandas permite mostrar los datos en tablas
import pandas as pd

# Permite establecer la conexión con MySQL
from database import obtener_conexion

st.title("Gestión de Pagos")

conn = obtener_conexion()

try:
    # ==========================================
    # 1. CONSULTAR PEDIDOS PENDIENTES DE PAGO
    # ==========================================
    st.subheader("Registrar pago")

    pedidos = pd.read_sql("""
        SELECT
            p.ID_Pedido,
            p.ID_Mesa,
            m.Numero_Mesa,
            p.Estado_Pedido,
            COALESCE(SUM(d.Subtotal), 0) AS Total
        FROM Pedidos p
        JOIN Mesas m
            ON p.ID_Mesa = m.ID_Mesa
        JOIN DetallePedido d
            ON p.ID_Pedido = d.ID_Pedido
        WHERE p.Estado_Pedido IN ('Entregado', 'Pagado')
          AND NOT EXISTS (
              SELECT 1
              FROM Pagos pg
              WHERE pg.ID_Pedido = p.ID_Pedido
          )
        GROUP BY
            p.ID_Pedido,
            p.ID_Mesa,
            m.Numero_Mesa,
            p.Estado_Pedido
        ORDER BY p.ID_Pedido ASC
    """, conn)

    if not pedidos.empty:

        st.info(
            "Selecciona un pedido entregado pendiente de pago. "
            "También aparecen los pedidos marcados como pagados "
            "que todavía no tienen un registro en la tabla Pagos."
        )

        id_pedido = st.selectbox(
            "Pedido",
            options=pedidos["ID_Pedido"].tolist(),
            format_func=lambda x: (
                f"Pedido {x} - Mesa "
                f"{pedidos.loc[
                    pedidos['ID_Pedido'] == x,
                    'Numero_Mesa'
                ].iloc[0]} - "
                f"{pedidos.loc[
                    pedidos['ID_Pedido'] == x,
                    'Estado_Pedido'
                ].iloc[0]}"
            )
        )

        fila = pedidos[
            pedidos["ID_Pedido"] == id_pedido
        ].iloc[0]

        total = float(fila["Total"])

        st.write(f"**Mesa:** {fila['Numero_Mesa']}")
        st.write(f"**Estado actual:** {fila['Estado_Pedido']}")
        st.write(f"**Importe a pagar: S/ {total:.2f}**")

        metodo = st.selectbox(
            "Método de pago",
            ["Efectivo", "Tarjeta", "Transferencia"]
        )

        confirmar = st.checkbox(
            "Confirmo que he recibido o verificado el pago real."
        )

        if st.button("Registrar pago"):

            if not confirmar:
                st.warning(
                    "Confirma que el pago se ha realizado "
                    "antes de registrarlo."
                )

            elif total <= 0:
                st.error(
                    "El importe debe ser mayor que cero. "
                    "Revisa los detalles del pedido."
                )

            else:
                cursor = conn.cursor()

                try:
                    # Comprobar que el pedido sigue sin pago
                    cursor.execute("""
                        SELECT Estado_Pedido
                        FROM Pedidos
                        WHERE ID_Pedido = %s
                        FOR UPDATE
                    """, (int(id_pedido),))

                    resultado = cursor.fetchone()

                    if resultado is None:
                        raise Exception("El pedido ya no existe.")

                    estado_actual = resultado[0]

                    if estado_actual not in ("Entregado", "Pagado"):
                        raise Exception(
                            "El pedido debe estar entregado "
                            "o pendiente de registrar un pago anterior."
                        )

                    # Evitar registrar dos pagos para el mismo pedido
                    cursor.execute("""
                        SELECT ID_Pedido
                        FROM Pagos
                        WHERE ID_Pedido = %s
                    """, (int(id_pedido),))

                    if cursor.fetchone() is not None:
                        raise Exception(
                            "Este pedido ya tiene un pago registrado."
                        )

                    # Registrar el pago
                    cursor.execute("""
                        INSERT INTO Pagos
                        (ID_Pedido, Metodo_Pago, Monto_Total)
                        VALUES (%s, %s, %s)
                    """, (
                        int(id_pedido),
                        metodo,
                        total
                    ))

                    # Marcar el pedido como pagado
                    cursor.execute("""
                        UPDATE Pedidos
                        SET Estado_Pedido = 'Pagado'
                        WHERE ID_Pedido = %s
                    """, (int(id_pedido),))

                    # Liberar la mesa si no tiene otros pedidos activos
                    id_mesa = int(fila["ID_Mesa"])

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

                    # Guardar todas las operaciones juntas
                    conn.commit()

                    st.success(
                        f"Pago registrado correctamente. "
                        f"Pedido: {id_pedido}. "
                        f"Importe: S/ {total:.2f}."
                    )

                    st.rerun()

                except Exception as e:
                    conn.rollback()
                    st.error(f"No se pudo registrar el pago: {e}")

                finally:
                    cursor.close()

    else:
        st.info(
            "No hay pedidos entregados pendientes de pago "
            "ni pedidos pagados con registros faltantes."
        )

    # ==========================================
    # 2. CONSULTAR PAGOS REGISTRADOS
    # ==========================================
    st.subheader("Consultar pagos")

    pagos = pd.read_sql("""
        SELECT *
        FROM Pagos
        ORDER BY Fecha_Hora_Pago DESC
    """, conn)

    if pagos.empty:
        st.info("Todavía no hay pagos registrados.")
    else:
        st.dataframe(pagos, use_container_width=True)

    # ==========================================
    # 3. RESUMEN DE INGRESOS
    # ==========================================
    st.subheader("Resumen de ingresos")

    resumen = pd.read_sql("""
        SELECT
            Metodo_Pago,
            COUNT(*) AS Cantidad_Pagos,
            SUM(Monto_Total) AS Total_Recaudado
        FROM Pagos
        GROUP BY Metodo_Pago
        ORDER BY Total_Recaudado DESC
    """, conn)

    if not resumen.empty:
        st.dataframe(resumen, use_container_width=True)

        total_recaudado = float(resumen["Total_Recaudado"].sum())

        st.metric(
            "Total recaudado",
            f"S/ {total_recaudado:.2f}"
        )
    else:
        st.info("No hay ingresos registrados para resumir.")

finally:
    conn.close()