document.addEventListener("DOMContentLoaded", () => {
    // TELÉFONO: solo números, máximo 10
    const phoneInput = document.getElementById('phone');
    if (phoneInput) {
        phoneInput.addEventListener('input', function(e) {
            this.value = this.value.replace(/\D/g, '').slice(0, 10);
        });
    }

    // NOMBRE COMPLETO: solo letras y espacios (incluyendo acentos y ñ)
    const nameInput = document.getElementById('name');
    if (nameInput) {
        nameInput.addEventListener('input', function(e) {
            this.value = this.value.replace(/[^a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]/g, '');
        });
    }

    // NOMBRE DE USUARIO: solo letras y números, sin espacios ni símbolos
    const usernameInput = document.getElementById('username');
    if (usernameInput) {
        usernameInput.addEventListener('input', function(e) {
            this.value = this.value.replace(/[^a-zA-Z0-9]/g, '');
        });
    }

    // Prevenir espacios al inicio en nombre y usuario
    [nameInput, usernameInput].forEach(input => {
        if (input) {
            input.addEventListener('keydown', function(e) {
                if (e.key === ' ' && this.value.length === 0) {
                    e.preventDefault();
                }
            });
        }
    });
});