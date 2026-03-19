import json
from posix import environ
from services.permisos_service import PermisosService
from services.home_service import HomeService
from core.render import render_view
from controllers.error_controller import not_found_action


def modulo_simulado_action(breadcrumbs, environ, seccion, nombre_modulo):
    user = environ.get('app.current_user', {})
    id_perfil_logeado = user.get('id_perfil', 1)

    todos_los_permisos = PermisosService.get_permisos_by_perfil(id_perfil_logeado)

    print(f"\n[DEBUG PYTHON] Buscando permisos para el módulo: '{nombre_modulo}'")

    permisos_modulo = next(
        (p for p in todos_los_permisos if str(p.get('strNombreModulo')).strip().lower() == nombre_modulo.strip().lower()),
        None 
    )

    if permisos_modulo is None:
        print(f"[DEBUG PYTHON] ❌ No se encontró el módulo '{nombre_modulo}'. Asignando False por defecto.")
        # ¡AHORA SÍ ESTÁ INDENTADO! Solo entra aquí si no lo encuentra
        permisos_modulo = {
            "bitAgregar": False, "bitEditar": False, "bitEliminar": False
        }
    else:
        print(f"[DEBUG PYTHON] ✅ Permisos encontrados en BD: {permisos_modulo}")

    datos_estaticos = [
        {"id": 1, "nombre": f"Registro Prueba A - {nombre_modulo}", "estado": "Activo"},
        {"id": 2, "nombre": f"Registro Prueba B - {nombre_modulo}", "estado": "Inactivo"},
        {"id": 3, "nombre": f"Registro Prueba C - {nombre_modulo}", "estado": "Activo"},
    ]

    if not permisos_modulo.get('bitConsulta', False):
        return not_found_action(breadcrumbs, environ)

    menu_dinamico = HomeService.get_sidebar_menu(id_perfil_logeado)
    archivo_nombre = nombre_modulo.replace("Principal ", "p").replace(".", "_").lower()

    # Log final antes de enviar a HTML
    print(f"[DEBUG PYTHON] JSON que se enviará a la vista: {json.dumps(permisos_modulo)}")

    return render_view(f'{seccion}/{archivo_nombre}.html', {
        "titulo": nombre_modulo,
        "breadcrumbs": breadcrumbs,
        "menu_sidebar": menu_dinamico,
        "user_nombre": user.get('nombre_completo', 'Usuario'),
        "user_email": user.get('email', ''),
        "user_iniciales": user.get('iniciales', 'U'),
        "permisos_json": json.dumps(permisos_modulo),
        "datos_json": json.dumps(datos_estaticos)
    })