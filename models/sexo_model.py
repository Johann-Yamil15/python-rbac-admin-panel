class Sexo:
    def __init__(self, id=None, strSexo=None):
        self.id = id
        self.strSexo = strSexo

    @staticmethod
    def from_dict(data):
        if not data: return None
        return Sexo(
            id=data.get('id'),
            strSexo=data.get('strSexo')
        )

    def to_dict(self):
        return {
            "id": self.id,
            "strSexo": self.strSexo
        }