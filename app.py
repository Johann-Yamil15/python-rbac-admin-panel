import os
import mimetypes
import jwt
from core.render import render_view
from core.router import get_route_handler
from werkzeug.wrappers import Response, Request
from werkzeug.utils import redirect
from services.login_service import SECRET_KEY

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
            if file_path.endswith(".css"):
                content_type = "text/css"
            elif file_path.endswith(".js"):
                content_type = "application/javascript"
            else:
                content_type, _ = mimetypes.guess_type(file_path)
                if not content_type:
                    content_type = "text/plain"

            start_response('200 OK', [('Content-Type', content_type)])
            with open(file_path, 'rb') as f:
                return [f.read()]
        else:
            start_response('404 Not Found', [('Content-Type', 'text/plain')])
            return [b"Archivo estatico no encontrado"]

    # --- 2. MIDDLEWARE DE AUTENTICACIÓN (NUEVO) ---
    # Rutas que cualquiera puede ver sin estar logueado
    rutas_publicas = {'/login', '/login/', '/api/login', '/api/login/'}

    if path not in rutas_publicas:
        current_user = get_current_user(environ)

    if not current_user:
        if path.startswith('/api/'):
            resp = Response('{"success": false, "msg": "Sesión expirada"}',
                            status=401, mimetype='application/json')
            return resp(environ, start_response)
        else:
            resp = redirect('/login')
            return resp(environ, start_response)

    environ['app.current_user'] = current_user

    # --- 3. PROCESAMIENTO DE RUTAS DINÁMICAS ---
    breadcrumbs = get_breadcrumbs(path)
    handler, status = get_route_handler(path, method)

    ctype = 'text/html; charset=utf-8'
    if path.startswith('/api/'):
        ctype = 'application/json'

    headers = [('Content-type', ctype)]

    try:
        response_body = handler(breadcrumbs, environ)

        if isinstance(response_body, Response):
            return response_body(environ, start_response)

        if isinstance(response_body, str):
            response_body = response_body.encode('utf-8')

    except Exception as e:
        print(f"🔥 Error ejecutando handler: {e}")
        status = '500 Internal Server Error'
        response_body = f"Error crítico en el servidor: {e}".encode(
            'utf-8')

    start_response(status, headers)
    return [response_body]
