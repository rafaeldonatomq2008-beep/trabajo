from models.cliente_model import ClienteModel

class ClienteController:
    
    @staticmethod
    def listar_clientes():
        """Devuelve la lista de clientes obtenida del modelo."""
        return ClienteModel.obtener_todos()

    @staticmethod
    def registrar_cliente(nombre, telefono, direccion):
        """Valida e intenta registrar un nuevo cliente."""
        if not nombre or not nombre.strip():
            return False, "El nombre del cliente es obligatorio."
        
        try:
            ClienteModel.registrar(nombre, telefono, direccion)
            return True, "Cliente registrado exitosamente."
        except Exception as e:
            return False, f"Error al registrar en la base de datos: {e}"

    @staticmethod
    def actualizar_cliente(idcliente, nombre, telefono, direccion):
        """Valida e intenta actualizar un cliente."""
        if not nombre or not nombre.strip():
            return False, "El nombre del cliente no puede estar vacío."
        
        try:
            ClienteModel.actualizar(idcliente, nombre, telefono, direccion)
            return True, "Cliente actualizado exitosamente."
        except Exception as e:
            return False, f"Error al actualizar en la base de datos: {e}"