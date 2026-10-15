
# Streamlit permite crear la interfaz gráfica del sistema
import streamlit as st

# Pandas permite mostrar los datos en tablas
import pandas as pd

# Permite establecer la conexión con MySQL
from database import obtener_conexion

st.title("Consultas y Reportes de Ventas")

conn = obtener_conexion()

# Consultar los ingresos diarios, semanales y mensuales
st.subheader("Ingresos por periodo")

periodo = st.selectbox(
    "Selecciona el periodo",
    ["Diario", "Semanal", "Mensual"]
)

if periodo == "Diario":
    agrupacion = "DATE(Fecha_Hora_Pago)"
elif periodo == "Semanal":
    agrupacion = "YEARWEEK(Fecha_Hora_Pago, 3)"
else:
    agrupacion = "DATE_FORMAT(Fecha_Hora_Pago, '%Y-%m')"

ventas = pd.read_sql(f"""
    SELECT {agrupacion} AS Periodo,
           COUNT(*) AS Numero_Pagos,
           SUM(Monto_Total) AS Ingresos
    FROM Pagos
    GROUP BY Periodo
    ORDER BY Periodo DESC
""", conn)

st.dataframe(ventas, use_container_width=True)

# Consultar los platos más vendidos del restaurante
st.subheader("Platos más vendidos")

platos = pd.read_sql("""
    SELECT pl.Nombre_Plato, SUM(d.Cantidad) AS Cantidad_Vendida
    FROM DetallePedido d
    JOIN Platos pl ON d.ID_Plato = pl.ID_Plato
    JOIN Pedidos p ON d.ID_Pedido = p.ID_Pedido
    WHERE p.Estado_Pedido = 'Pagado'
    GROUP BY pl.ID_Plato, pl.Nombre_Plato
    ORDER BY Cantidad_Vendida DESC
""", conn)

st.dataframe(platos, use_container_width=True)

# Consultar los ingresos según el método de pago
st.subheader("Ingresos por método de pago")

metodos = pd.read_sql("""
    SELECT Metodo_Pago, SUM(Monto_Total) AS Ingresos
    FROM Pagos
    GROUP BY Metodo_Pago
""", conn)

st.dataframe(metodos, use_container_width=True)

# Mostrar los ingresos mediante un gráfico de barras
if not metodos.empty:
    st.bar_chart(metodos.set_index("Metodo_Pago")["Ingresos"])

# Cerrar la conexión con la base de datos
conn.close()
