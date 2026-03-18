from config.database import get_connection

class PermisosService:
    @staticmethod
    def get_permisos_by_perfil(id_perfil):
        permisos_list = []
        conn = get_connection()
        cursor = conn.cursor(as_dict=True)
        
        try:
            # 1. Validar si el perfil es Administrador
            query_perfil = "SELECT bitAdministrador FROM Perfil WHERE id = %s"
            cursor.execute(query_perfil, (id_perfil,))
            perfil_data = cursor.fetchone()
            
            if not perfil_data:
                return [] # Si el perfil no existe, regresamos lista vacía
                
            es_admin = bool(perfil_data.get('bitAdministrador', 0))
            
            if es_admin:
                # 2A. Si es admin, traemos TODOS los módulos con todos los permisos en 1
                query = """
                    SELECT 
                        M.id AS idModulo, 
                        M.strNombreModulo,
                        NULL AS idPermiso, -- No hay un ID de permiso real porque es asignación dinámica
                        1 as bitAgregar,
                        1 as bitEditar,
                        1 as bitEliminar,
                        1 as bitConsulta,
                        1 as bitDetalle
                    FROM Modulo M
                """
                cursor.execute(query)
            else:
                # 2B. Si no es admin, usamos tu lógica original con LEFT JOIN
                query = """
                    SELECT 
                        M.id AS idModulo, 
                        M.strNombreModulo,
                        P.id AS idPermiso,
                        ISNULL(P.bitAgregar, 0) as bitAgregar,
                        ISNULL(P.bitEditar, 0) as bitEditar,
                        ISNULL(P.bitEliminar, 0) as bitEliminar,
                        ISNULL(P.bitConsulta, 0) as bitConsulta,
                        ISNULL(P.bitDetalle, 0) as bitDetalle
                    FROM Modulo M
                    LEFT JOIN PermisosPerfil P ON M.id = P.idModulo AND P.idPerfil = %s
                """
                cursor.execute(query, (id_perfil,))
                
            permisos_list = cursor.fetchall()
            
        finally:
            conn.close()
            
        return permisos_list
    
    @staticmethod
    def get_permisos_by_viewperfil(id_perfil):
        permisos_list = []
        conn = get_connection()
        cursor = conn.cursor(as_dict=True)
        # Traemos TODOS los módulos y hacemos LEFT JOIN con los permisos del perfil seleccionado
        query = """
            SELECT 
                M.id AS idModulo, 
                M.strNombreModulo,
                P.id AS idPermiso,
                ISNULL(P.bitAgregar, 0) as bitAgregar,
                ISNULL(P.bitEditar, 0) as bitEditar,
                ISNULL(P.bitEliminar, 0) as bitEliminar,
                ISNULL(P.bitConsulta, 0) as bitConsulta,
                ISNULL(P.bitDetalle, 0) as bitDetalle
            FROM Modulo M
            LEFT JOIN PermisosPerfil P ON M.id = P.idModulo AND P.idPerfil = %s
        """
        cursor.execute(query, (id_perfil,))
        permisos_list = cursor.fetchall()
        conn.close()
        return permisos_list

    @staticmethod
    def update_permiso(data):
        conn = get_connection()
        cursor = conn.cursor()
        # Lógica de "Upsert": Si existe actualiza, si no, inserta.
        query = """
            IF EXISTS (SELECT 1 FROM PermisosPerfil WHERE idModulo = %s AND idPerfil = %s)
            BEGIN
                UPDATE PermisosPerfil SET 
                    bitAgregar = %s, bitEditar = %s, bitEliminar = %s, 
                    bitConsulta = %s, bitDetalle = %s
                WHERE idModulo = %s AND idPerfil = %s
            END
            ELSE
            BEGIN
                INSERT INTO PermisosPerfil (idModulo, idPerfil, bitAgregar, bitEditar, bitEliminar, bitConsulta, bitDetalle)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            END
        """
        params = (
            data['idModulo'], data['idPerfil'],
            data['bitAgregar'], data['bitEditar'], data['bitEliminar'], data['bitConsulta'], data['bitDetalle'],
            data['idModulo'], data['idPerfil'],
            data['idModulo'], data['idPerfil'],
            data['bitAgregar'], data['bitEditar'], data['bitEliminar'], data['bitConsulta'], data['bitDetalle']
        )
        cursor.execute(query, params)
        conn.commit()
        conn.close()
        return True