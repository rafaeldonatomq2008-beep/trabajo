import mysql.connector
from mysql.connector import Error


def obtener_conexion():
    """Establece la conexión con la base de datos MySQL."""
    try:
        conexion = mysql.connector.connect(
            host="168.232.167.152",
            user="root",
            password="root_dennis",
            database="restaurante_db",
            port=3306
        )

        if conexion.is_connected():
            return conexion

    except Error as error:
        print(f"Error al conectar con MySQL: {error}")

    return None