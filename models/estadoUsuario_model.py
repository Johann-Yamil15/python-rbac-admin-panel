class EstadoUsuario:
    def __init__(self, id=None, strNombreEstado=None):
        self.id = id
        self.strNombreEstado = strNombreEstado

    @staticmethod
    def from_dict(data):
        if not data: return None
        return EstadoUsuario(
            id=data.get('id'),
            strNombreEstado=data.get('strNombreEstado')
        )

    def to_dict(self):
        return {
            "id": self.id,
            "strNombreEstado": self.strNombreEstado
        }