
class DataType:
    def __init__(self):
        self._name = self.__class__.__name__

    def __call__(self, value, **kwargs):
        return self.execute(value, **kwargs)

    def execute(self, value, **kwargs):
        '''
        Overwrite this function to impliment a type change behavior and use this as type hints on model fields.
        '''
        raise Exception(f'[ERROR] DataType {self._name} execute method not implimented.')

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
    def __init__(self, *data_types):
        self.__data_types__ = {}
        for data_type in data_types:
            data_type_instance = data_type()
            self.__data_types__[data_type._name] = data_type_instance

    def __getitem__(self, data_type_name: str):
        return self.__data_type__[data_type_name]

    def __setitem__(self, data_type_name: str, data_type):
        self.__data_types__[data_type_name] = data_type

    def __iter__(self):
        for data_type in self.__data_types__.values():
            yield data_type
