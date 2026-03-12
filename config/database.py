# config/database.py
import pymssql
from config.settings import USE_LOCAL_DB, LOCAL_DB, CLOUD_DB


def get_connection():
    config = LOCAL_DB if USE_LOCAL_DB else CLOUD_DB

    return pymssql.connect(
        server=config["server"],
        user=config["user"],
        password=config["password"],
        database=config["database"],
    )


def load_settings():
    try:
        conn = get_connection()
        conn.close()
    except Exception as e:
        raise RuntimeError(f"Error de conexión a BD: {e}")


def test_connection():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT GETDATE()")
    fecha = cursor.fetchone()[0]
    conn.close()
    return fecha
