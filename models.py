from uuid import uuid4
import inspect
import pandas as pd
from .utils import to_snake, Schema, hydrate


class Model:

    @property
    def pk(self) -> str:
        if not hasattr(self, "_pk"):
            self._pk = str(uuid4())

        return self._pk

    @pk.setter
    def pk(self, value):
        self._pk = str(value)

    def __init__(self, *args, **kwargs):
        self._schema = Schema(self)
        self.__dict__.update(self._schema.values)
        for key, value in kwargs.items():
            setattr(self, key, value)

    @property
    def _snake_name(self) -> str:
        return to_snake(self.__class__.__name__)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)

    def _hydrate(self, db, df: pd.DataFrame = None):
        if not df:
            df = self._to_df()
        return hydrate(self.__class__, df, db)

    def _to_dict(self) -> dict:
        instance_values = dict()
        for field, dtype, default_value in self._schema.items():
            instance_values[field] = self[field]

        return instance_values

    def _to_df(self) -> pd.DataFrame:
        df = pd.DataFrame([self._to_dict()])
        return df

    def __repr__(self):
        return self._to_df().to_string()

class ModelManager:
    def __init__(self, models: list):
        self.__models__ = models
        for model in models:
            self.__dict__[model.__name__] = model

    def __iter__(self):
        for model in self.__models__:
            yield model

    def __getitem__(self, index: int):
        return self.__models__[index]
