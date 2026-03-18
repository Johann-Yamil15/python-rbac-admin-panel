import json
from datetime import datetime, date
from werkzeug.wrappers import Request, Response
from core.render import render_view
from services.user_service import UserService
from services.home_service import HomeService

def profile_action(breadcrumbs, environ):
    user_session = environ.get('app.current_user', {})
    user_id = user_session.get('id')

    if not user_id:
        return Response("No autorizado", status=401)

    user_data = UserService.get_user_by_id(user_id)

    user_data = {
    'Nombre':         user_data.get('nombre', ''),
    'ApellidoP':      user_data.get('ap', ''),
    'ApellidoM':      user_data.get('am', ''),
    'strCorreo':      user_data.get('email', ''),
    'FechaRegistro':  user_data.get('fecha_registro', ''),
    'strImagenPath':  user_data.get('imagen_path', ''),
    'strNumeroCelular': user_data.get('celular', ''),
}
    
    # 1. Formatear Fecha
    if user_data.get('FechaRegistro'):
        if isinstance(user_data['FechaRegistro'], (datetime, date)):
            user_data['FechaRegistro'] = user_data['FechaRegistro'].strftime('%d de %B, %Y')

    # 2. Procesar Ruta de Imagen (Evita el error 500 y 404)
    foto = user_data.get('strImagenPath', '')
    if foto:
        foto_perfil = foto.replace('\\', '/')
    else:
        foto_perfil = 'static/Images/users/default.png'

    # 3. Procesar Teléfono (Evita mostrar lógica 'if' en el HTML)
    tel_celular = user_data.get('strNumeroCelular')
    if not tel_celular or str(tel_celular).strip() == "":
        tel_celular = "No disponible"

    id_perfil_usuario = user_session.get('id_perfil', 1)
    menu_dinamico = HomeService.get_sidebar_menu(id_perfil_usuario)

    if user_data and 'strPwd' in user_data:
        del user_data['strPwd']

    # 4. Renderizar enviando variables procesadas y el objeto usuario
    return render_view('home/perfil.html', {
        "titulo": "Mi Perfil",
        "breadcrumbs": breadcrumbs,
        "menu_sidebar": menu_dinamico,
        "user_nombre": user_session.get('nombre_completo', 'Usuario'),
        "user_email": user_session.get('email', ''),
        "user_iniciales": user_session.get('iniciales', 'U'),
        "usuario": user_data,
        "foto_perfil": foto_perfil,       # Variable lista para <img>
        "telefono_contacto": tel_celular  # Variable lista para el span
    })