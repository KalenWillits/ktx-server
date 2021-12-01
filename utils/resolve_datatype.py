def resolve_datatype(datatype, resolved_list: list = []):
    '''
    Recursively resolves data types as to support nested types.
    return ->  type function; if nested, returned from outer to inner.
    '''
    # Is the datatype nested?
    if hasattr(datatype, '__origin__'):
        # Loop through nested types and recursevily resolve them.
        if datatype.__args__:
            for inner_type in datatype.__args__:
                if inner_type is Ellipsis:
                    resolved_list.append(...)
                else:
                    resolved_list.append(datatype.__origin__)
                    resolved_list.append(resolve_datatype(inner_type, resolved_list=resolved_list))
        else:
            return datatype

    else:
        return datatype
