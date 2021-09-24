import inspect
from typing import get_type_hints

class Schema:
    def __init__(self, instance):
        self.instance = instance
        self.values = dict()

        for attribute in dir(self.instance):
            if '__' in attribute:
                continue
            if attribute[0] == '_':
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
        return f'{self.instance.__class__.__name__}._schema({self.dtypes()})'

    def __str__(self):
        return str(self.dtypes())

    def dtypes(self):
        dtypes_dict = get_type_hints(self.instance.__class__)
        for attribute_name in dir(self.instance):
            if '__' in attribute_name:
                continue
            if attribute_name[0] == '_':
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
            if attribute[0] == '_':
                continue
            yield attribute, dtypes.get(attribute), getattr(self.instance.__class__, attribute)