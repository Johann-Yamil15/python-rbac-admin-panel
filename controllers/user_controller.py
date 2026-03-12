import json
from datetime import datetime, date
from werkzeug.wrappers import Request
from core.render import render_view
from services.user_service import UserService
from services.home_service import HomeService
from services.permisos_service import PermisosService
from utils.validators import validate_form


def json_serial(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

# Agregamos 'environ' al recibir los parámetros


def user_manager_action(breadcrumbs, environ):
    user = environ.get('app.current_user', {})
    id_perfil_usuario = user.get('id_perfil', 1)

    # 1. Obtener todos los permisos
    todos_los_permisos = PermisosService.get_permisos_by_perfil(
        id_perfil_usuario)

    # --- 🔍 DEBUG 1: VER TODOS LOS PERMISOS QUE LLEGAN ---
    print("\n" + "="*50)
    print(f"[DEBUG] TODOS los permisos para el perfil ID: {id_perfil_usuario}")
    for permiso in todos_los_permisos:
        print(f"  -> {permiso}")
    print("="*50)

    # 2. Intentar buscar por 'Modulo' (según tus logs) o 'NombreModulo'
    permisos_usuario = next(
        (p for p in todos_los_permisos if p.get('strNombreModulo') == 'Usuario'), 
        {}
    )

    # --- 🔍 DEBUG 2: VER QUÉ ENCONTRÓ EL FILTRO ---
    print(
        f"[DEBUG] Permisos filtrados para el módulo 'Usuario': {permisos_usuario}")

    # Si llega vacío, daremos permisos falsos por defecto
    # Si llega vacío, daremos permisos falsos por defecto
    if not permisos_usuario:
        print("[DEBUG] ⚠️ No se encontró el módulo 'Usuario'. Enviando todos los permisos en False.")
        permisos_usuario = {
            "bitAgregar": False, 
            "bitEditar": False,
            "bitEliminar": False, 
            "bitConsulta": False,
            "bitDetalle": False
        }
    else:
        print("[DEBUG] ✅ Se encontraron permisos. Enviando al renderizador.")
    print("="*50 + "\n")

    menu_dinamico = HomeService.get_sidebar_menu(id_perfil_usuario)

    return render_view('seguridad/usuario.html', {
        "titulo": "Gestión de Usuarios",
        "breadcrumbs": breadcrumbs,
        "menu_sidebar": menu_dinamico,
        "user_nombre": user.get('nombre_completo', 'Usuario'),
        "user_email": user.get('email', ''),
        "user_iniciales": user.get('iniciales', 'U'),
        "permisos_json": json.dumps(permisos_usuario)
    })


def user_api_dispatcher(environ, method):
    request = Request(environ)
    user_id_url = request.args.get('id')

    try:
        # --- MÉTODO GET ---
        if method == 'GET':
            if user_id_url:
                data = UserService.get_user_by_id(user_id_url)
            else:
                data = UserService.get_all_users()
            return json.dumps(data, default=json_serial).encode('utf-8')

        # --- PROCESAMIENTO DE DATOS ---
        body = {}
        image_file = None

        # 1. Intentar leer JSON (Usado por DELETE y a veces por otros)
        if request.content_type == 'application/json':
            data_raw = request.get_data(as_text=True)
            if data_raw:
                body = json.loads(data_raw)

        # 2. Si es FormData (POST/PUT con archivos)
        elif "multipart/form-data" in (request.content_type or ""):
            body = request.form.to_dict()
            image_file = request.files.get('imagenInput')

        # 3. Si es un formulario simple (x-www-form-urlencoded)
        elif request.form:
            body = request.form.to_dict()

        # --- OPERACIONES ---
        if method == 'POST':
            # ... tu lógica de validación ...
            success, message = UserService.register_user(body, image_file)
            return json.dumps({"success": success, "msg": message}).encode('utf-8')

        if method == 'PUT':
            # ... tu lógica de validación ...
            success, message = UserService.update_existing_user(
                body, image_file)
            return json.dumps({"success": success, "msg": message}).encode('utf-8')

        if method == 'DELETE':
            # Ahora 'body' ya tiene el ID porque lo leyó del JSON
            user_id = body.get('id')
            # Verifica esto en consola
            print(f"[DEBUG] Intentando eliminar ID: {user_id}")

            if not user_id:
                return json.dumps({"success": False, "msg": "ID no proporcionado"}).encode('utf-8')

            success, message = UserService.delete_user(user_id)
            return json.dumps({"success": success, "msg": message}).encode('utf-8')

    except Exception as e:
        print(f" ERROR CRÍTICO en User Dispatcher: {str(e)}")
        return json.dumps({
            "success": False,
            "msg": f"Error interno en servidor: {str(e)}"
        }).encode('utf-8')
