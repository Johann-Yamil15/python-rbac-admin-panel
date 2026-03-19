from core.render import render_view
from services.db_service import get_home_data
from services.home_service import HomeService
from services.permisos_service import PermisosService

def index_action(breadcrumbs, environ):
    # 1. Extraer el usuario que el Middleware ya validó y guardó en environ
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
    datos_bd = get_home_data()
    # # 4. Construir contexto (Variables planas para el layout)
    # context = {
    #     "titulo": "Monitor de Sistema",
    #     "menu_sidebar": menu_dinamico,
    #     "mensaje": "Estado de infraestructura en tiempo real",
    #     "servidor_fecha": datos_bd['fecha_bd'],
    #     "Estado": "Activo" if datos_bd.get('online') else "Desactivado",
    #     "breadcrumbs": breadcrumbs,
        
    #     # Datos del usuario centralizados
    #     "user_nombre": user.get('nombre_completo', 'Usuario'),
    #     "user_email": user.get('email', 'Sin correo'),
    #     "user_iniciales": user.get('iniciales', 'US')
    # }
    
    return render_view('home/index.html', {
        "titulo": "Monitor de Sistema",
        "menu_sidebar": menu_dinamico,
        "mensaje": "Estado de infraestructura en tiempo real",
        "servidor_fecha": datos_bd['fecha_bd'],
        "Estado": "Activo" if datos_bd.get('online') else "Desactivado",
        "breadcrumbs": breadcrumbs,
        
        # VARIABLES PARA EL LAYOUT
        "user_nombre": user.get('nombre_completo', 'Usuario'),
        "user_email": user.get('email', ''),
        "user_iniciales": user.get('iniciales', 'U'),
    })