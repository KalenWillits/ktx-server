import pandas as pd
from typing import get_type_hints
import pytz
import os

from .utils import (
    is_datetime,
    handle_sort,
    handle_limit,
    column_filters,
    parse_list,
    parse_set,
)

from .models import ModelManager, Model

pd.options.mode.chained_assignment = None


class Database:

    def __init__(self, models: ModelManager = ModelManager(), path: str = ''):
        '''
        Simple in-memory database built with pandas to store data in ram.
        This is a "Pandas Database".
        '''
        self.models = models
        self.path = path
        self.load()

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getitem__(self, key):
        return self.__dict__[key]

    def __repr__(self):
        # TODO: Refactor to create a schema diagram including types
        output = "<object 'Database'>"
        for model in self.models:
            shape = self[model.__name__].shape
            output += f"\n{model.__name__}(columns: {shape[1]}, rows: {shape[0]})"
        return output

    def has(self, model_name: str) -> bool:
        if hasattr(self, model_name):
            if isinstance(self[model_name], pd.DataFrame):
                return True

        return False

    def create(self, model_name, **kwargs) -> Model:
        instance = self.models[model_name](**kwargs)
        df = instance._to_df()

        if self.has(model_name):
            self[model_name] = self[model_name].append(df, ignore_index=True)
        else:
            self[model_name] = df
        return instance

    def query(self, model_name: str, **kwargs) -> pd.DataFrame:
        if self.has(model_name):
            df = self[model_name]

            kwargs, df = handle_sort(kwargs, df)
            kwargs, df = handle_limit(kwargs, df)

            for key, value in kwargs.items():
                if isinstance(value, (list, set)):
                    continue

                if '__' in key:

                    column, operator = key.split('__')
                    if is_datetime(value):
                        value = pd.to_datetime(value)
                        if not value.tzinfo:
                            value = pytz.timezone('UTC').localize(value)
                        df[column] = pd.to_datetime(df[column])

                    df = column_filters[operator](df, column, value)

                    if is_datetime(value):
                        df[column] = df[column].dt.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    df = df[df[key] == value]
            return df
        else:
            return pd.DataFrame()

    def get(self, model_name, pk: str):
        df = self.query(model_name, pk=pk)
        if not df.empty:
            return self.models[model_name](**df.iloc[0].to_dict())

        return None

    def update(self, model_name: str, query: pd.DataFrame, **kwargs):
        for column, value in kwargs.items():
            self[model_name][column].iloc[query.index] = [value]

        return self[model_name].iloc[query.index]

    def drop(self, model_name: str, **kwargs) -> None:
        indexes = self.query(model_name, **kwargs).index
        self[model_name].drop(index=indexes, inplace=True)

    def init_schema(self):
        for model in self.models:
            if name := model.__name__:
                if not self.has(name):
                    empty_df = model()._to_df().iloc[0:0]
                    self[name] = empty_df

    def audit_iter_types(self):
        '''
        Changes lists and sets from strings back into lists and sets on load.
        '''
        for model in self.models:
            if name := model.__name__:
                if self.has(name):
                    dtypes = get_type_hints(model)
                    for field in self[name].columns:
                        if dtype := dtypes.get(field):
                            if hasattr(dtype, '__origin__'):
                                if dtype.__origin__ is set:
                                    inner_dtype = dtype.__args__[0]
                                    for index, set_string in enumerate(self[name][field].values):
                                        self[name][field][index] = parse_set(set_string)

                                        if inner_dtype is int or inner_dtype is float:
                                            self[name][field].iloc[index].apply(
                                                lambda parsed_set: {inner_dtype(value) for value in parsed_set})

                                elif dtype.__origin__ is list:
                                    inner_dtype = dtype.__args__[0]
                                    for index, list_string in enumerate(self[name][field].values):
                                        self[name][field][index] = parse_list(list_string)

                                        if inner_dtype is int or inner_dtype is float:
                                            self[name][field].iloc[index].apply(
                                                lambda parsed_list: [inner_dtype(value) for value in parsed_list])

                            else:
                                self[name][field].astype(dtype)

    def save(self):
        for model in self.models:
            if name := model.__name__:
                if hasattr(self, name):
                    columns = list(self[name].columns)
                    self[name].to_csv(os.path.join(self.path, f'{name}.csv'), columns=columns, index=False)

    def load(self):
        self.init_schema()
        for model in self.models:
            if name := model.__name__:
                if os.path.isfile(os.path.join(self.path, f'{name}.csv')):
                    self[name] = pd.read_csv(os.path.join(self.path, f'{name}.csv'))

        self.audit_iter_types()
