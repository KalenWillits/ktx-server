from typing import get_type_hints

from .resolve_default_value import resolve_default_value


class Schema:
    def __init__(self, instance):
        self.instance = instance

    def datatypes(self):
        datatypes_dict = get_type_hints(self.instance.__class__)
        datatypes_dict.update(self.instance.__annotations__)
        for field_name in dir(self.instance):
            if '__' in field_name:
                continue
            if field_name[0] == '_':
                continue

            # Gathering and formatting datatypes for properties
            if hasattr(self.instance.__class__, field_name):
                field_value = getattr(self.instance.__class__, field_name)
                if hasattr(field_value, 'fget'):
                    field_dtype = get_type_hints(field_value.fget)
                    try:
                        datatypes_dict.update({field_name: field_dtype['return']})
                    except KeyError:
                        raise Exception(
                            f'Type hint requirement not met on {self.instance.__class__.__name__}.{field_name}')

        return datatypes_dict

    def fields(self):
        fields = dir(self.instance)
        fields.extend(list(self.instance.__annotations__.keys()))

        for field in fields:
            if '__' in field:
                continue
            if field[0] == '_':
                continue

            yield field

    def default_values(self) -> dict:
        datatypes = self.datatypes()

        default_values_dict = {}
        for field in self.fields():

            if hasattr(self.instance.__class__, field):
                value = getattr(self.instance.__class__, field)

            else:
                value = resolve_default_value(datatypes.get(field))

            if isinstance(value, property):

                # Allows default values to be set on properties.
                if hasattr(self.instance.__class__, f'_{field}'):
                    value = getattr(self.instance.__class__, f'_{field}')

                else:
                    value = resolve_default_value(datatypes.get(field))

            default_values_dict[field] = value

        return default_values_dict

    def items(self):
        try:
            datatypes = self.datatypes()
            default_values = self.default_values()
            for field in self.fields():
                yield field, datatypes[field], default_values[field]

        except KeyError as error:
            raise KeyError(error)
            raise Exception(f'Model {self.instance._name} field {field} has been set up incorrectly')

