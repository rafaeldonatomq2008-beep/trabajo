import mysql.connector


def obtener_conexion():
    try:
        return mysql.connector.connect(
            host="168.232.167.152",
            user="root",
            password="root_dennis",
            database="sistema_restaurante",
            port=3306
        )
    except mysql.connector.Error as error:
        print("Error de conexión:", error)
        return None