from config.database import get_connection

def get_home_data():
    try:
        conn = get_connection()
        cursor = conn.cursor(as_dict=True) # as_dict ayuda mucho para el render
        
        # Ejemplo: obtener fecha del servidor y quizás un conteo
        cursor.execute("SELECT GETDATE() as fecha, DB_NAME() as db_actual")
        resultado = cursor.fetchone()
        
        conn.close()
        return {
            "fecha_bd": resultado['fecha'],
            "online": True  # <--- Indicador de éxito
        }
    except Exception as e:
        print(f"Error en servicio: {e}")
        return {
            "fecha_bd": "N/A", 
            "online": False # <--- Indicador de fallo
        }