def apply_nested_datatype(db, value, datatype):
    if isinstance(datatype, tuple):
        outer_type = datatype[0]
        inner_type = datatype[1]

        if inner_type is Ellipsis:
            yield [outer_type(inner_value) for inner_value in value]

        elif inner_type is tuple:
            yield [apply_nested_datatype(inner_value, inner_datatype) for inner_value in value]

        elif inner_type is in db.models:



    if hasattr(datatype, '__origin__'):
        if datatype.__origin__ is list:
            if datatype.__args__:
                for inner_type in datatype.__args__:
                    yield [datatype(apply_nested_datatype(value)]
            else:
                yield datatype(value)






