const PerfilManager = {
    allPerfiles: [],
    filteredPerfiles: [],
    currentPage: 1,
    rowsPerPage: 5,

    init() {
        this.tableBody = document.getElementById('perfilTableBody');
        this.form = document.getElementById('perfilForm');
        this.modal = document.getElementById('perfilModal');
        this.deleteModal = document.getElementById('deleteModal');
        
        // Inputs de búsqueda
        this.searchInput = document.getElementById('searchInput');
        this.btnClear = document.getElementById('btnClearFilters');
        
        // Botón Nuevo Perfil
        this.btnNew = document.getElementById('btnNewPerfil');

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

        this.bindEvents();
        this.loadPerfiles();
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
            const maxPage = Math.ceil(this.filteredPerfiles.length / this.rowsPerPage);
            if (this.currentPage < maxPage) { this.currentPage++; this.renderTableWithPagination(); }
        };
        if (this.btnLast) this.btnLast.onclick = () => {
            this.currentPage = Math.ceil(this.filteredPerfiles.length / this.rowsPerPage) || 1;
            this.renderTableWithPagination();
        };
    },

    async loadPerfiles() {
        try {
            const res = await fetch('/api/perfiles');
            const data = await res.json();
            this.allPerfiles = Array.isArray(data) ? data : [];
            this.applyFilters();
        } catch (e) {
            this.showToast("Error al cargar perfiles", 'error');
        }
    },

    applyFilters() {
        const term = this.searchInput.value.toLowerCase().trim();
        
        this.filteredPerfiles = this.allPerfiles.filter(p => {
            const name = p.strNombrePerfil.toLowerCase();
            return term === "" || name.includes(term);
        });

        this.currentPage = 1;
        this.renderTableWithPagination();
    },

    renderTableWithPagination() {
        const total = this.filteredPerfiles.length;
        const maxPage = Math.ceil(total / this.rowsPerPage) || 1;

        if (this.currentPage > maxPage) this.currentPage = maxPage;
        
        const start = (this.currentPage - 1) * this.rowsPerPage;
        const end = start + this.rowsPerPage;
        const pagedData = this.filteredPerfiles.slice(start, end);

        this.renderTable(pagedData);

        if (this.pageIndicator) {
            this.pageIndicator.innerText = `Página ${this.currentPage} de ${maxPage}`;
        }

        // Bloqueo de botones de paginación
        if(this.btnFirst) {
            this.btnFirst.disabled = this.currentPage === 1;
            this.btnPrev.disabled = this.currentPage === 1;
            this.btnNext.disabled = this.currentPage === maxPage || total === 0;
            this.btnLast.disabled = this.currentPage === maxPage || total === 0;
        }
    },

    renderTable(data) {
        if (data.length > 0) {
            this.tableBody.innerHTML = data.map(p => {
                
                // --- LÓGICA DE PERMISOS PARA BOTONES EN TABLA ---
                let botonesAccion = '';

                if (typeof PERMISOS_MODULO !== 'undefined') {
                    if (PERMISOS_MODULO.canEdit) {
                        botonesAccion += `<button class="btn-edit" onclick="PerfilManager.openModal(${p.id})"><i class="fas fa-edit"></i></button>`;
                    }
                    if (PERMISOS_MODULO.canDelete) {
                        botonesAccion += `<button class="btn-delete" onclick="PerfilManager.confirmDelete(${p.id})"><i class="fas fa-trash"></i></button>`;
                    }
                }

                // Si no tiene permisos, mostrar un mensaje
                if (!botonesAccion) {
                    botonesAccion = '<span class="text-muted small">Sin permisos</span>';
                }

                return `
                <tr>
                    <td style="font-weight: 600; color: #1e293b;">${p.strNombrePerfil}</td>
                    <td>
                        <span class="badge" 
                              style="padding: 4px 12px; border-radius: 20px; font-weight: 700; font-size: 11px; 
                              background: ${p.bitAdministrador ? '#10b981' : '#0ea5e9'}; color: white;">
                            ${p.bitAdministrador ? 'SÍ' : 'NO'}
                        </span>
                    </td>
                    <td style="text-align: center;">
                        ${botonesAccion}
                    </td>
                </tr>
            `;
            }).join('');
        } else {
            this.tableBody.innerHTML = '<tr><td colspan="3" style="text-align:center; padding: 20px;">No se encontraron perfiles.</td></tr>';
        }
    },

    async openModal(id = null) {
        this.form.reset();
        this.form.id.value = id || "";
        
        const modalTitle = document.getElementById('modalTitle');
        const submitBtn = this.form.querySelector('button[type="submit"]');
        
        // Reset del botón
        submitBtn.disabled = false;
        submitBtn.style.opacity = "1";
        submitBtn.innerHTML = id ? '<span>Guardar Cambios</span> <i class="fas fa-check"></i>' : '<span>Crear Perfil</span> <i class="fas fa-plus"></i>';
        
        modalTitle.innerText = id ? 'Editar Perfil' : 'Nuevo Perfil';

        if (id) {
            try {
                const res = await fetch(`/api/perfiles?id=${id}`);
                const p = await res.json();
                this.form.strNombrePerfil.value = p.strNombrePerfil;
                this.form.bitAdministrador.checked = p.bitAdministrador;
            } catch (e) {
                this.showToast("Error al obtener datos", 'error');
            }
        }
        this.modal.style.display = 'flex';
    },

    closeModal() { this.modal.style.display = 'none'; },

    confirmDelete(id) {
        this.perfilToDeleteId = id;
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
            const res = await fetch('/api/perfiles', {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id: this.perfilToDeleteId })
            });
            const result = await res.json();
            if (result.success) {
                this.showToast("Perfil eliminado correctamente", 'warning');
                this.loadPerfiles();
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
            const res = await fetch('/api/perfiles', {
                method: id ? 'PUT' : 'POST',
                body: formData
            });
            const result = await res.json();
            if (result.success) {
                this.showToast(id ? "Perfil actualizado con éxito" : "Perfil creado con éxito", 'success');
                this.closeModal();
                this.loadPerfiles();
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

document.addEventListener('DOMContentLoaded', () => PerfilManager.init());