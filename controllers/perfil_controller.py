import json
from werkzeug.wrappers import Request
from services.perfil_service import PerfilService
from services.home_service import HomeService
from services.permisos_service import PermisosService  
from core.render import render_view

def perfil_manager_action(breadcrumbs, environ):
    """Renderiza la pantalla principal de perfiles"""
    
    # Extraemos al usuario del environ
    user = environ.get('app.current_user', {})
    id_perfil_logeado = user.get('id_perfil', 1)
    
    # 1. Obtener todos los permisos del usuario logeado
    todos_los_permisos = PermisosService.get_permisos_by_perfil(id_perfil_logeado)
    
    # 2. Filtrar los permisos específicamente para el módulo 'Perfil'
    permisos_modulo = next(
        (p for p in todos_los_permisos if p.get('strNombreModulo') == 'Perfil'), 
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
        
    menu_dinamico = HomeService.get_sidebar_menu(id_perfil_logeado)
    
    return render_view('seguridad/perfil.html', {
        "titulo": "Gestión de Perfiles",
        "breadcrumbs": breadcrumbs,
        "menu_sidebar": menu_dinamico,
        
        # VARIABLES PARA EL LAYOUT
        "user_nombre": user.get('nombre_completo', 'Usuario'),
        "user_email": user.get('email', ''),
        "user_iniciales": user.get('iniciales', 'U'),
        
        # Pasamos los permisos como JSON string seguro
        "permisos_json": json.dumps(permisos_modulo)
    })

def perfil_api_dispatcher(environ, method):
    request = Request(environ)
    perfil_id = request.args.get('id')

    try:
        if method == 'GET':
            if perfil_id:
                data = PerfilService.get_by_id(perfil_id)
            else:
                data = PerfilService.get_all()
            return json.dumps(data).encode('utf-8')

        # Leer body (JSON para DELETE, form para POST/PUT)
        body = {}
        if request.content_type == 'application/json':
            body = json.loads(request.get_data(as_text=True))
        else:
            body = request.form.to_dict()

        if method in ['POST', 'PUT']:
            success, msg = PerfilService.save(body)
            return json.dumps({"success": success, "msg": msg}).encode('utf-8')

        if method == 'DELETE':
            success, msg = PerfilService.delete(body.get('id'))
            return json.dumps({"success": success, "msg": msg}).encode('utf-8')

    except Exception as e:
        return json.dumps({"success": False, "msg": str(e)}).encode('utf-8')