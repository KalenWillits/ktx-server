class DataType:
    def __init__(self, **kwargs):
        self.__dict__.update(**kwargs)
        self._name = self.__class__.__name__

    def __call__(self, value, encode=False):
        if encode:
            return self.encode(value)
        return self.decode(value)

    def decode(self, value):
        '''
        data -> true form
        Overwrite this function to impliment a type change behavior and use this as type hints on model fields.
        This function should be able to indentify if the value is currently serialized for a pandas dataframe
        and change it back into the desired type.
        '''
        raise Exception(f'[ERROR] DataDataType {self._name} execute method not implimented.')

    def encode(self, value):
        '''
        data -> serialized form
        Optional overwrite method to change the data back into a dataframe safe format.
        '''
        return value

    def hydrate(self, value, db, encode=False):
        '''
        data -> data
        Overwrite this method to handle custom hydrate behavior
        Such as - Foreign key look ups.
        '''
        return self(value, encode=encode)


class DataTypeManager:
    def __init__(self, *datatypes):
        self.__datatypes__ = {}
        for datatype in datatypes:
            datatype_instance = datatype()
            self.__datatypes__[datatype_instance._name] = datatype_instance

    def __getitem__(self, datatype_name: str):
        return self.__datatypes__[datatype_name]

    def __setitem__(self, datatype_name: str, datatype):
        self.__datatypes__[datatype_name] = datatype

    def __iter__(self):
        for datatype in self.__datatypes__.values():
            yield datatype
