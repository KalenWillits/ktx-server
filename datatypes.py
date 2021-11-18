class DataType:
    def __init__(self):
        self._name = self.__class__.__name__

    def __call__(self, value, **kwargs):
        return self.execute(value, **kwargs)

    def execute(self, value, **kwargs):
        '''
        Overwrite this function to impliment a type change behavior and use this as type hints on model fields.
        '''
        raise Exception(f'[ERROR] DataDataType {self._name} execute method not implimented.')

    def encode(self, value, **kwargs):
        '''
        Optional overwrite method to serialize data on save.
        i.e. derived data types such as lists and sets should be stored as strings.
        '''
        return value

    def decode(self, value, **kwargs):
        '''
        Optiomal overwrite method to change serialized data back into it's desired form.
        '''
        return value


class DataTypeManager:
    def __init__(self, *datatypes):
        self.__datatypes__ = {}
        for datatype in datatypes:
            datatype_instance = datatype()
            self.__datatypes__[datatype_instance._name] = datatype_instance

    def __getitem__(self, datatype_name: str):
        return self.__datatype__[datatype_name]

    def __setitem__(self, datatype_name: str, datatype):
        self.__datatypes__[datatype_name] = datatype

    def __iter__(self):
        for datatype in self.__datatypes__.values():
            yield datatype
