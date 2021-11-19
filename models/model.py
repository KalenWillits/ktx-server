from uuid import uuid4
from inspect import isclass
from typing import get_type_hints
import pandas as pd
from ..utils import to_snake, hydrate
from ..datatypes import PrimaryKey


class Schema:
    def __init__(self, instance):
        self.instance = instance
        self.datatypes = {}
        self.values = {}

        # Create the datatypes dict off of the base model.
        for field, datatype in self.build_datatypes_dict().items():
            if field[0] == '_':
                continue

            self.datatypes[field] = datatype

        # Create the default values dict off of the base model.
        for field, default_value in self.instance.__class__.__dict__.items():
            if '__' in field:
                continue

            if field[0] == '_':
                continue

            if isclass(default_value):
                default_value = None

            self.values[field] = default_value

    def __getitem__(self, key):
        return self.datatypes[key]

    def __repr__(self):
        return f'{self.instance.__class__.__name__}._schema({set(self.items())})'

    def build_datatypes_dict(self) -> dict:
        '''
        This is a required process to merge variables and properties on models and subject them to the
        same behavior.
        Creates a dictionary of field datatypes:
            :{[FIELD_NAME]: [DTYPE]}:
        '''
        datatypes_dict = get_type_hints(self.instance.__class__)
        for field_name in dir(self.instance):
            if '__' in field_name:
                continue
            if field_name[0] == '_':
                continue

            # Gathering and formatting datatypes for properties
            if hasattr(self.instance.__class__, field_name):
                field_value = getattr(self.instance.__class__, field_name)
                if hasattr(field_value, 'fget'):
                    field_datatype = get_type_hints(field_value.fget)
                    try:
                        datatypes_dict.update({field_name: field_datatype['return']})
                    except KeyError:
                        raise Exception(
                            f'DataType hint requirement not met on {self.instance.__class__.__name__}.{field_name}')

        return datatypes_dict

    def fields(self):
        for field in self.datatypes.keys():
            yield field

    def default_values(self):
        for value in self.values.values():
            yield value

    def types(self):
        for datatype in self.datatypes.values():
            yield datatype

    def items(self):
        for field, datatype, default_value in zip(self.fields(), self.types(), self.default_values()):
            yield field, datatype, default_value

class Model:
    @property
    def pk(self) -> PrimaryKey():
        if not hasattr(self, '_pk'):
            self._pk = uuid4()

        return self._pk

    @pk.setter
    def pk(self, value):
        datatype = PrimaryKey()
        self._pk = datatype(value)

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
        for field, datatype in self._schema.datatypes.items():
            instance_values[field] = datatype(self[field], encode=encode)

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
