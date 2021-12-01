from uuid import uuid4
import inspect
import pandas as pd
import os

from .utils import (
    is_datetime,
    handle_sort,
    handle_limit,
    column_filters,
    hydrate,
    parse_datatype,
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
        terminal_width = os.get_terminal_size().columns
        header = 'DATABASE'
        header_margin = int((terminal_width / 2) - (len(header) / 2)) * '_'
        output = header_margin + header + header_margin

        for model in self.models:
            shape = self[model.__name__].shape
            info = f"{model.__name__}(COLUMNS: {shape[1]}, ROWS: {shape[0]})"
            info_margin = int((terminal_width / 2) - (len(info) / 2)) * '-'

            output += '\n' + info_margin + info + info_margin

            schema = [{'FIELD': field, 'DATATYPE': datatype, 'DEFAULT': default_value}
                      for field, datatype, default_value in model()._schema.items()]
            schema_df = pd.DataFrame(schema)
            output += schema_df.to_string()

        output += '\n' + '_' * terminal_width
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
            keys = list(kwargs.keys())
            for key in keys:
                if key not in df.columns:
                    del kwargs[key]

            kwargs, df = handle_sort(kwargs, df)
            kwargs, df = handle_limit(kwargs, df)

            for key, value in kwargs.items():
                if isinstance(value, (list, set)):
                    continue

                if '__' in key:

                    column, operator = key.split('__', 1)
                    if is_datetime(value):
                        value = pd.to_datetime(value, utc=True)
                        df[column] = pd.to_datetime(df[column])

                    # FK lookup.
                    if inspect.isclass(fk_model := getattr(self.models[model_name], column)):
                        fk_df = self.query(fk_model.__name__, **{operator: value}).pk
                        temp_column_suffix = f'_{uuid4()}'
                        df = pd.merge(left=df, right=fk_df, how='right', left_on=column, right_on='pk',
                                      suffixes=(None, temp_column_suffix))
                        df.drop(f'pk{temp_column_suffix}', inplace=True, axis=1)

                    # Special filters
                    else:
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

    def hydrate(self, model_name: str, **kwargs):
        return hydrate(self, model_name, self.query(model_name, **kwargs))

    def init_schema(self):
        for model in self.models:
            if name := model.__name__:
                if not self.has(name):
                    empty_df = model()._to_df().iloc[0:0]
                    self[name] = empty_df

    def audit_data_types(self):
        for model in self.models:
            if name := model.__name__:
                if self.has(name):
                    datatypes = model()._schema.datatypes()
                    for field in self[name].columns:
                        if datatype := datatypes.get(field):
                            self[name][field] = self[name][field].apply(
                                lambda value: parse_datatype(self, datatype, value))

    def save(self):
        self.audit_data_types()
        for model in self.models:
            if name := model.__name__:
                if hasattr(self, name):
                    self[name].to_json(os.path.join(self.path, f'{name}.json'), orient='records')

    def load(self):
        self.init_schema()
        for model in self.models:
            if name := model.__name__:
                if os.path.isfile(os.path.join(self.path, f'{name}.json')):
                    self[name] = pd.read_json(os.path.join(self.path, f'{name}.json'))

                    # Handle migrations
                    instance = model()
                    default_values = instance._schema.default_values()
                    loaded_fields = set(self[name].columns)
                    model_fields = set([field for field in instance._schema.fields()])
                    new_fields = model_fields.difference(loaded_fields)
                    removed_fields = loaded_fields.difference(model_fields)

                    for field in new_fields:
                        if isinstance((default_value := default_values[field]), (list, dict)):
                            for index in self[name].index:
                                self[name][field].iloc[index] = default_value
                        else:
                            self[name][field] = default_value

                    for field in removed_fields:
                        self[name].drop(field, inplace=True, axis=1)

        # self.audit_data_types()
