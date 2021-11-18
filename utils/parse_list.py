def parse_list(string: str):
    if isinstance(string, list):
        return string.replace('[', '').replace(']', '').replace('\'', '').replace('\"', '').split(',')
    else:
        return string
