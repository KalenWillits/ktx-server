CORE_TYPES = (str, int, float, bool)
OUTER_TYPES = (list, dict)


def parse_datatype(datatype, value, db):

    if hasattr(datatype, '__origin__'):
        outer_type = datatype.__origin__
        inner_types = datatype.__args__

        # assert isinstance(value, outer_type), f'Validation error -> {value} is not of type {outer_type}.'

        if outer_type is list:
            if not inner_types[-1] is Ellipsis:
                assert_message = f'Validation error -> {inner_types} does not match length of {value}.'
                assert len(value) == len(inner_types), assert_message

            result = []

            for index, inner_type in enumerate(inner_types):
                # Handle Foreign Key
                if inner_type in db.models:
                    if index < len(value):
                        if value[index] is None:
                            result.append(None)
                        else:
                            result.append(str(value[index]))

                # Handle repeated value
                elif inner_type is Ellipsis:
                    result.extend([parse_datatype(inner_types[0], inner_value, db) for inner_value in value[1:]])

                # Handle other outer types.
                elif inner_type in OUTER_TYPES or hasattr(inner_type, '__origin__'):
                    if index < len(value):
                        result.append(parse_datatype(inner_type, value[index], db))

                # Handle all else.
                elif inner_type in CORE_TYPES:
                    if index < len(value):
                        if value[index] is None:
                            result.append(None)
                        else:
                            result.append(inner_type(value[index]))

                else:
                    raise TypeError(f'{inner_type} is not a supported type.')

            return result

        if outer_type is dict:
            assert len(inner_types) == 2, f'{inner_types} <- dict types can only contain a key type and value type.'
            assert inner_types[0] in CORE_TYPES, f'{inner_types[0]} <- is not a supported key type.'

            key_type = inner_types[0]
            value_type = inner_types[1]
            result = {}
            for key, data in value.items():
                result[key_type(key)] = parse_datatype(value_type, data, db)

            return result

    elif datatype in CORE_TYPES:
        if value is None:
            return None
        return datatype(value)

    elif datatype in db.models:
        if value is None:
            return None
        else:
            return str(value)

    else:
        raise Exception(f'{datatype} is not supported.')
