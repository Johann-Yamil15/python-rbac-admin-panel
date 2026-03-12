class PermisosPerfil:
    def __init__(self, id=None, idModulo=None, idPerfil=None, 
                 bitAgregar=False, bitEditar=False, bitEliminar=False, 
                 bitConsulta=False, bitDetalle=False):
        self.id = id
        self.idModulo = idModulo
        self.idPerfil = idPerfil
        self.bitAgregar = bitAgregar
        self.bitEditar = bitEditar
        self.bitEliminar = bitEliminar
        self.bitConsulta = bitConsulta
        self.bitDetalle = bitDetalle

    @staticmethod
    def from_dict(data):
        if not data: return None
        return PermisosPerfil(
            id=data.get('id'),
            idModulo=data.get('idModulo'),
            idPerfil=data.get('idPerfil'),
            bitAgregar=bool(data.get('bitAgregar', False)),
            bitEditar=bool(data.get('bitEditar', False)),
            bitEliminar=bool(data.get('bitEliminar', False)),
            bitConsulta=bool(data.get('bitConsulta', False)),
            bitDetalle=bool(data.get('bitDetalle', False))
        )

    def to_dict(self):
        return {
            "id": self.id,
            "idModulo": self.idModulo,
            "idPerfil": self.idPerfil,
            "permisos": {
                "agregar": self.bitAgregar,
                "editar": self.bitEditar,
                "eliminar": self.bitEliminar,
                "consulta": self.bitConsulta,
                "detalle": self.bitDetalle
            }
        }