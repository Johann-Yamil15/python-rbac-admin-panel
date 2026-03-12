from core.render import render_view
from services.db_service import get_home_data
from services.home_service import HomeService

def index_action(breadcrumbs, environ):
    # 1. Extraer el usuario que el Middleware ya validó y guardó en environ
    current_user = environ.get('app.current_user', {})
    
    # 2. Obtener datos específicos de esta vista (BD)
    datos_bd = get_home_data()
    
    # 3. Obtener el menú usando el ID de perfil del token
    id_perfil = current_user.get('id_perfil', 1)
    menu_dinamico = HomeService.get_sidebar_menu(id_perfil)
    
    # 4. Construir contexto (Variables planas para el layout)
    context = {
        "titulo": "Monitor de Sistema",
        "menu_sidebar": menu_dinamico,
        "mensaje": "Estado de infraestructura en tiempo real",
        "servidor_fecha": datos_bd['fecha_bd'],
        "Estado": "Activo" if datos_bd.get('online') else "Desactivado",
        "breadcrumbs": breadcrumbs,
        
        # Datos del usuario centralizados
        "user_nombre": current_user.get('nombre_completo', 'Usuario'),
        "user_email": current_user.get('email', 'Sin correo'),
        "user_iniciales": current_user.get('iniciales', 'US')
    }
    
    return render_view('home/index.html', context)