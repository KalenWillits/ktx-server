from models import Model


class SpecialPermission(Model):

    @property
    def type(self) -> str:
        return self.__type

    @type.setter
    def type(self, type_string: str):
        if type_string.upper() == "MODEL":
            self.__type = "MODEL"
        elif type_string.upper() == "ACTION":
            self.__type = "ACTION"

    name: str = ''
    fk: int = 0
