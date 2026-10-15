
# Streamlit permite crear la interfaz gráfica del sistema
import streamlit as st

# Pandas permite mostrar los datos en tablas
import pandas as pd

# Permite establecer la conexión con MySQL
from database import obtener_conexion

st.title("Gestión de Pagos")

conn = obtener_conexion()

# Registrar pagos de pedidos entregados y pendientes de pago
st.subheader("Registrar pago")

pedidos = pd.read_sql("""
    SELECT p.ID_Pedido, p.ID_Mesa,
           SUM(d.Subtotal) AS Total
    FROM Pedidos p
    JOIN DetallePedido d ON p.ID_Pedido = d.ID_Pedido
    WHERE p.Estado_Pedido = 'Entregado'
      AND NOT EXISTS (
          SELECT 1 FROM Pagos pg WHERE pg.ID_Pedido = p.ID_Pedido
      )
    GROUP BY p.ID_Pedido, p.ID_Mesa
""", conn)

if not pedidos.empty:
    id_pedido = st.selectbox("Pedido", pedidos["ID_Pedido"])

    fila = pedidos[pedidos["ID_Pedido"] == id_pedido].iloc[0]
    total = float(fila["Total"])

    st.write(f"Importe a pagar: S/ {total:.2f}")

    metodo = st.selectbox(
        "Método de pago",
        ["Efectivo", "Tarjeta", "Transferencia"]
    )

    if st.button("Registrar pago"):
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO Pagos (ID_Pedido, Metodo_Pago, Monto_Total)
                VALUES (%s, %s, %s)
            """, (int(id_pedido), metodo, total))

            # Actualizar el pedido a Pagado y liberar la mesa si corresponde
            cursor.execute("""
                UPDATE Pedidos SET Estado_Pedido='Pagado'
                WHERE ID_Pedido=%s
            """, (int(id_pedido),))

            cursor.execute("""
                UPDATE Mesas SET Estado='Disponible'
                WHERE ID_Mesa=%s
                  AND NOT EXISTS (
                      SELECT 1 FROM Pedidos
                      WHERE ID_Mesa=%s
                        AND Estado_Pedido NOT IN ('Pagado', 'Cancelado')
                  )
            """, (int(fila["ID_Mesa"]), int(fila["ID_Mesa"])))

            conn.commit()
            st.success("Pago registrado")
            st.rerun()

        except Exception as e:
            conn.rollback()
            st.error(f"No se pudo registrar el pago: {e}")
        finally:
            cursor.close()
else:
    st.info("No hay pedidos entregados pendientes de pago")

# Consultar y mostrar los pagos registrados
st.subheader("Consultar pagos")

pagos = pd.read_sql("""
    SELECT * FROM Pagos ORDER BY Fecha_Hora_Pago DESC
""", conn)

st.dataframe(pagos, use_container_width=True)

# Cerrar la conexión con la base de datos
conn.close()
