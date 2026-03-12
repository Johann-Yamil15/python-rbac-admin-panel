import os
import mimetypes
import jwt
from core.render import render_view
from core.router import get_route_handler 
from werkzeug.wrappers import Response, Request
from werkzeug.utils import redirect
from services.login_service import SECRET_KEY  # Asegúrate de que la ruta coincida con tu proyecto

# --- FUNCIÓN PARA VALIDAR EL TOKEN ---
def get_current_user(environ):
    """Extrae y decodifica el token de la cookie de la petición."""
    request = Request(environ)
    token = request.cookies.get('auth_token')
    
    if not token:
        return None
        
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

def get_breadcrumbs(path):
    parts = [p for p in path.split('/') if p]
    breadcrumbs = [{"name": "My Project", "url": "/"}]
    current_url = ""
    for part in parts:
        current_url += f"/{part}"
        name = part.replace('_', ' ').replace('-', ' ').title()
        breadcrumbs.append({"name": name, "url": current_url})
    return breadcrumbs

def application(environ, start_response):
    path = environ.get('PATH_INFO', '/')
    method = environ.get('REQUEST_METHOD', 'GET')
    
    if path == '/favicon.ico':
        start_response('204 No Content', [('Content-Length', '0')])
        return [b""]

    # --- 1. LÓGICA PARA ARCHIVOS ESTÁTICOS ---
    if path.startswith('/static/'):
        file_path = os.path.join(os.getcwd(), path.lstrip('/'))
        if os.path.exists(file_path):
            if file_path.endswith(".css"): content_type = "text/css"
            elif file_path.endswith(".js"): content_type = "application/javascript"
            else:
                content_type, _ = mimetypes.guess_type(file_path)
                if not content_type: content_type = "text/plain"

            start_response('200 OK', [('Content-Type', content_type)])
            with open(file_path, 'rb') as f: return [f.read()]
        else:
            start_response('404 Not Found', [('Content-Type', 'text/plain')])
            return [b"Archivo estatico no encontrado"]

    # --- 2. MIDDLEWARE DE AUTENTICACIÓN (NUEVO) ---
    # Rutas que cualquiera puede ver sin estar logueado
    rutas_publicas = {'/login', '/login/', '/api/login', '/api/login/'}
    
    if path not in rutas_publicas and path != '/':
        current_user = get_current_user(environ)
        
        # Si NO está logueado
        if not current_user:
            if path.startswith('/api/'):
                # Para APIs: devolvemos un 401 No Autorizado en formato JSON
                resp = Response('{"success": false, "msg": "Sesión expirada"}', status=401, mimetype='application/json')
                return resp(environ, start_response)
            else:
                # Para vistas HTML: lo mandamos a la pantalla de login
                resp = redirect('/login')
                return resp(environ, start_response)
                
        # Si SÍ está logueado, inyectamos los datos en el entorno para usarlos en los controladores
        environ['app.current_user'] = current_user

    # --- 3. PROCESAMIENTO DE RUTAS DINÁMICAS ---
    breadcrumbs = get_breadcrumbs(path)
    handler, status = get_route_handler(path, method)

    ctype = 'text/html; charset=utf-8'
    if path.startswith('/api/'):
        ctype = 'application/json'
    
    headers = [('Content-type', ctype)]

    try:
        if status == '404 Not Found':
            # El 404 suele recibir bc y el path errado
            response_body = handler(breadcrumbs, path)
        else:
            # Para Home, Usuarios y API, enviamos ambos
            response_body = handler(breadcrumbs, environ)
            
        # Si el controlador devolvió un objeto Response de Werkzeug (redirect, cookies, json especial)
        if isinstance(response_body, Response):
            return response_body(environ, start_response)
            
        # Si es un string (HTML normal devuelto por render_view), lo pasamos a bytes
        if isinstance(response_body, str):
            response_body = response_body.encode('utf-8')
            
    except Exception as e:
        print(f"🔥 Error ejecutando handler: {e}")
        status = '500 Internal Server Error'
        response_body = f"Error crítico en el servidor: {e}".encode('utf-8')

    start_response(status, headers)
    return [response_body]