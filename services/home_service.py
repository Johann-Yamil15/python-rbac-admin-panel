from config.database import get_connection

class HomeService:
    @staticmethod
    def get_sidebar_menu(id_perfil):
        """
        Obtiene la estructura de menús y submenús basada en los permisos del perfil con logs de consola.
        Valida si el perfil es Super Administrador para mapear todos los módulos automáticamente.
        """
        print(f"\n[DEBUG] Cargando menú para el perfil ID: {id_perfil}")
        
        conn = get_connection()
        cursor = conn.cursor(as_dict=True)
        
        try:
            # 1. Validar si el perfil es Administrador
            print(f"[DEBUG] Verificando si el perfil es Super Administrador...")
            query_perfil = "SELECT bitAdministrador FROM Perfil WHERE id = %s"
            cursor.execute(query_perfil, (id_perfil,))
            perfil_data = cursor.fetchone()
            
            if not perfil_data:
                print(f"[ERROR] El perfil ID {id_perfil} no existe en la base de datos.")
                return []
                
            es_admin = bool(perfil_data.get('bitAdministrador', 0))
            
            # 2. Elegir la consulta dependiendo del tipo de perfil
            if es_admin:
                print("[DEBUG] ¡Es Super Administrador! Mapeando TODOS los módulos por defecto...")
                query = """
                    SELECT 
                        ME.id AS idMenu,
                        ME.strNombreMenu AS nombreMenu,
                        MO.id AS idModulo,
                        MO.strNombreModulo AS nombreModulo,
                        MO.strRuta,
                        1 AS bitConsulta
                    FROM Menu ME
                    INNER JOIN Modulo MO ON ME.id = MO.idMenu
                    ORDER BY ME.id, MO.id
                """
                cursor.execute(query)
            else:
                print("[DEBUG] No es Super Administrador. Validando permisos específicos (PermisosPerfil)...")
                query = """
                    SELECT 
                        ME.id AS idMenu,
                        ME.strNombreMenu AS nombreMenu,
                        MO.id AS idModulo,
                        MO.strNombreModulo AS nombreModulo,
                        MO.strRuta,
                        PP.bitConsulta
                    FROM Menu ME
                    INNER JOIN Modulo MO ON ME.id = MO.idMenu
                    INNER JOIN PermisosPerfil PP ON MO.id = PP.idModulo
                    WHERE PP.idPerfil = %s AND PP.bitConsulta = 1
                    ORDER BY ME.id, MO.id
                """
                cursor.execute(query, (id_perfil,))
                
            rows = cursor.fetchall()
            
            print(f"[DEBUG] Filas encontradas en la BD: {len(rows)}")
            
            # Imprimir cada fila para ver exactamente qué viene de la BD
            for i, row in enumerate(rows):
                print(f"   -> Fila {i+1}: Menu={row['nombreMenu']} | Modulo={row['nombreModulo']} | Ruta={row['strRuta']}")

            # 3. Estructurar los datos en un diccionario jerárquico (Tu lógica original intacta)
            menu_estructurado = {}
            for row in rows:
                menu_id = row['idMenu']
                if menu_id not in menu_estructurado:
                    menu_estructurado[menu_id] = {
                        "titulo": row['nombreMenu'],
                        "id_html": f"menu_{menu_id}",
                        "submodulos": []
                    }
                
                menu_estructurado[menu_id]["submodulos"].append({
                    "nombre": row['nombreModulo'],
                    "ruta": row['strRuta']
                })

            resultado_final = list(menu_estructurado.values())
            
            print(f"[DEBUG] Estructura jerárquica generada:")
            for m in resultado_final:
                sub_nombres = [s['nombre'] for s in m['submodulos']]
                print(f"   [*] Sección: {m['titulo']} | Submódulos: {sub_nombres}")

            return resultado_final

        except Exception as e:
            print(f"[ERROR] Falló la carga del menú dinámico: {str(e)}")
            return []
        finally:
            conn.close()
            print("[DEBUG] Conexión a la base de datos cerrada.\n")