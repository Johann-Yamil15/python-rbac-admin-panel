import os
from core.render import render_view
from services.home_service import HomeService

def not_found_action(bc=None, env=None):
    # env ahora siempre es el dict WSGI completo
    path_erroneo = env.get('PATH_INFO', '/404') if isinstance(env, dict) else '/404'
    
    user = {}
    menu_dinamico = []
    if isinstance(env, dict):
        user = env.get('app.current_user') or {}
        id_perfil = user.get('id_perfil', 1)
        menu_dinamico = HomeService.get_sidebar_menu(id_perfil)

    context = {
        "titulo": "404 - Página No Encontrada",
        "breadcrumbs": bc if isinstance(bc, list) else [
            {"name": "Inicio", "url": "/"},
            {"name": "Error 404", "url": "#"}
        ],
        "menu_sidebar": menu_dinamico,
        "path": path_erroneo,
        "user_nombre": user.get('nombre_completo', 'Usuario'),
        "user_email": user.get('email', ''),
        "user_iniciales": user.get('iniciales', 'U'),
    }
    return render_view('error/404.html', context)