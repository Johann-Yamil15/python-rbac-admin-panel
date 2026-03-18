import json
from werkzeug.wrappers import Request
from services.modulo_service import ModuloService
from services.home_service import HomeService
from services.permisos_service import PermisosService
from core.render import render_view


def modulo_manager_action(breadcrumbs, environ):
    """Renderiza la pantalla principal de módulos"""
    print("\n[DEBUG] --- Iniciando modulo_manager_action ---")

    user = environ.get('app.current_user', {})
    id_perfil_logeado = user.get('id_perfil', 1)
    print(f"[DEBUG] Usuario detectado - ID Perfil: {id_perfil_logeado}")

    # 1. Permisos
    print("[DEBUG] Solicitando permisos generales a la BD...")
    todos_los_permisos = PermisosService.get_permisos_by_perfil(
        id_perfil_logeado)

    # Buscamos el módulo 'Módulo'
    print("[DEBUG] Buscando permisos específicos para el módulo 'Módulo'...")
    permisos_modulo = next(
        (p for p in todos_los_permisos if p.get('strNombreModulo') == 'Módulo'),
        {}
    )

    if not permisos_modulo:
        print("[WARN] No se encontraron permisos, aplicando default (False).")
        permisos_modulo = {
            "bitAgregar": False, "bitEditar": False, "bitEliminar": False,
            "bitConsulta": False, "bitDetalle": False
        }
    else:
        print(f"[DEBUG] Permisos encontrados: {permisos_modulo}")

    print("[DEBUG] Cargando menú dinámico lateral...")
    menu_dinamico = HomeService.get_sidebar_menu(id_perfil_logeado)

    # Obtener menús para el dropdown en el modal
    print("[DEBUG] Obteniendo menús disponibles para el modal...")
    menus_disponibles = ModuloService.get_menus()

    # --- LA SOLUCIÓN ESTÁ AQUÍ ---
    # ensure_ascii=False obliga a Python a dejar la 'ó' normal y no usar '\u00f3'
    print("[DEBUG] Convirtiendo permisos a JSON seguro...")
    permisos_json_string = json.dumps(permisos_modulo, ensure_ascii=False)

    print("[DEBUG] Renderizando vista 'seguridad/modulo.html'...")
    return render_view('seguridad/modulo.html', {
        "titulo": "Gestión de Módulos",
        "breadcrumbs": breadcrumbs,
        "menu_sidebar": menu_dinamico,

        "user_nombre": user.get('nombre_completo', 'Usuario'),
        "user_email": user.get('email', ''),
        "user_iniciales": user.get('iniciales', 'U'),

        "permisos_json": permisos_json_string,
        "menus_disponibles": menus_disponibles
    })


def modulo_api_dispatcher(environ, method):
    # (El resto de tu código de dispatcher queda igual)
    request = Request(environ)
    modulo_id = request.args.get('id')

    try:
        if method == 'GET':
            if modulo_id:
                data = ModuloService.get_by_id(modulo_id)
            else:
                data = ModuloService.get_all()
            return json.dumps(data).encode('utf-8')

        body = {}
        if request.content_type == 'application/json':
            body = json.loads(request.get_data(as_text=True))
        else:
            body = request.form.to_dict()

        if method in ['POST', 'PUT']:
            success, msg = ModuloService.save(body)
            return json.dumps({"success": success, "msg": msg}).encode('utf-8')

        if method == 'DELETE':
            success, msg = ModuloService.delete(body.get('id'))
            return json.dumps({"success": success, "msg": msg}).encode('utf-8')

    except Exception as e:
        return json.dumps({"success": False, "msg": str(e)}).encode('utf-8')
    
def menu_api_dispatcher(environ, method):
    """Maneja las peticiones a /api/menus (PUT, DELETE)"""
    request = Request(environ)

    try:
        # Leer body (JSON)
        body = {}
        if request.content_type == 'application/json':
            body = json.loads(request.get_data(as_text=True))
        else:
            body = request.form.to_dict()

        # PUT: Actualiza un menú
        if method == 'PUT':
            success, msg = ModuloService.update_menu(body)
            return json.dumps({"success": success, "msg": msg}).encode('utf-8')

        # DELETE: Elimina un menú
        if method == 'DELETE':
            success, msg = ModuloService.delete_menu(body.get('id'))
            return json.dumps({"success": success, "msg": msg}).encode('utf-8')

    except Exception as e:
        return json.dumps({"success": False, "msg": str(e)}).encode('utf-8')
