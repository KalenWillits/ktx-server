from uuid import UUID
from ..datatypes import DataType


class KeyType(DataType):
    def execute(self, value, **kwargs):
        return self.encode(value, **kwargs)

    def encode(self, value, **kwargs):
        return str(value)

    def decode(self, value, **kwargs):
        return UUID(value)


key_type = KeyType()
