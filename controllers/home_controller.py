from core.render import render_view
from services.db_service import get_home_data
from services.home_service import HomeService
from services.permisos_service import PermisosService
from controllers.error_controller import not_found_action

def index_action(breadcrumbs, environ):
    user = environ.get('app.current_user', {})
    
    # Si no hay usuario autenticado, redirigir al login
    if not user:
        # o retornar error/redirect según tu arquitectura
        return not_found_action(breadcrumbs, environ)
    
    id_perfil_logeado = user.get('id_perfil')
    
    # Sin perfil válido, no construir menú completo
    if not id_perfil_logeado:
        menu_dinamico = []
    else:
        menu_dinamico = HomeService.get_sidebar_menu(id_perfil_logeado)
    
    datos_bd = get_home_data()
    
    return render_view('home/index.html', {
        "titulo": "Monitor de Sistema",
        "menu_sidebar": menu_dinamico,
        "mensaje": "Estado de infraestructura en tiempo real",
        "servidor_fecha": datos_bd['fecha_bd'],
        "Estado": "Activo" if datos_bd.get('online') else "Desactivado",
        "breadcrumbs": breadcrumbs,
        "user_nombre": user.get('nombre_completo', 'Usuario'),
        "user_email": user.get('email', ''),
        "user_iniciales": user.get('iniciales', 'U'),
    })