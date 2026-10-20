from database import obtener_conexion


class ClienteModel:
    
    @staticmethod
    def obtener_todos():
        """Obtiene todos los clientes de la base de datos."""
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("SELECT idcliente, nombre, telefono, direccion FROM CLIENTES")
        clientes = cursor.fetchall()
        conexion.close()
        return clientes

    @staticmethod
    def registrar(nombre, telefono, direccion):
        """Inserta un nuevo cliente en la base de datos."""
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            "INSERT INTO CLIENTES (nombre, telefono, direccion) VALUES (%s, %s, %s)",
            (nombre, telefono, direccion)
        )
        conexion.commit()
        conexion.close()

    @staticmethod
    def actualizar(idcliente, nombre, telefono, direccion):
        """Actualiza los datos de un cliente existente."""
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            "UPDATE CLIENTES SET nombre=%s, telefono=%s, direccion=%s WHERE idcliente=%s",
            (nombre, telefono, direccion, idcliente)
        )
        conexion.commit()
        conexion.close()