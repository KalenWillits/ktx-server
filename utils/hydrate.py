import pandas as pd

CORE_TYPES = (str, int, float, bool)
OUTER_TYPES = (list, dict)


def retrieve_foreign_data(db, model_name, pk: str):
    if not (query_df := db.query(model_name, pk=pk)).empty:
        foreign_data = next(hydrate(db, model_name, query_df))
        return foreign_data

    return None


def parse_datatype(db, datatype, value):

    if hasattr(datatype, '__origin__'):
        outer_type = datatype.__origin__
        inner_types = datatype.__args__

        if outer_type is list:
            if not inner_types[-1] is Ellipsis:
                while len(value) < len(inner_types):
                    if (inner_type := inner_types[0]) in db.models:
                        value.append(None)
                    else:
                        value.append(inner_type())

                value = value[:len(inner_types) + 1]

            result = []

            for index, inner_type in enumerate(inner_types):

                if index < len(value):
                    # Handle nested foreign Key
                    if inner_type in db.models:
                        result.append(parse_datatype(db, inner_type, value[index]))

                    # Handle repeated value
                    elif inner_type is Ellipsis:
                        if other_values := value[0:]:
                            for inner_value in other_values:
                                result.append(parse_datatype(db, inner_types[index - 1], inner_value))

                    # Handle other outer types.
                    elif inner_type in OUTER_TYPES or hasattr(inner_type, '__origin__'):
                        result.append(parse_datatype(db, inner_type, value[index]))

                    # Handle all else.
                    elif inner_type in CORE_TYPES:
                        if value[index] is None:
                            result.append(None)
                        else:
                            result.append(inner_type(value[index]))

            return result

        if outer_type is dict:
            assert len(inner_types) == 2, f'{inner_types} <- dict types can only contain a key type and value type.'
            assert inner_types[0] in CORE_TYPES, f'{inner_types[0]} <- is not a supported key type.'
            assert isinstance(value, dict), f'Validation error: {value} is not of type {datatype}'

            key_type = inner_types[0]
            value_type = inner_types[1]
            result = {}
            for key, data in value.items():
                result[key_type(key)] = parse_datatype(db, value_type, data)

            return result

    elif datatype in CORE_TYPES:
        if value is None:
            return None
        return datatype(value)

    # Resolve foreign key
    elif datatype in db.models:
        return retrieve_foreign_data(db, datatype.__name__, value)

    else:
        raise Exception(f'{datatype} is not supported.')


def hydrate(db, model_name: str, df: pd.DataFrame):
    instance = db.models[model_name]()
    for index in range(df.shape[0]):
        record = df.iloc[index].to_dict()
        for field, datatype in instance._schema.datatypes().items():
            record[field] = parse_datatype(db, datatype, record[field])

        yield record
