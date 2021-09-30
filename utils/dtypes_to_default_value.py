def dtypes_to_default_value(dtype):
    if dtype == str:
        return ""
    elif dtype == int:
        return 0
    elif dtype == float:
        return 0.0
    elif dtype == list:
        return list()
    elif dtype == tuple:
        return tuple()
    elif dtype == dict:
        return dict()
    else:
        return None
