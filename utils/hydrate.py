import pandas as pd


def hydrate(db, model_name: str, df: pd.DataFrame):
    'Takes the Pandas DataFrame values and generates fully populated dictionaries based on the selected model FKs.'
    model = db.models[model_name]
    for index in range(df.shape[0]):
        result = df.iloc[index].to_dict()

        for field, dtype, default_value in model()._schema.items():

            # FK resolver
            if default_value in db.models:
                if foreign_key := result.get(field):
                    foreign_table = default_value.__name__
                    foreign_key_df = db.query(foreign_table, pk=foreign_key)

                if not foreign_key_df.empty:
                    result[field] = next(hydrate(db, foreign_table, foreign_key_df))
                else:
                    result[field] = None

            # Iterable fields resolver
            elif dtype in (list[str], list[int], list[float], list[bool]):
                if len(default_value) > 0:
                    inner_value = next(iter(default_value))
                    if inner_value in db.models and (len(values := result[field]) > 0):
                        foreign_table = inner_value.__name__
                        foreign_key_df = db.query(foreign_table, pk__in=values)
                        result[field] = [foreign_model for foreign_model in hydrate(db, foreign_table, foreign_key_df)]

                elif values := df[field].iloc[0]:

                    if dtype == list[bool]:
                        cleaned_bool_values = []
                        for bool_value in values:
                            if bool_value:
                                cleaned_bool_values.append(True)
                            else:
                                cleaned_bool_values.append(False)
                        values = cleaned_bool_values

                    result[field] = values

                else:
                    result[field] = []

            # Boolean conversion (numpy uses bool64)
            elif dtype == bool:
                if result[field]:
                    result[field] = True
                else:
                    result[field] = False

            elif default_value is None:
                if not result[field]:
                    result[field] = None

        yield result
