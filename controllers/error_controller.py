import os
from core.render import render_view

def not_found_action(bc=None, env=None):
    # Forzamos que path_erroneo sea un string aunque env falle
    path_erroneo = "Ruta no especificada"
    
    # Verificamos si env es realmente el diccionario WSGI
    if isinstance(env, dict):
        path_erroneo = env.get('PATH_INFO', '404')
    elif isinstance(bc, str): 
        # A veces el servidor pasa el path directamente como primer argumento
        path_erroneo = bc

    context = {
        "titulo": "404 - No Encontrado",
        "breadcrumbs": [
            {"name": "My Project", "url": "/"},
            {"name": "Error 404", "url": "#"}
        ],
        "path": path_erroneo
    }
    return render_view('error/404.html', context)