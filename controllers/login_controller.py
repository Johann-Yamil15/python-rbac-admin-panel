import json
import os
from werkzeug.wrappers import Request, Response
# IMPORTANTE: Agregamos redirect aquí
from werkzeug.utils import redirect 
from core.render import render_view
from services.login_service import LoginService

def login_view(environ):
    """Renderiza la vista de login desde el archivo HTML puro"""
    # Ajusta esta ruta según tu estructura real (auth/login.html o login.html)
    ruta_login = os.path.join('views', 'auth', 'login.html') 
    
    try:
        with open(ruta_login, 'r', encoding='utf-8') as f:
            html_puro = f.read()
            
        return Response(html_puro, mimetype='text/html')
        
    except FileNotFoundError:
        return Response("<h1>Error: No se encontró el archivo login.html</h1>", status=404, mimetype='text/html')

def login_api_dispatcher(environ, method):
    request = Request(environ)
    
    if method == 'POST':
        body = {}
        if request.content_type == 'application/json':
            data_raw = request.get_data(as_text=True)
            if data_raw:
                body = json.loads(data_raw)
        elif request.form:
            body = request.form.to_dict()

        email = body.get('correo')
        password = body.get('password')

        if not email or not password:
            return Response(json.dumps({"success": False, "msg": "Faltan credenciales"}), 
                            content_type='application/json')

        success, msg, token, user_data = LoginService.authenticate_user(email, password)

        response_data = json.dumps({"success": success, "msg": msg})
        response = Response(response_data, content_type='application/json')

        if success:
            # Guardamos el token en una cookie HTTP
            response.set_cookie(
                'auth_token', 
                value=token, 
                max_age=60*60*8, # 8 horas
                httponly=True,   # Seguridad contra XSS
                samesite='Lax'
            )
        
        return response
    
def logout_action(environ):
    """
    Cierra la sesión del usuario eliminando la cookie del token
    y lo redirige a la pantalla de inicio de sesión.
    """
    # 1. Ahora 'redirect' ya funcionará porque está importado arriba
    response = redirect('/login')
    
    # 2. Eliminamos la cookie 'auth_token'
    response.delete_cookie('auth_token')
    
    return response