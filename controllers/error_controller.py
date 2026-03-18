import os
from core.render import render_view
from services.permisos_service import PermisosService  

def not_found_action(bc=None, env=None, environ=None):
    # Forzamos que path_erroneo sea un string aunque env falle
    path_erroneo = "Ruta no especificada"
    
    # Verificamos si env es realmente el diccionario WSGI
    if isinstance(env, dict):
        path_erroneo = env.get('PATH_INFO', '404')
    elif isinstance(bc, str): 
        # A veces el servidor pasa el path directamente como primer argumento
        path_erroneo = bc

    # Extraemos al usuario del environ
    user = environ.get('app.current_user', {})
    id_perfil_logeado = user.get('id_perfil', 1)
    
    # 1. Obtener todos los permisos del usuario logeado
    todos_los_permisos = PermisosService.get_permisos_by_perfil(id_perfil_logeado)

    context = {
        "titulo": "404 - No Encontrado",
        "breadcrumbs": [
            {"name": "My Project", "url": "/"},
            {"name": "Error 404", "url": "#"}
        ],
        "path": path_erroneo,
         # VARIABLES PARA EL LAYOUT
        "user_nombre": user.get('nombre_completo', 'Usuario'),
        "user_email": user.get('email', ''),
        "user_iniciales": user.get('iniciales', 'U')
        
    }
    return render_view('error/404.html', context)