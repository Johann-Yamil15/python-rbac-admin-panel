from config.database import get_connection

class CatalogoService:
    @staticmethod
    def get_catalog(table_name, order_by="id"):
        """Método genérico para obtener datos de cualquier tabla de catálogo"""
        print(f"\n--- [DEBUG] CatalogoService: Solicitando tabla '{table_name}' ---")
        
        conn = get_connection()
        if not conn:
            print(f"!!! [ERROR] No se pudo establecer conexión a la BD para '{table_name}'")
            return []

        cursor = conn.cursor(as_dict=True)
        try:
            query = f"SELECT * FROM {table_name} ORDER BY {order_by}"
            print(f"-> Ejecutando SQL: {query}")
            
            cursor.execute(query)
            result = cursor.fetchall()
            
            print(f"-> Éxito: Se obtuvieron {len(result)} registros de '{table_name}'.")
            
            # Print del primer registro para verificar nombres de columnas en consola
            if len(result) > 0:
                print(f"-> Muestra del primer registro: {result[0]}")
            
            return result
        except Exception as e:
            print(f"!!! [ERROR] Falló la consulta en '{table_name}': {str(e)}")
            return []
        finally:
            print(f"--- [DEBUG] Cerrando conexión de '{table_name}' ---\n")
            conn.close()

    @staticmethod
    def get_sexos():
        print("Llamada a: get_sexos()")
        return CatalogoService.get_catalog("Sexo", "strSexo")

    @staticmethod
    def get_estados():
        print("Llamada a: get_estados()")
        return CatalogoService.get_catalog("EstadoUsuario", "strNombreEstado")

    @staticmethod
    def get_perfiles():
        print("Llamada a: get_perfiles()")
        # Si tu columna ID se llama distinto, el ORDER BY "id" fallará. 
        # Aquí lo forzamos por nombre para evitar errores.
        return CatalogoService.get_catalog("Perfil", "strNombrePerfil")
    
    @staticmethod
    def get_modulos():
        print("Llamada a: get_modulos()")
        return CatalogoService.get_catalog("Modulo", "strNombreModulo")
  
    @staticmethod
    def get_menus():
        print("Llamada a: get_menus()")
        return CatalogoService.get_catalog("Menu", "strNombreMenu")