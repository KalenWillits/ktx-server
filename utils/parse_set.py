def parse_set(string: str):
    if isinstance(string, str):
        return set(string.replace('{', '').replace('}', '').replace('\'', '').replace('\"', '').split(','))
    else:
        return string
