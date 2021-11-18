from inspect import isclass
from typing import get_type_hints


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
        return self.datatypes.keys()

    def default_values(self):
        return self.values.values()

    def datatypes(self):
        return self.datatypes.values()

    def items(self):
        for field, datatype, default_value in zip(self.fields(), self.datatypes(), self.default_values()):
            yield field, datatype, default_value
