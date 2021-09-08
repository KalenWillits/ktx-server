from apps.assets.models import Icon
from typing import get_type_hints
import os
import pandas as pd
import re

def is_datetime(string):
    if not isinstance(string, str):
        return False

    if len(string) < 10:
        return False

    if string:
        try:
            pd.to_datetime(string)
            return True
        except ValueError:
            return False
    else:
        return False


def file_to_string(file_path, encoder='LATIN'):
    with open(file_path, 'rb') as file_bytes:
        file_string = file_bytes.read().decode(encoder)
        return file_string

def string_to_file(file_string, file_path, encoder='LATIN'):
    with open(file_path, 'wb') as output_file:
        file_bytes = file_string.encode(encoder)
        output_file.write(file_bytes)


def batch_import_icons(path, db):
    for file_name in os.listdir(path):
        image_string = file_to_string(os.path.join(path, file_name))
        icon = Icon(title=file_name, file=image_string, file_name=file_name)
        db.add(icon)

def parse_nums(string):
    nums_list = re.findall(r"[+-]? *(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?", string)
    nums_str = ''.join(nums_list)
    return nums_str

def is_numeric(data, ignore_letters=True):
    'Checks if there are numbers in an object.'
    if ignore_letters and isinstance(data, str):
        if parse_nums(data):
            return True
        return False
    else:
        try:
            pd.to_numeric(data)
            return True
        except ValueError:
            return False


class Schema:
    def __init__(self, model):
        self.model = model
        self._ = dict()
        self.exempt_methods = ('on_read', 'on_create', 'on_change', 'on_delete', 'df')

        for attribute in dir(self.model):
            if '__' in attribute:
                continue
            if attribute in self.exempt_methods:
                continue
            self._[attribute] = getattr(self.model, attribute)

    def __setitem__(self, key, value):
        self._[key] = value

    def __getitem__(self, key):
        return self._.get(key)

    def items(self):
        '''
        Returns the table schema from a model.
        [
        ...
        (NAME, TYPE, VALUE),
        ...
        ]
        '''
        dtypes = get_type_hints(self.model)
        for attribute in dir(self.model):
            if '__' in attribute:
                continue
            if attribute in ('on_read', 'on_create', 'on_change', 'on_delete', 'df'):
                continue
            yield attribute, dtypes.get(attribute), getattr(self.model, attribute)
