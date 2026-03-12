class Menu:
    def __init__(self, id=None, strNombreMenu=None):
        self.id = id
        self.strNombreMenu = strNombreMenu

    @staticmethod
    def from_dict(data):
        if not data: return None
        return Menu(
            id=data.get('id'),
            strNombreMenu=data.get('strNombreMenu')
        )

    def to_dict(self):
        return {
            "id": self.id,
            "strNombreMenu": self.strNombreMenu
        }