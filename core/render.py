from multiprocessing import context
import os
import re

def resolve_dot_notation(context):
    flat = {}
    for key, value in context.items():
        if key == 'menu_sidebar':
            continue
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                flat[f"{key}.{sub_key}"] = sub_value
        else:
            flat[key] = value
    return flat

def render_view(template_name, context={}):
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    base_path = os.path.join(current_dir, 'views')
    
    layout_path = os.path.join(base_path, 'home', 'layout.html')
    
    try:
        with open(layout_path, 'r', encoding='utf-8') as f:
            layout = f.read()
    except FileNotFoundError:
        return f"Error Crítico: No se encontró el layout en {layout_path}".encode('utf-8')

    template_path = os.path.join(base_path, template_name)
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        return f"Error: No se encontró la vista {template_name} en {template_path}".encode('utf-8')
    
    final_html = layout.replace('{{content}}', content)

    # --- NUEVA LÓGICA PARA MENÚ DINÁMICO (Sustituye al {% for %}) ---
    if 'menu_sidebar' in context:
        menu_html = ""
        for menu in context['menu_sidebar']:
            # Construimos el bloque del menú principal (Padre)
            menu_html += f'''
            <div class="nav-dropdown-wrapper">
                <a class="nav-link d-flex justify-content-between align-items-center" 
                   data-bs-toggle="collapse" href="#{menu['id_html']}" role="button" aria-expanded="false">
                    <div class="d-flex align-items-center gap-12">
                        <i data-lucide="folder"></i>
                        <span>{menu['titulo']}</span>
                    </div>
                    <i data-lucide="chevron-down" class="chevron-icon" size="14"></i>
                </a>
                <div class="collapse" id="{menu['id_html']}">
                    <div class="nav-sub-items">'''
            
            # Construimos los submenús (Hijos)
            for sub in menu['submodulos']:
                menu_html += f'''
                        <a href="{sub['ruta']}" class="nav-link sub-link">
                            <i data-lucide="circle" size="12"></i> {sub['nombre']}
                        </a>'''
            
            menu_html += '''
                    </div>
                </div>
            </div>'''
        
        # Reemplazamos un placeholder específico en el layout
        final_html = final_html.replace('{{menu_sidebar_placeholder}}', menu_html)
    else:
        final_html = final_html.replace('{{menu_sidebar_placeholder}}', '')

    # --- Lógica de breadcrumbs (Mantienes la tuya) ---
    if 'breadcrumbs' in context:
        bc_html = ""
        for i, bc in enumerate(context['breadcrumbs']):
            is_last = i == len(context['breadcrumbs']) - 1
            if is_last:
                bc_html += f'<span class="bc-current">{bc["name"]}</span>'
            else:
                bc_html += f'<a href="{bc["url"]}" class="bc-item">{bc["name"]}</a>'
                bc_html += '<span class="bc-sep">/</span>'
        final_html = final_html.replace('{{breadcrumbs_placeholder}}', bc_html)
    else:
        final_html = final_html.replace('{{breadcrumbs_placeholder}}', 'Dashboard')

    # Reemplazo de variables generales
    # for key, value in context.items():
    #     if key != 'menu_sidebar': # Evitamos procesar la lista como string simple
    #         placeholder = '{{' + key + '}}'
    #         final_html = final_html.replace(placeholder, str(value))

    flat_context = resolve_dot_notation(context)

    print("[DEBUG] flat_context keys:", list(flat_context.keys()))  # ← verifica aquí

    for key, value in flat_context.items():
        patron = r'\{\{\s*' + re.escape(key) + r'\s*\}\}'
        str_value = str(value) if value is not None else ''
        final_html = re.sub(patron, lambda m, v=str_value: v, final_html)

    return final_html.encode('utf-8')