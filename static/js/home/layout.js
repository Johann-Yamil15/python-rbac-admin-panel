document.addEventListener('DOMContentLoaded', function () {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    const btnToggle = document.getElementById('btnToggle');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');

    // --- LÓGICA DE NAVEGACIÓN Y MENÚS DESPLEGABLES ---
    navLinks.forEach(link => {
        link.classList.remove('active');
        const linkPath = link.getAttribute('href');

        if (currentPath === linkPath || (linkPath !== '#' && currentPath.startsWith(linkPath) && linkPath !== '/')) {
            link.classList.add('active');

            // Si el link activo está dentro de un submenú (collapse), ábrelo
            const parentCollapse = link.closest('.collapse');
            if (parentCollapse) {
                parentCollapse.classList.add('show'); // Clase de Bootstrap para mostrar
                // Opcional: Cambiar el estado del botón disparador para que la flecha rote
                const trigger = document.querySelector(`[href="#${parentCollapse.id}"]`);
                if (trigger) trigger.setAttribute('aria-expanded', 'true');
                trigger.classList.add('active');
            }
        }
    });

    // --- TOGGLE MOBILE ---
    if (btnToggle && sidebar && overlay) {
        btnToggle.addEventListener('click', () => {
            sidebar.classList.add('active');
            overlay.classList.add('active');
        });

        overlay.addEventListener('click', () => {
            sidebar.classList.remove('active');
            overlay.classList.remove('active');
        });
    }

    // Reiniciar Lucide para los iconos generados dinámicamente
    if (window.lucide) {
        window.lucide.createIcons();
    }
});