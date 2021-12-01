import re

UUID4PATTERN = re.compile('^[0-9A-F]{8}-[0-9A-F]{4}-[4][0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}$/i')


def is_uuid(uuid_to_test) -> bool:
    return UUID4PATTERN.match(str(uuid_to_test))
