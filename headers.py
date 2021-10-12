class Header:
    def __init__(self):
        self._name = self.__class__.__name__

    def execute(self, **kwargs) -> bool:
        raise Exception('[ERROR] Header {self._name} execute functon not implimented.')


class HeaderManager:
    def __init__(self, *headers):
        self.__headers__ = {}
        for header in headers:
            self.__headers__[header._name] = header()

    def __getitem__(self, header_name: str):
        return self.__headers__[header_name]

    def __setitem__(self, header_name, header):
        self.__headers__[header_name] = header

    def __iter__(self):
        for header in self.__headers__.values():
            yield header
