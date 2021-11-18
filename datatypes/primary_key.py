from uuid import UUID

from .datatypes import DataType


class PrimaryKey(DataType):
    def decode(self, value: str) -> UUID:
        return UUID(value)

    def encode(self, value: UUID) -> str:
        return str(value)

primary_key = PrimaryKey()
