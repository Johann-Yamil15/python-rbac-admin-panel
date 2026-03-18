import json
from werkzeug.wrappers import Request
from services.permisos_service import PermisosService
from services.perfil_service import PerfilService
from services.permisos_service import PermisosService
from services.home_service import HomeService
from core.render import render_view

# Agregamos 'environ' al recibir los parámetros


def permisos_manager_action(breadcrumbs, environ):
    """Renderiza la pantalla principal de permisos"""

    # EXTRAEMOS AL USUARIO DEL ENVIRON
    user = environ.get('app.current_user', {})
    id_perfil_logeado = user.get('id_perfil', 1)
    
    # 1. Obtener todos los permisos del usuario logeado
    todos_los_permisos = PermisosService.get_permisos_by_perfil(id_perfil_logeado)
    
    # 2. Filtrar los permisos específicamente para el módulo 'Permisos-Perfil' (según tu BD)
    permisos_modulo = next(
        (p for p in todos_los_permisos if p.get('strNombreModulo') == 'Permisos-Perfil'), 
        {}
    )
    
    # 3. Si no tiene permisos, enviar el diccionario por defecto en False
    if not permisos_modulo:
        permisos_modulo = {
            "bitAgregar": False, 
            "bitEditar": False,
            "bitEliminar": False, 
            "bitConsulta": False,
            "bitDetalle": False
        }

    # Obtenemos el menú dinámico real
    menu_dinamico = HomeService.get_sidebar_menu(id_perfil_logeado)

    return render_view('seguridad/permisos_perfil.html', {
        "titulo": "Gestión de Permisos",
        "breadcrumbs": breadcrumbs,
        "menu_sidebar": menu_dinamico,
        
        # VARIABLES PARA EL LAYOUT (IMPORTANTE)
        "user_nombre": user.get('nombre_completo', 'Usuario'),
        "user_email": user.get('email', ''),
        "user_iniciales": user.get('iniciales', 'U'),
        
        # Inyectamos los permisos de forma segura
        "permisos_json": json.dumps(permisos_modulo)
    })


def permisos_api_dispatcher(environ, method):
    """Dispatcher para las peticiones AJAX de permisos"""
    request = Request(environ)

    # Extraer ID de perfil si viene en la URL (ej. /api/permisos_perfil/1)
    path_info = environ.get('PATH_INFO', '')
    parts = path_info.strip('/').split('/')
    perfil_id_url = parts[-1] if len(
        parts) > 2 and parts[-1].isdigit() else None

    try:
        # --- CASO GET: Obtener permisos de un perfil específico ---
        if method == 'GET':
            if perfil_id_url:
                data = PermisosService.get_permisos_by_viewperfil(perfil_id_url)
                return json.dumps(data).encode('utf-8')
            return json.dumps({"error": "ID de perfil requerido"}).encode('utf-8')

        # --- CASO POST: Guardado Masivo (Bulk Update) ---
        if method == 'POST':
            if request.content_type == 'application/json':
                body = json.loads(request.get_data(as_text=True))

                # La data enviada desde el JS es un objeto con idPerfil y lista de permisos
                id_perfil = body.get('idPerfil')
                lista_permisos = body.get('permisos', [])

                if not id_perfil:
                    return json.dumps({"success": False, "msg": "Perfil no identificado"}).encode('utf-8')

                success_count = 0
                for item in lista_permisos:
                    # Sincronizamos el idPerfil en cada objeto de permiso
                    item['idPerfil'] = id_perfil
                    if PermisosService.update_permiso(item):
                        success_count += 1

                return json.dumps({
                    "success": True,
                    "msg": f"Se actualizaron {success_count} módulos con éxito"
                }).encode('utf-8')

        return json.dumps({"success": False, "msg": "Método no soportado"}).encode('utf-8')

    except Exception as e:
        return json.dumps({"success": False, "msg": f"Error en controlador: {str(e)}"}).encode('utf-8')
