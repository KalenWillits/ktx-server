def resolve_datatype(datatype):
    '''
    Recursively resolves data types as to support nested types.
    return ->  type function; if nested, returned from outer to inner.
    '''
    # Is the datatype nested?
    if hasattr(datatype, '__origin__'):
        # Loop through nested types and recursevily resolve them.
        for inner_type in datatype.__args__:
            if inner_type is Ellipsis:
                return ...
            else:
                return datatype, resolve_datatype(inner_type)

        else:
            return datatype
