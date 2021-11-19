from ..models import Model
import pandas as pd


def hydrate(db, model_name: str, dataframe: pd.DataFrame, encode: bool = False):
    '''
    Recursive function to build a dictionary of all values including foreign keys.
    '''
    for index in dataframe.index:
        pk = dataframe.pk.iloc[0]
        instance = db.get(model_name, pk)
        result = {}
        instance_dict = instance._to_dict(encode=encode)

        for field, datatype, value in zip(instance_dict.keys(), instance._schema.datatypes(), instance_dict.values()):
            result[field] = datatype.hydrate(value, db, encode=encode)

        yield result
