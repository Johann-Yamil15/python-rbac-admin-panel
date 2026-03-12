class User:
    def __init__(self, id=None, nombre=None, ap=None, am=None, email=None,
                 fecha_nac=None, password=None, id_perfil=None,
                 id_estado=None, id_sexo=None, celular=None,
                 imagen_path=None, fecha_registro=None):
        self.id = id
        self.nombre = nombre
        self.ap = ap
        self.am = am
        self.email = email
        self.fecha_nac = fecha_nac
        self.password = password
        self.id_perfil = id_perfil
        self.id_estado = id_estado
        self.id_sexo = id_sexo
        self.celular = celular
        self.imagen_path = imagen_path
        self.fecha_registro = fecha_registro

    @staticmethod
    def from_dict(data):
        if not data:
            return None

        # Mapeo flexible que acepta nombres de la DB (SQL Server) o de diccionarios de Python
        return User(
            id=data.get('id'),
            nombre=data.get('Nombre'),
            ap=data.get('ApellidoP'),
            am=data.get('ApellidoM'),
            email=data.get('strCorreo'),
            fecha_nac=data.get('FechaNacimiento'),
            password=data.get('strPwd'),
            id_perfil=data.get('idPerfil'),
            id_estado=data.get('idEstadoUsuario'),
            id_sexo=data.get('idSexo'),
            celular=data.get('strNumeroCelular'),
            imagen_path=data.get('strImagenPath'),
            fecha_registro=data.get('FechaRegistro')
        )

    def to_dict(self, include_password=False):
        # Este diccionario es el que se enviará al Frontend como JSON
        user_dict = {
            "id": self.id,
            "nombre": self.nombre,
            "ap": self.ap,
            "am": self.am,
            "nombre_completo": f"{self.nombre} {self.ap} {self.am}".strip(),
            "email": self.email,
            "fecha_nac": str(self.fecha_nac) if self.fecha_nac else None,
            "id_perfil": self.id_perfil,
            "id_estado": self.id_estado,
            "id_sexo": self.id_sexo,
            "celular": self.celular,
            "imagen_path": self.imagen_path,
            "fecha_registro": str(self.fecha_registro) if self.fecha_registro else None
        }
        if include_password:
            user_dict["password"] = self.password
        return user_dict
