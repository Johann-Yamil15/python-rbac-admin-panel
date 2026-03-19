from controllers.home_controller import index_action
from controllers.user_controller import user_manager_action, user_api_dispatcher
from controllers.error_controller import not_found_action
from controllers.catalogo_controller import catalogo_api_dispatcher
from controllers.perfil_controller import perfil_manager_action, perfil_api_dispatcher
from controllers.permisos_controller import permisos_manager_action, permisos_api_dispatcher
from controllers.login_controller import login_view, login_api_dispatcher, logout_action
from controllers.vistasStaticas_controller import modulo_simulado_action
from controllers.modulo_controller import modulo_manager_action, modulo_api_dispatcher, menu_api_dispatcher
from controllers.profile_controller import profile_action


def get_route_handler(path, method):
    routes = {
        ('/', 'GET'): lambda bc, env: index_action(bc, env),
        ('/usuarios', 'GET'): lambda bc, env: user_manager_action(bc, env),
        ('/perfiles', 'GET'): lambda bc, env: perfil_manager_action(bc, env),
        ('/permisos', 'GET'): lambda bc, env: permisos_manager_action(bc, env),
        ('/modulos', 'GET'): lambda bc, env: modulo_manager_action(bc, env),
        ('/profile', 'GET'): lambda bc, env: profile_action(bc, env),

        # --- RUTAS DE AUTENTICACIÓN ---
        ('/login', 'GET'): lambda bc, env: login_view(env),
        ('/api/login', 'POST'): lambda bc, env: login_api_dispatcher(env, 'POST'),
        ('/logout', 'GET'): lambda bc, env: logout_action(env),

        ('/api/usuarios', 'GET'): lambda bc, env: user_api_dispatcher(env, 'GET'),
        ('/api/usuarios', 'POST'): lambda bc, env: user_api_dispatcher(env, 'POST'),
        ('/api/usuarios', 'PUT'): lambda bc, env: user_api_dispatcher(env, 'PUT'),
        ('/api/usuarios', 'DELETE'): lambda bc, env: user_api_dispatcher(env, 'DELETE'),

        ('/api/perfil', 'GET'): lambda bc, env: catalogo_api_dispatcher(env, 'GET', 'perfiles'),
        ('/api/sexos', 'GET'): lambda bc, env: catalogo_api_dispatcher(env, 'GET', 'sexos'),
        ('/api/estados', 'GET'): lambda bc, env: catalogo_api_dispatcher(env, 'GET', 'estados'),
        ('/api/modulos', 'GET'): lambda bc, env: catalogo_api_dispatcher(env, 'GET', 'modulos'),
        ('/api/menus', 'GET'): lambda bc, env: catalogo_api_dispatcher(env, 'GET', 'menus'),

        ('/api/menus', 'PUT'): lambda bc, env: menu_api_dispatcher(env, 'PUT'),
        ('/api/menus', 'DELETE'): lambda bc, env: menu_api_dispatcher(env, 'DELETE'),

        ('/api/perfiles', 'GET'): lambda bc, env: perfil_api_dispatcher(env, 'GET'),
        ('/api/perfiles', 'POST'): lambda bc, env: perfil_api_dispatcher(env, 'POST'),
        ('/api/perfiles', 'PUT'): lambda bc, env: perfil_api_dispatcher(env, 'PUT'),
        ('/api/perfiles', 'DELETE'): lambda bc, env: perfil_api_dispatcher(env, 'DELETE'),

        ('/api/modulos', 'GET'): lambda bc, env: modulo_api_dispatcher(env, 'GET'),
        ('/api/modulos', 'POST'): lambda bc, env: modulo_api_dispatcher(env, 'POST'),
        ('/api/modulos', 'PUT'): lambda bc, env: modulo_api_dispatcher(env, 'PUT'),
        ('/api/modulos', 'DELETE'): lambda bc, env: modulo_api_dispatcher(env, 'DELETE'),

        ('/api/permisos_perfil', 'GET'): lambda bc, env: permisos_api_dispatcher(env, 'GET'),
        ('/api/permisos_perfil', 'POST'): lambda bc, env: permisos_api_dispatcher(env, 'POST'),

        # --- VISTAS ESTÁTICAS SIMULADAS ---
        ('/p1-1', 'GET'): lambda bc, env: modulo_simulado_action(bc, env, 'principal1', 'Principal 1.1'),
        ('/p1-2', 'GET'): lambda bc, env: modulo_simulado_action(bc, env, 'principal1', 'Principal 1.2'),
        ('/p2-1', 'GET'): lambda bc, env: modulo_simulado_action(bc, env, 'principal2', 'Principal 2.1'),
        ('/p2-2', 'GET'): lambda bc, env: modulo_simulado_action(bc, env, 'principal2', 'Principal 2.2'),
    }

    # 1. Buscamos primero si hay una coincidencia exacta en el diccionario
    handler = routes.get((path, method))
    if handler:
        return handler, '200 OK'

    # 2. NUEVO: Si no hubo coincidencia exacta, revisamos si es una ruta dinámica (con ID)
    if path.startswith('/api/permisos_perfil/') and method == 'GET':
        # El dispatcher ya sabe extraer el ID de la variable "environ"
        return lambda bc, env: permisos_api_dispatcher(env, 'GET'), '200 OK'

    # 3. Si no cumple ninguna de las anteriores, devolvemos 404
    return not_found_action, '404 Not Found'
