import inspect
import pandas as pd
from utils import to_snake, Schema


class Model:
    pk: int = 0

    def __init__(self, *args, **kwargs):
        self.schema = Schema(self)
        self.__dict__.update(self.schema.values)
        for key, value in kwargs.items():
            setattr(self, key, value)

    @property
    def snake_name(self) -> str:
        return to_snake(self.__class__.__name__)

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getitem__(self, key):
        return self.__dict__[key]

    def df(self):
        fields_dict = dict()
        for field, dtype, default_value in self.schema.items():
            if inspect.isclass(default_value):
                default_value = 0
            elif dtype == list:
                default_value = list()
            elif dtype == set:
                default_value = set()

            fields_dict[field] = default_value
        instance_values = self.__dict__
        del instance_values['schema']
        fields_dict.update(instance_values)

        df = pd.DataFrame([fields_dict])

        return df

    def on_read(self, db):
        return self.df()

    def on_create(self, db):
        table_name = to_snake(self.__class__.__name__)
        self.pk = db.new_pk(table_name)
        return self.df()

    def on_change(self, db):
        return self.df()

    def on_delete(self, db):
        return self.df()

    def __repr__(self):
        return self.df().to_string()

class ModelManager:
    def __init__(self, models: list):
        self.__models__ = models
        for model in models:
            self.__dict__[model.__class__.__name__] = model

    def __iter__(self):
        for model in self.__models__:
            yield model

    def __getitem__(self, index: int):
        return self.__models__[index]
