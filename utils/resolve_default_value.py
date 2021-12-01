from .resolve_datatype import resolve_datatype


def resolve_default_value(input_datatype):
    if (datatuple := resolve_datatype(input_datatype)) is tuple:
        if datatype := datatuple[1] is Ellipsis:
            return datatuple[0]()
        else:
            if datatype is tuple:
                return resolve_default_value(datatuple[1])
            elif datatype is list:
                return [resolve_default_value(datatuple[1])]
            elif datatype is dict:
                key = datatuple[1]
                value = datatuple[2]
                return {key: resolve_default_value(value)}
            else:
                raise Exception(f'Invalid datatype found {datatype}')

    # If datatuple in not a tuple, return the default datatype's value.
    return input_datatype()
