const ModuloManager = {
    allModulos: [],
    filteredModulos: [],
    currentPage: 1,
    rowsPerPage: 5,
    menusData: [], // Variable para guardar los menús crudos
    currentMenuId: null, // Guardará el ID del menú si existe

    init() {
        this.tableBody = document.getElementById('moduloTableBody');
        this.form = document.getElementById('moduloForm');
        this.modal = document.getElementById('moduloModal');
        this.deleteModal = document.getElementById('deleteModal');

        // Inputs de búsqueda
        this.searchInput = document.getElementById('searchInput');
        this.btnClear = document.getElementById('btnClearFilters');

        // Botón Nuevo Módulo
        this.btnNew = document.getElementById('btnNewModulo');

        // Paginación
        this.btnFirst = document.getElementById('btnFirst');
        this.btnPrev = document.getElementById('btnPrev');
        this.btnNext = document.getElementById('btnNext');
        this.btnLast = document.getElementById('btnLast');
        this.pageIndicator = document.getElementById('currentPageIndicator');

        // --- LÓGICA DE PERMISOS: Ocultar botón 'Nuevo' ---
        if (this.btnNew && typeof PERMISOS_MODULO !== 'undefined') {
            if (!PERMISOS_MODULO.canAdd) {
                this.btnNew.style.display = 'none';
            }
        }

        const inputMenu = document.getElementById('nombreMenu');
        if (inputMenu) {
            inputMenu.addEventListener('input', () => this.checkMenuExists());
        }

        this.bindEvents();
        this.loadMenus();
        this.loadModulos();
    },

    bindEvents() {
        this.form.onsubmit = (e) => this.handleSubmit(e);

        if (this.searchInput) {
            this.searchInput.addEventListener('input', () => this.applyFilters());
        }

        if (this.btnClear) {
            this.btnClear.onclick = () => {
                this.searchInput.value = "";
                this.applyFilters();
            };
        }

        // Eventos de paginación con validación de existencia
        if (this.btnFirst) this.btnFirst.onclick = () => { this.currentPage = 1; this.renderTableWithPagination(); };
        if (this.btnPrev) this.btnPrev.onclick = () => { if (this.currentPage > 1) { this.currentPage--; this.renderTableWithPagination(); } };
        if (this.btnNext) this.btnNext.onclick = () => {
            const maxPage = Math.ceil(this.filteredModulos.length / this.rowsPerPage);
            if (this.currentPage < maxPage) { this.currentPage++; this.renderTableWithPagination(); }
        };
        if (this.btnLast) this.btnLast.onclick = () => {
            this.currentPage = Math.ceil(this.filteredModulos.length / this.rowsPerPage) || 1;
            this.renderTableWithPagination();
        };
    },

    async loadMenus() {
        try {
            const res = await fetch('/api/menus');
            const menus = await res.json();

            // Guardamos la info completa (que debería traer el 'id' y 'strNombreMenu')
            this.menusData = Array.isArray(menus) ? menus : [];

            const datalist = document.getElementById('menusList');
            if (datalist) {
                datalist.innerHTML = this.menusData.map(m =>
                    `<option value="${m.strNombreMenu}"></option>`
                ).join('');
            }
            // Revisamos si el input actual coincide con algún menú recién cargado
            this.checkMenuExists();
        } catch (e) {
            console.error("Error al cargar los menús:", e);
        }
    },

    // Esta función oculta o muestra los botones "Editar / Eliminar"
    checkMenuExists() {
        const inputVal = this.form.nombreMenu.value.trim().toLowerCase();
        // Buscamos si lo escrito coincide con un menú existente
        const menuEncontrado = this.menusData.find(m => m.strNombreMenu.toLowerCase() === inputVal);

        const actionsDiv = document.getElementById('menuActions');
        if (menuEncontrado) {
            this.currentMenuId = menuEncontrado.id; // ¡Lo encontramos! Guardamos su ID
            actionsDiv.style.display = 'flex';      // Mostramos los botones
        } else {
            this.currentMenuId = null;              // Es un menú nuevo
            actionsDiv.style.display = 'none';      // Ocultamos los botones
        }
    },

    async editMenu(e) {
        e.preventDefault();
        if (!this.currentMenuId) return;
        
        const oldName = this.form.nombreMenu.value;

        // --- SweetAlert2 en lugar de prompt() ---
        const { value: newName } = await Swal.fire({
            title: 'Editar Menú Padre',
            text: "Escribe el nuevo nombre para este menú:",
            input: 'text',
            inputValue: oldName,
            icon: 'info',
            showCancelButton: true,
            confirmButtonColor: '#3b82f6', // Tu color azul
            cancelButtonColor: '#6c757d',
            confirmButtonText: '<i class="fas fa-save"></i> Guardar',
            cancelButtonText: 'Cancelar',
            inputValidator: (value) => {
                if (!value || value.trim() === "") {
                    return 'El nombre no puede estar vacío';
                }
            }
        });
        
        // Si canceló o no cambió el nombre, no hacemos nada
        if (!newName || newName.trim() === oldName) return;

        try {
            const res = await fetch('/api/menus', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id: this.currentMenuId, strNombreMenu: newName.trim() })
            });
            const result = await res.json();
            if (result.success) {
                this.showToast("Menú actualizado con éxito", "success");
                this.form.nombreMenu.value = newName.trim();
                await this.loadMenus();    
                this.loadModulos();        
            } else {
                this.showToast(result.msg || "Error al actualizar", "error");
            }
        } catch(err) {
            this.showToast("Error de conexión", "error");
        }
    },

    async deleteMenu(e) {
        e.preventDefault();
        if (!this.currentMenuId) return;
        
        // --- SweetAlert2 en lugar de confirm() ---
        const confirmacion = await Swal.fire({
            title: '¿Eliminar Menú?',
            html: `¿Estás seguro de eliminar el menú <b>"${this.form.nombreMenu.value}"</b>?<br><br><span style="font-size:0.9em; color:#666;">OJO: El sistema solo te permitirá borrarlo si no tiene módulos adentro.</span>`,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#ef4444', // Color rojo para eliminar
            cancelButtonColor: '#6c757d',
            confirmButtonText: '<i class="fas fa-trash"></i> Sí, eliminar',
            cancelButtonText: 'Cancelar'
        });
        
        // Verificamos si el usuario dio clic en el botón de confirmar
        if (confirmacion.isConfirmed) {
            try {
                const res = await fetch('/api/menus', {
                    method: 'DELETE',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ id: this.currentMenuId })
                });
                const result = await res.json();
                if (result.success) {
                    this.showToast("Menú eliminado con éxito", "success");
                    this.form.nombreMenu.value = "";
                    await this.loadMenus();
                } else {
                    Swal.fire('No se pudo eliminar', result.msg || "Tiene módulos asociados.", 'warning');
                }
            } catch(err) {
                this.showToast("Error de conexión", "error");
            }
        }
    },

    async loadModulos() {
        try {
            const res = await fetch('/api/modulos');
            const data = await res.json();
            this.allModulos = Array.isArray(data) ? data : [];
            this.applyFilters();
        } catch (e) {
            this.showToast("Error al cargar módulos", 'error');
        }
    },

    applyFilters() {
        const term = this.searchInput.value.toLowerCase().trim();

        this.filteredModulos = this.allModulos.filter(m => {
            const name = m.strNombreModulo.toLowerCase();
            return term === "" || name.includes(term);
        });

        this.currentPage = 1;
        this.renderTableWithPagination();
    },

    renderTableWithPagination() {
        const total = this.filteredModulos.length;
        const maxPage = Math.ceil(total / this.rowsPerPage) || 1;

        if (this.currentPage > maxPage) this.currentPage = maxPage;

        const start = (this.currentPage - 1) * this.rowsPerPage;
        const end = start + this.rowsPerPage;
        const pagedData = this.filteredModulos.slice(start, end);

        this.renderTable(pagedData);

        if (this.pageIndicator) {
            this.pageIndicator.innerText = `Página ${this.currentPage} de ${maxPage}`;
        }

        // Bloqueo de botones de paginación
        if (this.btnFirst) {
            this.btnFirst.disabled = this.currentPage === 1;
            this.btnPrev.disabled = this.currentPage === 1;
            this.btnNext.disabled = this.currentPage === maxPage || total === 0;
            this.btnLast.disabled = this.currentPage === maxPage || total === 0;
        }
    },

    renderTable(data) {
        if (data.length > 0) {
            this.tableBody.innerHTML = data.map(m => {

                // --- LÓGICA DE PERMISOS PARA BOTONES EN TABLA ---
                let botonesAccion = '';

                if (typeof PERMISOS_MODULO !== 'undefined') {
                    if (PERMISOS_MODULO.canEdit) {
                        botonesAccion += `<button class="btn-edit" onclick="ModuloManager.openModal(${m.id})"><i class="fas fa-edit"></i></button>`;
                    }
                    if (PERMISOS_MODULO.canDelete) {
                        botonesAccion += `<button class="btn-delete" onclick="ModuloManager.confirmDelete(${m.id})"><i class="fas fa-trash"></i></button>`;
                    }
                }

                // Si no tiene permisos, mostrar un mensaje
                if (!botonesAccion) {
                    botonesAccion = '<span class="text-muted small">Sin permisos</span>';
                }

                return `
                <tr>
                    <td style="font-weight: 600; color: #1e293b;">${m.strNombreModulo}</td>
                    <td>
                        <span class="badge" 
                              style="padding: 4px 12px; border-radius: 20px; font-weight: 600; font-size: 11px; 
                              background: #f1f5f9; color: #475569; border: 1px solid #e2e8f0;">
                            <i class="fas fa-folder" style="margin-right: 4px; color: #94a3b8;"></i> ${m.strNombreMenu}
                        </span>
                    </td>
                    <td style="color: #64748b; font-family: monospace; font-size: 13px;">${m.strRuta || '-'}</td>
                    <td style="text-align: center;">
                        ${botonesAccion}
                    </td>
                </tr>
            `;
            }).join('');
        } else {
            this.tableBody.innerHTML = '<tr><td colspan="4" style="text-align:center; padding: 20px;">No se encontraron módulos.</td></tr>';
        }
    },

    async openModal(id = null) {
        this.form.reset();
        this.form.id.value = id || "";

        const modalTitle = document.getElementById('modalTitle');
        const submitBtn = this.form.querySelector('button[type="submit"]');

        submitBtn.disabled = false;
        submitBtn.style.opacity = "1";
        submitBtn.innerHTML = id ? '<span>Guardar Cambios</span> <i class="fas fa-check"></i>' : '<span>Crear Módulo</span> <i class="fas fa-plus"></i>';

        modalTitle.innerText = id ? 'Editar Módulo' : 'Nuevo Módulo';

        if (id) {
            try {
                const res = await fetch(`/api/modulos?id=${id}`);
                const m = await res.json();
                this.form.strNombreModulo.value = m.strNombreModulo;
                // CAMBIO AQUÍ 👇
                this.form.nombreMenu.value = m.strNombreMenu || '';
                this.form.strRuta.value = m.strRuta || '';
            } catch (e) {
                this.showToast("Error al obtener datos", 'error');
            }
        }
        this.modal.style.display = 'flex';
    },

    closeModal() { this.modal.style.display = 'none'; },

    confirmDelete(id) {
        this.moduloToDeleteId = id;
        this.deleteModal.style.display = 'flex';
        const confirmBtn = document.getElementById('confirmDeleteBtn');
        confirmBtn.disabled = false;
        confirmBtn.innerText = "Sí, eliminar";
        confirmBtn.onclick = () => this.executeDelete();
    },

    closeDeleteModal() { this.deleteModal.style.display = 'none'; },

    async executeDelete() {
        const confirmBtn = document.getElementById('confirmDeleteBtn');
        confirmBtn.disabled = true;
        confirmBtn.innerText = "Eliminando...";

        try {
            const res = await fetch('/api/modulos', {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id: this.moduloToDeleteId })
            });
            const result = await res.json();
            if (result.success) {
                this.showToast("Módulo eliminado correctamente", 'warning');
                this.loadModulos();
            } else {
                this.showToast(result.msg || "Error al eliminar", 'error');
            }
        } catch (e) {
            this.showToast("Error al eliminar", 'error');
        } finally {
            this.closeDeleteModal();
        }
    },

    async handleSubmit(e) {
        e.preventDefault();
        const submitBtn = this.form.querySelector('button[type="submit"]');
        const originalContent = submitBtn.innerHTML;

        // Estado de carga
        submitBtn.disabled = true;
        submitBtn.style.opacity = "0.7";
        submitBtn.innerHTML = '<span>Guardando...</span> <i class="fas fa-spinner fa-spin"></i>';

        const formData = new FormData(this.form);
        const id = formData.get('id');

        try {
            const res = await fetch('/api/modulos', {
                method: id ? 'PUT' : 'POST',
                body: formData
            });
            const result = await res.json();
            if (result.success) {
                this.showToast(id ? "Módulo actualizado con éxito" : "Módulo creado con éxito", 'success');
                this.closeModal();
                this.loadModulos();
            } else {
                this.showToast(result.msg || "Error al procesar", 'error');
            }
        } catch (e) {
            this.showToast("Error de conexión al guardar", 'error');
        } finally {
            submitBtn.disabled = false;
            submitBtn.style.opacity = "1";
            submitBtn.innerHTML = originalContent;
        }
    },

    // --- LÓGICA DE NOTIFICACIONES RESCATADA ---
    showToast(msg, type = 'success') {
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container';
            document.body.appendChild(container);
        }

        const existingToasts = Array.from(container.querySelectorAll('.toast-message'));
        if (existingToasts.some(t => t.innerText === msg)) return;

        const config = {
            success: { icon: 'fa-check-circle', title: 'Éxito' },
            error: { icon: 'fa-times-circle', title: 'Error' },
            warning: { icon: 'fa-exclamation-triangle', title: 'Atención' },
            info: { icon: 'fa-info-circle', title: 'Info' }
        };

        const typeKey = typeof type === 'boolean' ? (type ? 'success' : 'error') : type;
        const { icon, title } = config[typeKey] || config.success;

        const toast = document.createElement('div');
        toast.className = `toast ${typeKey}`;
        toast.innerHTML = `
            <i class="fas ${icon}"></i>
            <div class="toast-content">
                <span class="toast-title">${title}</span>
                <span class="toast-message">${msg}</span>
            </div>
            <i class="fas fa-times" style="cursor:pointer; font-size: 12px; opacity: 0.7;" onclick="this.parentElement.remove()"></i>
        `;

        container.appendChild(toast);
        setTimeout(() => {
            if (toast.parentElement) {
                toast.style.opacity = '0';
                toast.style.transform = 'translateX(100%)';
                toast.style.transition = 'all 0.4s ease';
                setTimeout(() => toast.remove(), 400);
            }
        }, 4000);
    }
};

document.addEventListener('DOMContentLoaded', () => ModuloManager.init());