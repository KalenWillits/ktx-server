import pandas as pd
from typing import get_type_hints
import pytz
import os
from .utils import (
    is_datetime,
    is_numeric,
    file_to_string,
    string_to_file,
    handle_sort,
    handle_limit,
    column_filters,
)
from .models import ModelManager

pd.options.mode.chained_assignment = None


class Database:

    def __init__(self, models: ModelManager = ModelManager([]), path: str = '', asset_models: tuple = ()):
        '''
        Simple in-memory database built with pandas to store data in ram.
        This is a "Pandas Database".

       Asset models is a tuple of models that have a "file" attribute. The file attribute should be a byte string
       of a file asset. Such as a photo or audio file.
        '''
        self.models = models
        self.path = path
        self.asset_models = asset_models
        self.load()

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getitem__(self, key):
        return self.__dict__[key]

    def __repr__(self):
        output = ""
        for model in self.models:
            output += f"\n{model.__name__}/{str(self[model.__name__].shape())}"
        return output

    def has(self, model_name: str):
        if hasattr(self, model_name):
            if isinstance(self[model_name], pd.DataFrame):
                return True

        return False

    def create(self, model_name, **kwargs):
        '''Adds a model instance to the corresponding table.
        If there is no table, one is created.
        '''
        instance = self.models[model_name](**kwargs)
        df = instance._to_df()

        if self.has(model_name):
            self[model_name] = self[model_name].append(df, ignore_index=True)
        else:
            self[model_name] = df
        return df

    def query(self, model_name, **kwargs):
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

                    df = column_filters["operator"](df, column, value)

                    if is_datetime(value):
                        df[column] = df[column].dt.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    df = df[df[key] == value]
            return df
        else:
            return pd.DataFrame()

    def get(self, model_name, pk=None, **kwargs):
        '''
        Finds a dataframe of a model instance by pk.

        If a table_name is not provided, a loop itereates through all tables checking if the given pk is present.
        Which is a much slower process. It is recommended to always provide a table name for any process executing
        at run time.

        If a model is provided, an instance of the model will be returned instead of a dataframe.
        '''

        df = self.filter(model_name, pk=pk)
        if not df.empty:
            return self.models[model_name](**df.iloc[0].to_dict())

        return None

    def update(self, model_name, **kwargs):
        indexes = self.query(model_name, **kwargs).index

        for column, value in kwargs.items():
            for index in indexes:
                self[model_name][column][index] = [value]

        try:
            return self[model_name].iloc[indexes]
        except KeyError:
            return self[model_name].iloc[0:0]

    def drop(self, model_name, **kwargs):
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
                            if dtype == set:
                                for index, set_value in enumerate(self[name][field].values):
                                    self[name][field].iloc[index] = set(
                                        (is_numeric(
                                            num
                                        ) and int(num) for num in set_value.replace(
                                            '{', '').replace('}', '').split(',')))

                            elif dtype == list:
                                for index, set_value in enumerate(self[name][field].values):
                                    self[name][field].iloc[index] = list(
                                        (is_numeric(
                                            num
                                        ) and int(num) for num in set_value.replace(
                                            '[', '').replace(']', '').split(',')))
                            else:
                                self[name][field].astype(dtype)

    def save(self):
        for model in self.models:
            if name := model.__name__:
                if issubclass(model, self.asset_models):
                    for file, file_name in zip(self[name]['file'].values, self[name]['file_name']):
                        string_to_file(file, os.path.join(self.path, file_name))

                if hasattr(self, name):
                    columns = list(self[name].columns)
                    if 'file' in columns:
                        columns.remove('file')
                    self[name].to_csv(os.path.join(self.path, f'{name}.csv'), columns=columns, index=False)

    def load(self):
        self.init_schema()
        for model in self.models:
            if name := model.__name__:
                if os.path.isfile(os.path.join(self.path, f'{name}.csv')):
                    self[name] = pd.read_csv(os.path.join(self.path, f'{name}.csv'))

                if issubclass(model, self.asset_models):
                    self[name]['file'] = self[name]['file_name'].apply(
                        lambda file_name: file_to_string(os.path.join(self.path, file_name)))
        self.audit_iter_types()
