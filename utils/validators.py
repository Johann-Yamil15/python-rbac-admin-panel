import re
from datetime import datetime

def validate_form(data):
    errors = {}

    # --- NOMBRE --- (Coincide con name="Nombre")
    nombre = data.get("Nombre", "").strip()
    if not nombre:
        errors["Nombre"] = "El nombre no puede estar vacío"
    elif not re.fullmatch(r"[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+", nombre):
        errors["Nombre"] = "Usa solo letras y espacios"

    # --- APELLIDO PATERNO --- (Coincide con name="ApellidoP")
    ap = data.get("ApellidoP", "").strip()
    if not ap:
        errors["ApellidoP"] = "El apellido paterno es obligatorio"
    elif not re.fullmatch(r"[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+", ap):
        errors["ApellidoP"] = "Usa solo letras y espacios"

    # --- CORREO --- (Coincide con name="strCorreo")
    email = data.get("strCorreo", "").strip()
    email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]{2,})+$"
    if not email:
        errors["strCorreo"] = "El correo es obligatorio"
    elif not re.fullmatch(email_regex, email):
        errors["strCorreo"] = "Formato inválido (ejemplo: usuario@uttt.edu.mx)"

    # --- NÚMERO CELULAR --- (Nueva validación para name="strNumeroCelular")
    celular = data.get("strNumeroCelular", "").strip()
    if celular: # Si lo llenan, validamos 10 dígitos
        if not re.fullmatch(r"\d{10}", celular):
            errors["strNumeroCelular"] = "El número debe tener 10 dígitos numéricos"

    # --- FECHA DE NACIMIENTO --- (Coincide con name="FechaNacimiento")
    fecha_nac_str = data.get("FechaNacimiento", "")
    if not fecha_nac_str:
        errors["FechaNacimiento"] = "La fecha es obligatoria"
    else:
        try:
            birth_date = datetime.strptime(fecha_nac_str, "%Y-%m-%d").date()
            if birth_date > datetime.now().date():
                errors["FechaNacimiento"] = "La fecha no puede ser futura"
        except ValueError:
            errors["FechaNacimiento"] = "Formato de fecha inválido"

    return errors