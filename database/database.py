import pandas as pd
# import pickle
from typing import get_type_hints
import numpy as np
from config.settings import settings
import pytz
import os
from database.utils import is_datetime, is_numeric, file_to_string, string_to_file
from models.utils import to_snake
from models.register import models
from apps.assets.utils import Asset

pd.options.mode.chained_assignment = None  # default='warn'
server_name = 'db'

class Database:
    file = os.path.join('db.pkl')

    def __init__(self):
        '''
        Simple in-memory database built with pandas to store data in ram.
        This is a "Pandas Database".
        '''
        self.load()

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getitem__(self, key):
        return self.__dict__[key]

    def new_pk(self, table_name):
        if self.has(table_name, column='pk'):
            if not self[table_name].empty:
                return self.__dict__[table_name].pk.max()+1
            else:
                return 1
        else:
            return 1

        raise Exception(f'{table_name} does not exist or has no column "pk".')

    def has(self, table_name, column=None, value=None):
        if column and value:
            if hasattr(self, table_name):
                if hasattr(self[table_name], column):
                    df = self[table_name][column]
                    df_filtered = df[df.isin([value])]
                    return not df_filtered.empty
            return False

        elif column:
            if hasattr(self, table_name):
                if hasattr(self[table_name], column):
                    return True
            return False

        elif not value or not column:
            if hasattr(self, table_name):
                if hasattr(self[table_name], 'empty'):
                    return not self[table_name].empty
        else:
            if hasattr(self, table_name):
                return any([self[table_name][column] == value])

        return False

    def make(self, instance):
        '''
        Stores a dataframe in an attribute to the database as a pandas DataFrame.
        This is a "Pandas Table".
        '''

        df = instance.on_create(self)
        instance = instance.__class__(**df.iloc[0].to_dict())
        table_name = to_snake(instance.__class__.__name__)
        if not self.has(table_name):
            db[table_name] = df

    def add(self, instance, skip_on_create=False):
        '''Adds a model instance to the corresponding table.
        If there is no table, one is created.
        '''

        if skip_on_create:
            df = instance.df()
        else:
            df = instance.on_create(self)

        instance = instance.__class__(**df.iloc[0].to_dict())
        table_name = to_snake(instance.__class__.__name__)
        if self.has(table_name):
            self[table_name] = self[table_name].append(df, ignore_index=True)
        else:
            self[table_name] = df
        return df

    def filter(self, table_name, **kwargs):
        if self.has(table_name):
            df = self[table_name]
            keys = kwargs.keys()

            if '_sort' in keys:
                if kwargs.get('_sort'):
                    if kwargs['_sort'][0] == '-':
                        ascending = False
                        kwargs['_sort'] = kwargs['_sort'][1:]
                    else:
                        ascending = True
                    df = df.sort_values(kwargs['_sort'], ascending=ascending)
                    del kwargs['_sort']

            if '_limit' in keys:
                df = df.head(kwargs['_limit'])
                del kwargs['_limit']

            for key, value in kwargs.items():
                if isinstance(value, (list, set)):
                    continue

                if '__' in key:

                    column, operator = key.split('__')
                    if is_datetime(value):
                        value = pd.to_datetime(value)
                        if not value.tzinfo:
                            value = pytz.timezone(settings.server_timezone).localize(value)
                        df[column] = pd.to_datetime(df[column])

                    if operator == 'f':
                        df = df[df[column].str.contains(value, regex=False)]
                    elif operator == 're':
                        df = df[df[column].str.contains(value)]
                    elif operator == 'gt':
                        df = df[df[column] > value]
                    elif operator == 'lt':
                        df = df[df[column] < value]
                    elif operator == 'gte':
                        df = df[df[column] >= value]
                    elif operator == 'lte':
                        df = df[df[column] <= value]
                    elif operator == 'max':
                        df = df[df[column] == df[column].max()]
                    elif operator == 'min':
                        df = df[df[column] == df[column].min()]

                    if is_datetime(value):
                        df[column] = df[column].dt.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    df = df[df[key] == value]
            return df
        else:
            return pd.DataFrame()

    def get(self, model, pk):
        '''
        Finds a model instance by pk.
        '''
        table_name = to_snake(model.__name__)
        df = self.filter(table_name, pk=pk)
        if not df.empty:
            return model(**df.iloc[0].to_dict())
        else:
            return None

    def query(self, instance, **kwargs):
        instance.on_read(self)
        table_name = to_snake(instance.__class__.__name__)
        return self.filter(table_name, **kwargs)

    def change(self, instance, **kwargs):
        table_name = to_snake(instance.__class__.__name__)
        df = instance.on_change(self)
        instance = instance.__class__(**df.iloc[0].to_dict())
        operator = None

        indexes = self[table_name][self[table_name].pk == kwargs['pk']].index
        del kwargs['pk']
        for key, value in kwargs.items():
            if '__' in key:
                key, operator = key.split('__')

            default_value = instance.__class__.__dict__.get(key)
            if isinstance(value, np.ndarray):
                value = value.to_list()
            if (is_list := isinstance(default_value, list)) or (is_set := isinstance(default_value, set)):
                if operator == 'add':
                    for index in indexes:
                        current_values = self[table_name][key].iloc[index]
                        if is_list:
                            self[table_name].loc[index, [key]] = [[*current_values, *value]]
                        elif is_set:
                            self[table_name].loc[index, [key]] = [{*current_values, *value}]
                    continue

                elif operator == 'rm':
                    for index in indexes:
                        current_values = self[table_name][key].iloc[index]
                        for sub_value in value:
                            current_values.remove(sub_value)
                        self[table_name].loc[index, [key]] = [current_values]
                    continue

                for index in indexes:
                    self[table_name].loc[index, [key]] = [value]

            else:
                self[table_name].loc[indexes, [key]] = [value]

        try:
            return self[table_name].iloc[indexes]
        except KeyError:
            return self[table_name].iloc[0:0]

    def init_schema(self):
        for model in models:
            if name := to_snake((model.__name__)):
                if not self.has(name):
                    empty_df = model().df().iloc[0:0]
                    self[name] = empty_df

    def audit_iter_types(self):
        '''
        Changes lists and sets from strings back into lists and sets on load.
        '''
        for model in models:
            if name := to_snake((model.__name__)):
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
        for model in models:
            if name := to_snake((model.__name__)):
                if issubclass(model, Asset):
                    for file, file_name in zip(self[name]['file'].values, self[name]['file_name']):
                        string_to_file(file, os.path.join(settings.assets_path, file_name))

                if hasattr(self, name):
                    columns = list(self[name].columns)
                    if 'file' in columns:
                        columns.remove('file')
                    self[name].to_csv(os.path.join(settings.data_path, f'{name}.csv'), columns=columns, index=False)

    def load(self):
        self.init_schema()
        for model in models:
            if name := to_snake((model.__name__)):
                if os.path.isfile(os.path.join(settings.data_path, f'{name}.csv')):
                    self[name] = pd.read_csv(os.path.join(settings.data_path, f'{name}.csv'))

                if issubclass(model, Asset):
                    self[name]['file'] = self[name]['file_name'].apply(
                        lambda file_name: file_to_string(os.path.join(settings.assets_path, file_name)))
        self.audit_iter_types()


db = Database()

def write_database_to_disk():
    db.save()
