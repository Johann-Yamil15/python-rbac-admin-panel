class Modulo:
    def __init__(self, id=None, strNombreModulo=None, idMenu=None, strRuta=None):
        self.id = id
        self.strNombreModulo = strNombreModulo
        self.idMenu = idMenu
        self.strRuta = strRuta

    @staticmethod
    def from_dict(data):
        if not data: return None
        return Modulo(
            id=data.get('id'),
            strNombreModulo=data.get('strNombreModulo'),
            idMenu=data.get('idMenu'),
            strRuta=data.get('strRuta')
        )

    def to_dict(self):
        return {
            "id": self.id,
            "strNombreModulo": self.strNombreModulo,
            "idMenu": self.idMenu,
            "strRuta": self.strRuta
        }