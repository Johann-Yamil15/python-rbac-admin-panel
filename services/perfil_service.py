from config.database import get_connection
from models.perfil_model import Perfil

class PerfilService:
    @staticmethod
    def get_all():
        conn = get_connection()
        cursor = conn.cursor(as_dict=True)
        try:
            cursor.execute("SELECT id, strNombrePerfil, bitAdministrador FROM Perfil ORDER BY id DESC")
            rows = cursor.fetchall()
            return [Perfil.from_dict(r).to_dict() for r in rows]
        finally:
            conn.close()

    @staticmethod
    def get_by_id(id_perfil):
        conn = get_connection()
        cursor = conn.cursor(as_dict=True)
        try:
            cursor.execute("SELECT id, strNombrePerfil, bitAdministrador FROM Perfil WHERE id = %s", (id_perfil,))
            row = cursor.fetchone()
            return Perfil.from_dict(row).to_dict() if row else None
        finally:
            conn.close()

    @staticmethod
    def save(data):
        id_p = data.get('id')
        nombre = data.get('strNombrePerfil')
        # Convertimos el valor del checkbox o radio a bit (0 o 1)
        es_admin = 1 if data.get('bitAdministrador') in [True, 'True', '1', 'on'] else 0
        
        conn = get_connection()
        cursor = conn.cursor()
        try:
            if id_p: # UPDATE
                cursor.execute("""UPDATE Perfil SET strNombrePerfil=%s, bitAdministrador=%s 
                               WHERE id=%s""", (nombre, es_admin, id_p))
                msg = "Perfil actualizado"
            else: # INSERT
                cursor.execute("""INSERT INTO Perfil (strNombrePerfil, bitAdministrador) 
                               VALUES (%s, %s)""", (nombre, es_admin))
                msg = "Perfil registrado"
            conn.commit()
            return True, msg
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    @staticmethod
    def delete(id_perfil):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM Perfil WHERE id = %s", (id_perfil,))
            conn.commit()
            return True, "Perfil eliminado"
        except Exception as e:
            return False, "No se puede eliminar: el perfil está en uso"
        finally:
            conn.close()