from core.render import render_view
from services.db_service import get_home_data
from services.home_service import HomeService
from services.permisos_service import PermisosService
from controllers.error_controller import not_found_action

def index_action(breadcrumbs, environ):
    # Mismo patrón que perfil_manager_action y permisos_manager_action
    user = environ.get('app.current_user', {})
    id_perfil_logeado = user.get('id_perfil', 1)  # ← default 1 igual que los demás

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