from database import obtener_conexion

conexion = obtener_conexion()

if conexion:
    print("✅ Conexión exitosa con MySQL.")
    conexion.close()
else:
    print("❌ No se pudo conectar con MySQL.")
