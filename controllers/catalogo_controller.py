import json
from services.catalogo_service import CatalogoService


def catalogo_api_dispatcher(environ, method, catalog_type):
    """
    catalog_type: vendrá de la ruta definida en tu router (ej: 'sexos', 'estados')
    """
    try:
        if method != 'GET':
            return json.dumps({"success": False, "msg": "Método no permitido"}).encode('utf-8')

        data = []

        if catalog_type == 'sexos':
            data = CatalogoService.get_sexos()
        elif catalog_type == 'estados':
            data = CatalogoService.get_estados()
        elif catalog_type == 'perfiles':
            data = CatalogoService.get_perfiles()
        elif catalog_type == 'modulos':
            data = CatalogoService.get_modulos()
        elif catalog_type == 'menus':
            data = CatalogoService.get_menus()

        return json.dumps(data).encode('utf-8')

    except Exception as e:
        return json.dumps({
            "success": False,
            "msg": f"Error en catálogo: {str(e)}"
        }).encode('utf-8')
