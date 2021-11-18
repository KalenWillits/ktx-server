from uuid import uuid4
import pandas as pd
from ..utils import to_snake, Schema, hydrate
from ..datatypes import primary_key


class Model:
    @property
    def pk(self) -> primary_key:
        if not hasattr(self, '_pk'):
            self._pk = uuid4()

        return self._pk

    @pk.setter
    def pk(self, value):
        self._pk = primary_key(value)

    def __init__(self, **kwargs):
        self._schema = Schema(self)
        self._name = self.__class__.__name__
        self.__dict__.update(self._schema.values)

        # setattr calls properties as well.
        for key, value in kwargs.items():
            setattr(self, key, value)

    @property
    def _snake_name(self) -> str:
        return to_snake(self._name)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)

    def _hydrate(self, db, df: pd.DataFrame = None):
        if not df:
            df = self._to_df()
        return hydrate(self.__class__, df, db)

    def _to_dict(self, encode: bool = True) -> dict:
        instance_values = {}
        for field, datatype in self._schema.datatypes.values():
            if encode:
                instance_values[field] = datatype.encode(self[field])
            else:
                instance_values[field] = datatype(self[field])

        return instance_values

    def _to_df(self) -> pd.DataFrame:
        df = pd.DataFrame([self._to_dict()])
        return df

    def __repr__(self):
        return self._to_df().to_string()


class ModelManager:
    def __init__(self, *models):
        self.__models__ = models
        for model in models:
            setattr(self, model.__name__, model)

    def __iter__(self):
        for model in self.__models__:
            yield model

    def __getitem__(self, key_or_index):
        if isinstance(key_or_index, int):
            return self.__models__[key_or_index]
        else:
            return getattr(self, key_or_index)
