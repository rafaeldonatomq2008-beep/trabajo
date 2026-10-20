from database import obtener_conexion

class Cliente:

    def __init__(self, idcliente=None, nombre="", telefono="", direccion=""):
        self.idcliente = idcliente
        self.nombre = nombre
        self.telefono = telefono
        self.direccion = direccion

    def __str__(self):
        return f"{self.idcliente} - {self.nombre}"

    @staticmethod
    def obtener_todos():
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("SELECT * FROM CLIENTES")
        filas = cursor.fetchall()

        conexion.close()

        clientes = []

        for f in filas:
            cliente = Cliente(f[0], f[1], f[2], f[3])
            clientes.append(cliente)

        return clientes

    def registrar(self):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        sql = "INSERT INTO CLIENTES (nombre, telefono, direccion) VALUES (%s, %s, %s)"
        datos = (self.nombre, self.telefono, self.direccion)

        cursor.execute(sql, datos)
        conexion.commit()
        conexion.close()

    def actualizar(self):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        sql = "UPDATE CLIENTES SET nombre=%s, telefono=%s, direccion=%s WHERE idcliente=%s"
        datos = (self.nombre, self.telefono, self.direccion, self.idcliente)

        cursor.execute(sql, datos)
        conexion.commit()
        conexion.close()
