from config.database import get_connection

class HomeService:
    @staticmethod
    def get_sidebar_menu(id_perfil):
        """
        Obtiene la estructura de menús y submenús basada en los permisos del perfil con logs de consola.
        """
        print(f"\n[DEBUG] Cargando menú para el perfil ID: {id_perfil}")
        
        conn = get_connection()
        # Nota: Asegúrate que tu conector soporte as_dict=True (pymssql lo hace)
        cursor = conn.cursor(as_dict=True)
        
        try:
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
            
            print(f"[DEBUG] Ejecutando consulta de menús...")
            cursor.execute(query, (id_perfil,))
            rows = cursor.fetchall()
            
            print(f"[DEBUG] Filas encontradas en la BD: {len(rows)}")
            
            # Imprimir cada fila para ver exactamente qué viene de la BD
            for i, row in enumerate(rows):
                print(f"   -> Fila {i+1}: Menu={row['nombreMenu']} | Modulo={row['nombreModulo']} | Ruta={row['strRuta']}")

            # Estructurar los datos en un diccionario jerárquico
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