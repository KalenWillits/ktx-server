from typing import get_type_hints


class Schema:
    def __init__(self, instance):
        self.instance = instance

    def dtypes(self):
        dtypes_dict = get_type_hints(self.instance.__class__)
        for field_name in dir(self.instance):
            if '__' in field_name:
                continue
            if field_name[0] == '_':
                continue

            # Gathering and formatting dtypes for properties
            if hasattr(self.instance.__class__, field_name):
                field_value = getattr(self.instance.__class__, field_name)
                if hasattr(field_value, 'fget'):
                    field_dtype = get_type_hints(field_value.fget)
                    try:
                        dtypes_dict.update({field_name: field_dtype['return']})
                    except KeyError:
                        raise Exception(
                            f'Type hint requirement not met on {self.instance.__class__.__name__}.{field_name}')

        return dtypes_dict

    def fields(self):
        for field in dir(self.instance):
            if '__' in field:
                continue
            if field[0] == '_':
                continue

            yield field

    def default_values(self) -> dict:
        dtypes = self.dtypes()

        default_values_dict = {}
        for field in self.fields():
            if hasattr(self.instance.__class__, field):
                value = getattr(self.instance.__class__, field)
            else:
                value = None

            if isinstance(value, property):

                # Allows default values to be set on properties.
                if hasattr(self.instance.__class__, f'_{field}'):
                    value = getattr(self.instance.__class__, f'_{field}')

                else:
                    value = dtypes.get(field)()

            default_values_dict[field] = value

        return default_values_dict

    def items(self):
        dtypes = self.dtypes()
        default_values = self.default_values()
        for field in self.fields():
            yield field, dtypes[field], default_values[field]
