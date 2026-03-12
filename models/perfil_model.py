class Perfil:
    def __init__(self, id=None, strNombrePerfil=None, bitAdministrador=False):
        self.id = id
        self.strNombrePerfil = strNombrePerfil
        self.bitAdministrador = bitAdministrador

    @staticmethod
    def from_dict(data):
        if not data: return None
        return Perfil(
            id=data.get('id'),
            strNombrePerfil=data.get('strNombrePerfil'),
            bitAdministrador=bool(data.get('bitAdministrador', False))
        )

    def to_dict(self):
        return {
            "id": self.id,
            "strNombrePerfil": self.strNombrePerfil,
            "bitAdministrador": self.bitAdministrador
        }