# Sistema de Gestión de Seguridad y Módulos Dinámicos (Python RBAC)

Este proyecto es una plataforma web ligera y segura desarrollada en **Python**, diseñada para la administración de usuarios, perfiles y permisos mediante una interfaz moderna y una estructura de menús dinámica basada en la base de datos. Destaca por construir sus propias herramientas (como el motor de plantillas) sin depender de frameworks pesados.

## 🚀 Características Principales

* **Menú Lateral Dinámico**: El sidebar se genera automáticamente consultando el perfil del usuario logueado en la base de datos, organizando módulos por secciones como "Seguridad", "Principal 1" y "Principal 2".
* **Control de Acceso Granular (RBAC)**: Cada módulo verifica permisos específicos (`bitAgregar`, `bitEditar`, `bitEliminar`, `bitConsulta`) antes de renderizar acciones en la interfaz. Protegido tanto en backend como en frontend.
* **Vistas Genéricas Inteligentes**: Implementación de un controlador único (`modulo_simulado_action`) que normaliza rutas y nombres de archivos `.html` dinámicamente basándose en el nombre del módulo.
* **Motor de Plantillas Personalizado (`render_view`)**: Sistema propio en Python para la inyección de datos dinámicos (JSON y variables) directamente en el DOM, pasando la información de forma segura al cliente.
* **Interfaz Moderna y Reactiva**: Diseño basado en componentes limpios construido con Vanilla JS, con buscador estilo "Google Pill", tablas modernas asíncronas y modales responsivos.

## 💻 Tecnologías Utilizadas (Tech Stack)

* **Backend:** Python (Vanilla / Framework minimalista propio)
* **Frontend:** HTML5, CSS3, Vanilla JavaScript (ES6+)
* **Base de Datos:** [Escribe aquí tu BD, ej. MySQL / SQL Server]
* **Arquitectura:** Patrón MVC (Modelo-Vista-Controlador) adaptado a servicios.

## 🛠️ Estructura del Proyecto

```text
Python_web_seguridad/
├── core/
│   └── render.py            # Motor propio de renderizado de vistas e inyección de datos
├── services/
│   ├── permisos_service.py  # Lógica de consulta de permisos por perfil
│   └── home_service.py      # Generación de estructura de menú jerárquica
├── static/
│   ├── css/                 # Estilos modulares (layout.css, users.css)
│   └── js/                  # Lógica de cliente y manejo de DOM (layout.js)
├── templates/
│   ├── principal1/          # Vistas para el grupo Principal 1 (p1_1.html)
│   └── principal2/          # Vistas para el grupo Principal 2 (p2_1.html)
└── server_local.py          # Punto de entrada del servidor de desarrollo