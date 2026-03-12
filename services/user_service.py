import os
import uuid
import hashlib
from config.database import get_connection
from models.user_model import User

UPLOAD_DIR = "static/Images/users"
WEB_PATH = "/static/Images/users"
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


class UserService:

    @staticmethod
    def save_profile_image(file):
        print(f"\n[DEBUG IMAGE] Analizando archivo: {file}")
        if not file or not file.filename:
            print("[DEBUG IMAGE] Resultado: No hay archivo o filename vacío.")
            return None

        print(f"[DEBUG IMAGE] Nombre original: {file.filename}")
        ext = os.path.splitext(file.filename)[1].lower()
        
        if ext not in ALLOWED_EXTENSIONS:
            print(f"[DEBUG IMAGE] Resultado: Extensión {ext} no permitida.")
            return None

        os.makedirs(UPLOAD_DIR, exist_ok=True)
        unique_name = f"user_{uuid.uuid4().hex}{ext}"
        real_path = os.path.join(UPLOAD_DIR, unique_name)
        
        # Guardamos con backslash para que coincida con tu ejemplo de Windows
        web_path = f"static\\Images\\users\\{unique_name}"

        try:
            file.save(real_path)
            print(f"[DEBUG IMAGE] ¡ÉXITO! Guardado en disco: {real_path}")
            print(f"[DEBUG IMAGE] Ruta para BD: {web_path}")
            return web_path
        except Exception as e:
            print(f"[DEBUG IMAGE] ERROR CRÍTICO al guardar: {e}")
            return None

    @staticmethod
    def get_all_users():
        print("\n--- INICIANDO GET_ALL_USERS ---")
        conn = get_connection()
        # Usamos as_dict=True para que coincida con el from_dict del modelo
        cursor = conn.cursor(as_dict=True)
        try:
            # Seleccionamos de la tabla 'Usuario' (nueva estructura)
            cursor.execute("SELECT * FROM Usuario ORDER BY id DESC")
            rows = cursor.fetchall()

            users_list = []
            for row in rows:
                obj = User.from_dict(row)
                users_list.append(obj.to_dict())

            return users_list
        except Exception as e:
            print(f" ERROR en get_all_users: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def register_user(user_data, file=None):
        print("\n" + "="*40)
        print("--- DEBUG REGISTER_USER ---")
        print(f"1. Datos recibidos (user_data): {user_data}")
        
        # 1. Intentar guardar imagen primero
        imagen_db_path = UserService.save_profile_image(file)
        print(f"2. Ruta de imagen generada: {imagen_db_path}")

        # 2. Mapear al modelo
        user = User.from_dict(user_data)
        print(f"3. Usuario mapeado (Nombre): {user.nombre} {user.ap}")

        # 3. Hashear pwd
       
        pwd = user_data.get('strPwd') or ""
        print(f"\n[UserService] ➡️ password: '{pwd}'")
        password_hash = hashlib.sha256(pwd.encode()).hexdigest()
        print(f"\n[UserService] ➡️ password hash: '{password_hash[:15]}...'")

        conn = get_connection()
        cursor = conn.cursor()
        try:
            query = """INSERT INTO Usuario 
                       (Nombre, ApellidoP, ApellidoM, idPerfil, strPwd, FechaNacimiento, 
                        idEstadoUsuario, idSexo, strCorreo, strNumeroCelular, strImagenPath, FechaRegistro) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, GETDATE())"""

            params = (
                user.nombre, user.ap, user.am, user.id_perfil, password_hash,
                user.fecha_nac, user.id_estado or 1, user.id_sexo, user.email, user.celular,
                imagen_db_path  # <--- Verificamos que no sea None
            )

            print(f"4. SQL Params (Imagen es la penúltima): {params}")
            cursor.execute(query, params)
            conn.commit()
            print("5. ¡Registro exitoso en Base de Datos!")
            return True, "Usuario registrado exitosamente"
        except Exception as e:
            print(f" !!! ERROR SQL: {e}")
            return False, str(e)
        finally:
            conn.close()
            print("="*40)

    @staticmethod
    def get_user_by_id(user_id):
        conn = get_connection()
        cursor = conn.cursor(as_dict=True)
        try:
            cursor.execute("SELECT * FROM Usuario WHERE id = %s", (user_id,))
            row = cursor.fetchone()
            if row:
                return User.from_dict(row).to_dict()
            return None
        except Exception as e:
            print(f" ERROR en get_user_by_id: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def update_existing_user(user_data, file=None):
        print("\n--- INICIANDO UPDATE ---")
        user = User.from_dict(user_data)

        # 1. Guardar nueva imagen (si viene una)
        nueva_imagen = UserService.save_profile_image(file)

        # 2. Extraer contraseña y limpiar espacios vacíos accidentales
        pwd = user_data.get('strPwd', '').strip()
        password_hash = None
        
        if pwd:
            # Si el campo NO está vacío, generamos el hash
            password_hash = hashlib.sha256(pwd.encode()).hexdigest()
            print(f"[DEBUG UPDATE] 🔑 Nueva contraseña detectada. Hash: {password_hash[:15]}...")
        else:
            print("[DEBUG UPDATE] 🔒 Contraseña en blanco. Se conservará la que ya tiene.")

        conn = get_connection()
        cursor = conn.cursor()
        try:
            # 3. Construimos la consulta base (los campos que SIEMPRE se actualizan)
            query = """UPDATE Usuario SET 
                       Nombre=%s, ApellidoP=%s, ApellidoM=%s, idPerfil=%s, 
                       FechaNacimiento=%s, idEstadoUsuario=%s, idSexo=%s, 
                       strCorreo=%s, strNumeroCelular=%s"""
            
            # Sus respectivos valores en una lista
            params = [user.nombre, user.ap, user.am, user.id_perfil,
                      user.fecha_nac, user.id_estado, user.id_sexo,
                      user.email, user.celular]

            # 4. Si hay imagen nueva, la agregamos a la consulta
            if nueva_imagen:
                query += ", strImagenPath=%s"
                params.append(nueva_imagen)

            # 5. Si hay contraseña nueva, la agregamos a la consulta
            if password_hash:
                query += ", strPwd=%s"
                params.append(password_hash)

            # 6. Rematamos la consulta con el WHERE
            query += " WHERE id=%s"
            params.append(user.id)

            print(f"[DEBUG UPDATE] Ejecutando SQL con {len(params)} parámetros...")
            
            # Ejecutamos pasando la lista convertida en tupla
            cursor.execute(query, tuple(params))
            conn.commit()
            print("[DEBUG UPDATE] ✅ ¡Usuario actualizado correctamente en la BD!")
            return True, "Usuario actualizado correctamente"
            
        except Exception as e:
            print(f"🔥 [DEBUG UPDATE] ERROR SQL: {e}")
            return False, str(e)
        finally:
            conn.close()

    @staticmethod
    def delete_user(user_id):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM Usuario WHERE id = %s", (user_id,))
            conn.commit()
            return True, "Usuario eliminado correctamente"
        except Exception as e:
            print(f" ERROR en delete: {e}")
            return False, str(e)
        finally:
            conn.close()
