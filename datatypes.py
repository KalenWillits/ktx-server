class DataType:
    def __init__(self):
        self._name = self.__class__.__name__

    def __call__(self, value, **kwargs):
        return self.execute(value, **kwargs)

    def execute(self, value, **kwargs):
        '''
        Overwrite this function to impliment a type change behavior and use this as type hints on model fields.
        This function should be able to indentify if the value is currently serialized for a pandas dataframe
        and change it back into the desired type.
        '''
        raise Exception(f'[ERROR] DataDataType {self._name} execute method not implimented.')

    def code(self, value, **kwargs):
        '''
        Optional overwrite method to change the data back into a dataframe safe format.
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
