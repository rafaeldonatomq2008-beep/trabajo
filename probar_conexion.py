
from database import obtener_conexion

conexion = obtener_conexion()

if conexion:
    cursor = None

    try:
        cursor = conexion.cursor()

        sql = """
            DELETE FROM Categorias
            WHERE Nombre_Categoria = %s
        """

        valores = ("Bebidas",)

        cursor.execute(sql, valores)
        conexion.commit()

        if cursor.rowcount > 0:
            print("✅ Categoría eliminada correctamente.")
        else:
            print("⚠️ No se encontró esa categoría.")

    except Exception as e:
        conexion.rollback()
        print(f"❌ Error al eliminar la categoría: {e}")

    finally:
        if cursor:
            cursor.close()
        conexion.close()
else:
    print("❌ No se pudo conectar con MySQL.")
