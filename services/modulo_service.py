from config.database import get_connection


class ModuloService:
    @staticmethod
    def get_all():
        conn = get_connection()
        cursor = conn.cursor(as_dict=True)
        try:
            # Join para traer también el nombre del Menú padre
            cursor.execute("""
                SELECT MO.id, MO.strNombreModulo, MO.idMenu, ME.strNombreMenu, MO.strRuta 
                FROM Modulo MO
                INNER JOIN Menu ME ON MO.idMenu = ME.id
                ORDER BY MO.id DESC
            """)
            return cursor.fetchall()
        finally:
            conn.close()

    @staticmethod
    def get_by_id(id_modulo):
        conn = get_connection()
        cursor = conn.cursor(as_dict=True)
        try:
            # CAMBIO: Agregamos el INNER JOIN para traer 'strNombreMenu'
            cursor.execute("""
                SELECT MO.id, MO.strNombreModulo, MO.idMenu, ME.strNombreMenu, MO.strRuta 
                FROM Modulo MO
                INNER JOIN Menu ME ON MO.idMenu = ME.id
                WHERE MO.id = %s
            """, (id_modulo,))
            return cursor.fetchone()
        finally:
            conn.close()

    @staticmethod
    def save(data):
        id_m = data.get('id')
        nombre = data.get('strNombreModulo')
        # <-- Obtenemos el TEXTO escrito por el usuario
        nombre_menu = data.get('nombreMenu')
        ruta = data.get('strRuta')

        conn = get_connection()
        # Usamos as_dict para leer columnas por nombre
        cursor = conn.cursor(as_dict=True)
        try:
            # --- LÓGICA MÁGICA DEL MENÚ ---
            if not nombre_menu:
                return False, "El Menú Padre es obligatorio."

            # 1. Buscar si ese texto ya existe como menú en la tabla Menu
            cursor.execute(
                "SELECT id FROM Menu WHERE strNombreMenu = %s", (nombre_menu,))
            menu_row = cursor.fetchone()

            if menu_row:
                id_menu = menu_row['id']  # Si existe, tomamos su ID
            else:
                # 2. Si no existe, lo insertamos en la tabla Menu y obtenemos su nuevo ID
                cursor.execute("""
                    INSERT INTO Menu (strNombreMenu) 
                    OUTPUT INSERTED.id 
                    VALUES (%s)
                """, (nombre_menu,))
                new_menu = cursor.fetchone()
                id_menu = new_menu['id']

            # --- AHORA SÍ, GUARDAMOS EL MÓDULO ---
            if id_m:  # UPDATE
                cursor.execute("""
                    UPDATE Modulo SET strNombreModulo=%s, idMenu=%s, strRuta=%s 
                    WHERE id=%s
                """, (nombre, id_menu, ruta, id_m))
                msg = "Módulo actualizado"
            else:  # INSERT
                cursor.execute("""
                    INSERT INTO Modulo (strNombreModulo, idMenu, strRuta) 
                    VALUES (%s, %s, %s)
                """, (nombre, id_menu, ruta))
                msg = "Módulo registrado"

            conn.commit()
            return True, msg
        except Exception as e:
            conn.rollback()  # Por si hay error, deshace cambios
            return False, str(e)
        finally:
            conn.close()

    @staticmethod
    def delete(id_modulo):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM Modulo WHERE id = %s", (id_modulo,))
            conn.commit()
            return True, "Módulo eliminado"
        except Exception as e:
            return False, "No se puede eliminar: el módulo está vinculado a permisos existentes."
        finally:
            conn.close()

    @staticmethod
    def get_menus():
        conn = get_connection()
        cursor = conn.cursor(as_dict=True)
        try:
            cursor.execute(
                "SELECT id, strNombreMenu FROM Menu ORDER BY strNombreMenu ASC")
            return cursor.fetchall()
        finally:
            conn.close()

    @staticmethod
    def update_menu(data):
        id_menu = data.get('id')
        nombre_menu = data.get('strNombreMenu')

        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE Menu SET strNombreMenu = %s WHERE id = %s", (nombre_menu, id_menu))
            conn.commit()
            return True, "Menú actualizado correctamente"
        except Exception as e:
            conn.rollback()
            return False, str(e)
        finally:
            conn.close()

    @staticmethod
    def delete_menu(id_menu):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM Menu WHERE id = %s", (id_menu,))
            conn.commit()
            return True, "Menú eliminado correctamente"
        except Exception as e:
            conn.rollback()
            # Si da error, normalmente es porque viola la Foreign Key (hay módulos usándolo)
            return False, "No se puede eliminar: el menú está siendo utilizado por uno o más módulos."
        finally:
            conn.close()
