from typing import get_type_hints
import inspect
import re
from config.settings import settings
import hashlib


def to_snake(name_string):
    '''
    Converts a string in title case to snake case.
    '''
    word_list = re.findall('[A-Z][^A-Z]*', name_string)
    snake_case = '_'.join((f'{w.lower()}' for w in word_list))
    return snake_case


def hydrate(model, df, db):
    'Takes the Pandas DataFrame values and generates model instances.'
    for i in range(df.shape[0]):
        result = df.iloc[i].to_dict()

        for field, dtype, default_value in model().schema.items():
            if '__' in field:
                continue
            if dtype is set:
                result[field] = list()

            if inspect.isclass(default_value):
                if db.has(to_snake(default_value.__name__)):
                    foreign_key_df = db.__dict__[to_snake(default_value.__name__)]
                    if key := result.get(field):
                        foreign_keys = [key]
                    else:
                        foreign_keys = list()
                    foreign_key_df_filtered = foreign_key_df[foreign_key_df.pk.isin(foreign_keys)]
                    if not foreign_key_df_filtered.empty:
                        result[field] = next(hydrate(default_value, foreign_key_df_filtered, db))

            elif isinstance(default_value, (list, set)):
                default_value = next(iter(default_value))
                if db.has(to_snake(default_value.__name__)):
                    foreign_key_df = db[to_snake(default_value.__name__)]
                    foreign_keys = result.get(field, list())
                    foreign_key_df_filtered = foreign_key_df[foreign_key_df.pk.isin(foreign_keys)]
                    if not foreign_key_df_filtered.empty:
                        result[field] = hydrate(default_value, foreign_key_df_filtered, db)
                    else:
                        result[field] = list()

            elif isinstance(default_value, bool):
                if result[field]:
                    result[field] = True
                else:
                    result[field] = False

        yield result


def encrypt(string):
    derived_key = hashlib.pbkdf2_hmac('sha256', bytes(string, 'UTF-8'), settings.hash_salt, 100_000)
    return derived_key.hex()

class Schema:
    def __init__(self, instance):
        self.instance = instance
        self.values = dict()
        self._exempt_methods = ('schema', 'on_read', 'on_create', 'on_change', 'on_delete', 'df', 'snake_name')

        for attribute in dir(self.instance):
            if '__' in attribute:
                continue
            if attribute in self._exempt_methods:
                continue

            if inspect.isclass(getattr(self.instance.__class__, attribute)):
                self.values[attribute] = 0
            elif isinstance(getattr(self.instance.__class__, attribute), set):
                self.values[attribute] = set()
            elif isinstance(getattr(self.instance.__class__, attribute), list):
                self.values[attribute] = list()
            else:
                self.values[attribute] = getattr(self.instance.__class__, attribute)

    def __setitem__(self, key, value):
        self._[key] = value

    def __getitem__(self, key):
        return self.dtypes()[key]

    def __repr__(self):
        return f'{self.instance.__class__.__name__}.schema({self.dtypes()})'

    def __str__(self):
        return str(self.dtypes())

    def dtypes(self):
        dtypes_dict = get_type_hints(self.instance.__class__)
        for attribute_name in dir(self.instance):
            if '__' in attribute_name:
                continue
            if attribute_name in self._exempt_methods:
                continue

            attribute_value = getattr(self.instance.__class__, attribute_name)
            if hasattr(attribute_value, 'fget'):
                attribute_dtype = get_type_hints(attribute_value.fget)
                try:
                    dtypes_dict.update({attribute_name: attribute_dtype['return']})
                except KeyError:
                    raise Exception(
                        f'Type hint requirement not met on {self.instance.__class__.__name__}.{attribute_name}')

        return dtypes_dict

    def items(self):
        '''
        Returns the table schema from a model.
        [
        ...
        (NAME, TYPE, VALUE),
        ...
        ]
        '''
        dtypes = self.dtypes()
        for attribute in dir(self.instance):
            if '__' in attribute:
                continue
            if attribute in self._exempt_methods:
                continue
            yield attribute, dtypes.get(attribute), getattr(self.instance.__class__, attribute)
