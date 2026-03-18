const UserManager = {
    allUsers: [],
    filteredUsers: [], // Para guardar el resultado de filtros antes de paginar
    allDepartments: [],
    currentPage: 1,
    rowsPerPage: 5,

    init() {
        this.form = document.getElementById('userForm');
        this.tableBody = document.getElementById('userTableBody');
        this.modal = document.getElementById('userModal');
        this.btnNew = document.getElementById('btnNewUser');
        this.deptoSelect = document.getElementById('deptoSelect');

        // Inputs de búsqueda y filtros
        this.searchInput = document.getElementById('searchInput');
        this.dateFrom = document.getElementById('dateFrom');
        this.dateTo = document.getElementById('dateTo');
        this.btnToggle = document.getElementById('btnToggleFilters');
        this.advancedFilters = document.getElementById('advancedFilters');
        this.btnClear = document.getElementById('btnClearFilters');

        // Elementos de validación
        this.birthdateInput = document.getElementById('birthdateInput');
        this.emailInput = document.getElementById('emailInput');

        // Elementos de paginación
        this.btnFirst = document.getElementById('btnFirst');
        this.btnPrev = document.getElementById('btnPrev');
        this.btnNext = document.getElementById('btnNext');
        this.btnLast = document.getElementById('btnLast');
        this.pageIndicator = document.getElementById('currentPageIndicator');

        // Nuevos elementos para la imagen
        this.inputFile = document.getElementById('imagenInput');
        this.previewImg = document.getElementById('previewImg');
        this.previewContainer = document.getElementById('previewContainer');
        this.fileError = document.getElementById('fileError');

        this.bindEvents();
        this.setupValidations();
        this.loadCatalogos().then(() => this.loadUsers());
    },

    bindEvents() {
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        this.btnNew.onclick = () => this.openModal();

        if (this.btnToggle) {
            this.btnToggle.onclick = () => {
                const pill = document.getElementById('searchPill');
                const isNowCollapsed = this.advancedFilters.classList.toggle('collapsed');
                pill.classList.toggle('expanded', !isNowCollapsed);
            };
        }

        if (this.btnClear) {
            this.btnClear.onclick = () => this.resetFilters();
        }

        [this.searchInput, this.dateFrom, this.dateTo].forEach(el => {
            if (el) el.addEventListener('input', () => this.applyFilters());
        });

        if (this.btnNew && typeof PERMISOS_MODULO !== 'undefined') {
            if (!PERMISOS_MODULO.canAdd) { // Asegúrate de que el nombre coincida con tu objeto global
                this.btnNew.style.display = 'none';
            }
        }

        // Eventos de paginación
        if (this.btnFirst) this.btnFirst.onclick = () => { this.currentPage = 1; this.renderTableWithPagination(); };
        if (this.btnPrev) this.btnPrev.onclick = () => { if (this.currentPage > 1) { this.currentPage--; this.renderTableWithPagination(); } };
        if (this.btnNext) this.btnNext.onclick = () => {
            const maxPage = Math.ceil(this.filteredUsers.length / this.rowsPerPage);
            if (this.currentPage < maxPage) { this.currentPage++; this.renderTableWithPagination(); }
        };
        if (this.btnLast) this.btnLast.onclick = () => {
            this.currentPage = Math.ceil(this.filteredUsers.length / this.rowsPerPage) || 1;
            this.renderTableWithPagination();
        };
        if (this.inputFile) {
            this.inputFile.addEventListener('change', (e) => this.handleImageValidation(e));
        }
    },

    // Lógica de validación de imagen
    handleImageValidation(e) {
        const file = e.target.files[0];
        const btnGuardar = this.form.querySelector('button[type="submit"]');

        // Reset estados
        btnGuardar.disabled = false; // Permitimos guardar si no hay archivo (opcional)
        if (this.fileError) this.fileError.classList.add("d-none");
        if (this.previewContainer) this.previewContainer.classList.add("d-none");

        if (!file) return;

        const allowed = ["jpg", "jpeg", "png", "webp"];
        const ext = file.name.split(".").pop().toLowerCase();

        if (!allowed.includes(ext)) {
            if (this.fileError) this.fileError.classList.remove("d-none");
            e.target.value = "";
            btnGuardar.disabled = true;
            return;
        }

        // Vista previa
        const reader = new FileReader();
        reader.onload = (e) => {
            this.previewImg.src = e.target.result;
            this.previewContainer.classList.remove("d-none");
        };
        reader.readAsDataURL(file);
    },

    renderSkeleton() {
        const skeletonRow = `
            <tr>
                <td><div class="skeleton skeleton-text"></div></td>
                <td><div class="skeleton skeleton-text"></div></td>
                <td><div class="skeleton skeleton-text"></div></td>
                <td><div class="skeleton skeleton-text"></div></td> 
                <td>
                    <div class="skeleton skeleton-btn"></div>
                    <div class="skeleton skeleton-btn"></div>
                </td>
            </tr>
        `;
        this.tableBody.innerHTML = skeletonRow.repeat(5);
    },

    async loadCatalogos() {
        try {
            // Cargamos los 3 catálogos en paralelo
            const [resP, resS, resE] = await Promise.all([
                fetch('/api/perfil'), // Ajusta estas rutas a tus endpoints reales
                fetch('/api/sexos'),
                fetch('/api/estados')
            ]);

            const perfiles = await resP.json();
            const sexos = await resS.json();
            const estados = await resE.json();

            // Guardamos para uso global si es necesario
            this.allPerfiles = perfiles;

            // Llenar select Perfil
            document.getElementById('deptoSelect').innerHTML = '<option value="">Seleccione un perfil...</option>' +
                perfiles.map(p => `<option value="${p.id}">${p.strNombrePerfil}</option>`).join('');

            // Llenar select Sexo
            document.getElementById('sexoSelect').innerHTML = '<option value="">Seleccione sexo...</option>' +
                sexos.map(s => `<option value="${s.id}">${s.strSexo}</option>`).join('');

            // Llenar select Estado
            document.getElementById('estadoSelect').innerHTML = '<option value="">Seleccione un estado...</option>' +
                estados.map(e => `<option value="${e.id}">${e.strNombreEstado}</option>`).join('');

        } catch (e) {
            console.error("Error cargando catálogos:", e);
            this.allPerfiles = []; // Aseguramos que no falle el render si no se cargan perfiles
        }
    },

    // Modificado: Ahora acepta los usuarios segmentados para renderizar la vista actual
    renderTable(users) {
        if (Array.isArray(users) && users.length > 0) {
            this.tableBody.innerHTML = users.map(u => {
                // --- NUEVA LÓGICA PARA BUSCAR EL NOMBRE DEL PERFIL ---
                const perfilObj = (this.allPerfiles || []).find(p => p.id == u.id_perfil);
                const nombrePerfil = perfilObj ? perfilObj.strNombrePerfil : 'Sin Perfil';
                // ------------------------------------------------------

                // --- LÓGICA DE PERMISOS PARA BOTONES ---
                let botonesAccion = '';

                if (PERMISOS_MODULO.canEdit) {
                    botonesAccion += `<button class="btn-edit" onclick="UserManager.openModal(${u.id})"><i class="fas fa-edit"></i></button>`;
                }

                if (PERMISOS_MODULO.canDelete) {
                    botonesAccion += `<button class="btn-delete" onclick="UserManager.delete(${u.id})"><i class="fas fa-trash"></i></button>`;
                }

                // Si no tiene ninguno de los dos, puedes mostrar un texto o dejar vacío
                if (!botonesAccion) botonesAccion = '<span class="text-muted small">Sin permisos</span>';

                return `
            <tr>
                <td><img src="${u.imagen_path ? '/' + u.imagen_path.replace(/\\/g, '/') : '/static/img/default-user.png'}" width="40" class="rounded-circle"></td>
                <td>${u.nombre_completo}</td>
                <td>${u.email}</td>
                <td>${u.id_sexo == 1 ? 'Masculino' : 'Femenino'}</td> 
                <td>${u.celular || 'N/A'}</td>
                <td>${nombrePerfil}</td> <td><span class="badge ${u.id_estado == 1 ? 'bg-success' : 'bg-danger'}">${u.id_estado == 1 ? 'Activo' : 'Inactivo'}</span></td>
                <td>
                    ${botonesAccion}
                </td>
            </tr>
        `;
            }).join('');
        } else {
            this.tableBody.innerHTML = '<tr><td colspan="8">No se encontraron registros.</td></tr>';
        }
    },

    // Nueva: Maneja la lógica de "rebanar" el arreglo y actualizar botones
    renderTableWithPagination() {
        const total = this.filteredUsers.length;
        const maxPage = Math.ceil(total / this.rowsPerPage) || 1;

        if (this.currentPage > maxPage) this.currentPage = maxPage;
        if (this.currentPage < 1) this.currentPage = 1;

        const start = (this.currentPage - 1) * this.rowsPerPage;
        const end = start + this.rowsPerPage;
        const pagedData = this.filteredUsers.slice(start, end);

        this.renderTable(pagedData);

        // Actualizar UI de paginación
        if (this.pageIndicator) {
            this.pageIndicator.innerText = `Página ${this.currentPage} de ${maxPage}`;
        }

        // Bloqueo de botones
        if (this.btnFirst) this.btnFirst.disabled = (this.currentPage === 1);
        if (this.btnPrev) this.btnPrev.disabled = (this.currentPage === 1);
        if (this.btnNext) this.btnNext.disabled = (this.currentPage === maxPage || total === 0);
        if (this.btnLast) this.btnLast.disabled = (this.currentPage === maxPage || total === 0);
    },

    async loadUsers() {
        this.renderSkeleton();
        try {
            const res = await fetch('/api/usuarios');
            const data = await res.json();
            this.allUsers = Array.isArray(data) ? data : [];
            this.applyFilters(); // Inicializa filteredUsers y llama a render
        } catch (e) {
            this.showToast("Error de conexión al cargar lista", 'error');
            this.tableBody.innerHTML = '<tr><td colspan="8">Error al cargar datos.</td></tr>';
        }
    },

    applyFilters() {
        const term = this.searchInput.value.toLowerCase().trim();
        const from = this.dateFrom.value;
        const to = this.dateTo.value;

        this.filteredUsers = this.allUsers.filter(u => {
            const fullName = `${u.nombre} ${u.ap} ${u.am || ''}`
                .toLowerCase()
                .normalize("NFD")
                .replace(/[\u0300-\u036f]/g, "");

            const matchesTerm = term === "" || fullName.includes(term);

            const userDate = u.fecha_nac;
            let matchesDate = true;
            if (from && userDate < from) matchesDate = false;
            if (to && userDate > to) matchesDate = false;

            return matchesTerm && matchesDate;
        });

        this.currentPage = 1; // Reiniciar a página 1 tras filtrar
        this.renderTableWithPagination();
    },

    resetFilters() {
        this.searchInput.value = "";
        this.dateFrom.value = "";
        this.dateTo.value = "";
        this.applyFilters(); // Reutiliza applyFilters para resetear filteredUsers y vista
    },

    setupValidations() {
        const nameInput = document.getElementById('name');
        const apPaterno = document.getElementById('ap_paterno');
        const apMaterno = document.getElementById('ap_materno');

        const soloLetras = function () {
            this.value = this.value.replace(/[^a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]/g, '');
        };

        const prevenirEspacioInicial = function (e) {
            if (e.key === ' ' && this.value.length === 0) {
                e.preventDefault();
            }
        };

        [nameInput, apPaterno, apMaterno].forEach(input => {
            if (input) {
                input.addEventListener('input', soloLetras);
                input.addEventListener('keydown', prevenirEspacioInicial);
            }
        });

        if (this.birthdateInput) {
            const todayLocal = new Date().toISOString().split('T')[0];
            this.birthdateInput.max = todayLocal;
        }

        this.birthdateInput.addEventListener('blur', () => {
            const selectedDate = new Date(this.birthdateInput.value);
            const today = new Date();
            today.setHours(0, 0, 0, 0);

            if (selectedDate > today) {
                document.getElementById('error_birthdate').innerText = "No se permiten fechas futuras";
                this.birthdateInput.value = "";
            }
        });
    },

    async openModal(id = null) {
        this.form.reset();
        this.clearErrors();

        // Limpiar vista previa al abrir
        if (this.previewContainer) this.previewContainer.classList.add("d-none");
        if (this.fileError) this.fileError.classList.add("d-none");

        const submitBtn = this.form.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.style.opacity = "1";
            submitBtn.innerText = id ? 'Guardar Cambios' : 'Registrar Usuario';
        }

        this.form.id.value = id || "";
        document.getElementById('modalTitle').innerText = id ? 'Editar Usuario' : 'Nuevo Usuario';

        if (id) {
            try {
                const res = await fetch(`/api/usuarios?id=${id}`);
                const u = await res.json();

                // Mapeo corregido según la respuesta de tu JSON
                this.form.Nombre.value = u.nombre || ""; // El name del input es "Nombre"
                this.form.ApellidoP.value = u.ap || "";  // El name del input es "ApellidoP"
                this.form.ApellidoM.value = u.am || "";  // El name del input es "ApellidoM"
                this.form.strCorreo.value = u.email || ""; // El name es "strCorreo"
                this.form.strNumeroCelular.value = u.celular || ""; // El name es "strNumeroCelular"
                this.form.FechaNacimiento.value = u.fecha_nac || ""; // El name es "FechaNacimiento"

                // Selects (Asegúrate de usar el ID correcto del elemento)
                document.getElementById('sexoSelect').value = u.id_sexo || "";
                document.getElementById('deptoSelect').value = u.id_perfil || "";
                document.getElementById('estadoSelect').value = u.id_estado || "";

                // Mostrar la imagen actual en la vista previa
                if (u.imagen_path) {
                    this.previewImg.src = "/" + u.imagen_path.replace(/\\/g, "/");
                    this.previewContainer.classList.remove("d-none");
                }

            } catch (e) {
                console.error("Error al poblar el modal:", e);
                this.showToast("Error al obtener datos", 'error');
            }
        }
        this.modal.style.display = 'flex';
    },

    async delete(id) {
        this.userToDeleteId = id;
        const deleteModal = document.getElementById('deleteModal');
        const confirmBtn = document.getElementById('confirmDeleteBtn');
        confirmBtn.disabled = false;
        confirmBtn.innerText = "Sí, eliminar";
        deleteModal.style.display = 'flex';
        confirmBtn.onclick = () => this.executeDelete();
    },

    async executeDelete() {
        const id = this.userToDeleteId;
        if (!id) return;
        const confirmBtn = document.getElementById('confirmDeleteBtn');
        if (confirmBtn.disabled) return;

        confirmBtn.disabled = true;
        confirmBtn.innerText = "Eliminando...";

        try {
            const res = await fetch('/api/usuarios', {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id: id })
            });
            const result = await res.json();

            if (result.success) {
                this.showToast(result.msg, 'warning');
                await this.loadUsers();
                this.closeDeleteModal();
            } else {
                this.showToast(result.msg, 'error');
                confirmBtn.disabled = false;
                confirmBtn.innerText = "Confirmar";
            }
        } catch (e) {
            this.showToast("Error al eliminar", 'error');
            confirmBtn.disabled = false;
            confirmBtn.innerText = "Confirmar";
        } finally {
            this.closeDeleteModal();
        }
    },

    closeDeleteModal() {
        const deleteModal = document.getElementById('deleteModal');
        deleteModal.style.display = 'none';
        this.userToDeleteId = null;
    },

    async handleSubmit(e) {
        e.preventDefault();
        this.clearErrors();

        const submitBtn = this.form.querySelector('button[type="submit"]');
        if (!submitBtn || submitBtn.disabled) return;

        const originalText = submitBtn.innerText;
        submitBtn.disabled = true;
        submitBtn.style.opacity = "0.7";
        submitBtn.innerText = "Guardando...";

        // 1. Capturamos todos los datos, incluyendo el archivo de imagen
        const formData = new FormData(this.form);

        // 2. Determinamos el ID para saber si es PUT o POST
        const id = formData.get('id');

        try {
            const res = await fetch('/api/usuarios', {
                method: id ? 'PUT' : 'POST',
                // IMPORTANTE: Al enviar archivos, NO debes definir 'Content-Type'. 
                // El navegador lo configurará automáticamente como multipart/form-data.
                body: formData
            });

            const result = await res.json();

            if (result.success) {
                this.showToast(result.msg, 'success');
                this.closeModal();
                // 3. Resetear el contenedor de vista previa de imagen
                if (this.previewContainer) this.previewContainer.classList.add("d-none");
                await this.loadUsers();
            } else {
                this.handleBackendErrors(result.errors);
                this.showToast(result.msg || "Error de validación", 'error');

                // Restaurar botón en caso de error de validación
                submitBtn.disabled = false;
                submitBtn.style.opacity = "1";
                submitBtn.innerText = originalText;
            }
        } catch (e) {
            console.error("Detalle técnico:", e);
            this.showToast("Error de conexión. Intente de nuevo.", 'error');

            // Restaurar botón en caso de error de red
            submitBtn.disabled = false;
            submitBtn.style.opacity = "1";
            submitBtn.innerText = originalText;
        }
    },

    handleBackendErrors(errors) {
        if (!errors) return;
        if (errors.email) document.getElementById('error_email').innerText = errors.email;
        if (errors.fecha_nac) document.getElementById('error_birthdate').innerText = errors.fecha_nac;
    },

    clearErrors() {
        document.querySelectorAll('.error-text').forEach(div => div.innerText = "");
    },

    closeModal() {
        this.modal.style.display = 'none';
    },

    showToast(msg, type = 'success') {
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container';
            document.body.appendChild(container);
        }

        const existingToasts = Array.from(container.querySelectorAll('.toast-message'));
        const isDuplicate = existingToasts.some(t => t.innerText === msg);
        if (isDuplicate) return;

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

document.addEventListener('DOMContentLoaded', () => UserManager.init());