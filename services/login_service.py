import hashlib
import jwt
from datetime import datetime, timedelta
from config.database import get_connection
from models.user_model import User

SECRET_KEY = "d8f7a6g5h4j3k2l1m0n9b8v7c6x5z4q3w2e1r0t9y8u7i6o5p4"

class LoginService:
    @staticmethod
    def authenticate_user(email, password):
        print(f"\n[LOGIN] ➡️ Iniciando intento de autenticación para: '{email}'")
        print(f"\n[LOGIN] ➡️ password: '{password}'")
        
        # Hashear la contraseña ingresada para compararla con la BD
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        print(f"[LOGIN] 🔑 Hash generado (primeros 15 chars): {password_hash[:15]}...")
        
        conn = get_connection()
        cursor = conn.cursor(as_dict=True)
        try:
            print("[LOGIN] ⏳ Consultando la base de datos...")
            # Buscamos al usuario por correo e incluimos el estado para saber si está activo
            cursor.execute("""
                SELECT * FROM Usuario 
                WHERE strCorreo = %s AND strPwd = %s 
            """, (email, password_hash))
            row = cursor.fetchone()
            
            if row:
                print(f"[LOGIN] ✅ ¡Éxito! Usuario encontrado en la BD. ID: {row.get('idUsuario')}")
                user = User.from_dict(row)
                
                # Crear el payload del JWT con los datos necesarios para el Layout
                payload = {
                    "id": user.id,
                    "email": user.email,
                    "nombre_completo": f"{user.nombre} {user.ap}".strip(),
                    "id_perfil": user.id_perfil,
                    "iniciales": f"{user.nombre[0]}{user.ap[0]}".upper() if user.nombre and user.ap else "U",
                    "exp": datetime.utcnow() + timedelta(hours=8) # El token expira en 8 horas
                }
                print(f"[LOGIN] 📦 Payload preparado para JWT: Perfil {user.id_perfil}")
                
                token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
                print("[LOGIN] 🎟️ Token JWT generado correctamente. Retornando éxito.")
                
                return True, "Login exitoso", token, payload
            else:
                print(f"[LOGIN] ❌ Fallo de autenticación. Credenciales incorrectas para '{email}'.")
                return False, "Correo o contraseña incorrectos, o usuario inactivo", None, None
                
        except Exception as e:
            print(f"🔥 [LOGIN] ERROR CRÍTICO en authenticate_user: {e}")
            return False, "Error interno del servidor", None, None
        finally:
            conn.close()
            print("[LOGIN] 🔌 Conexión a la base de datos cerrada.\n")