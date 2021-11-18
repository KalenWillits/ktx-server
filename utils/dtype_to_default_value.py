def dtype_to_default_value(value):
    if isinstance(value, str) or value == str:
        return ''
    elif isinstance(value, int) or value == int:
        return 0
    elif isinstance(value, float) or value == float:
        return 0.0
    elif isinstance(value, list) or value == list:
        return []
    elif isinstance(value, tuple) or value == tuple:
        return tuple()
    elif isinstance(value, dict) or value == dict:
        return {}
    elif isinstance(value, set) or value == set:
        return set()
    else:
        return None
