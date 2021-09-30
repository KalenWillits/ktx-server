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

    def _as_response(self, db, values: list = None):
        df = self._to_df()
        if values:
            df = df[values]
        return hydrate(self.__class__, df, db)

    def _to_dict(self) -> dict:
        fields_dict = dict()
        for field, dtype, default_value in self._schema.items():

            if inspect.isclass(default_value):
                default_value = ""
            elif dtype == list:
                default_value = list()
            elif dtype == set:
                default_value = set()

            fields_dict[field] = default_value

        instance_values = self.__dict__
        for field, value in instance_values.items():
            if field[0] == "_":
                continue
            fields_dict[field] = value

        return fields_dict

    def _to_df(self) -> pd.DataFrame:
        df = pd.DataFrame([self._to_dict()])
        return df

    def _on_read(self, db):
        pass

    def _on_create(self, db):
        pass

    def _on_change(self, db):
        pass

    def _on_delete(self, db):
        pass

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
