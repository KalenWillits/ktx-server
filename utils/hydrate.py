import inspect
from typing import Set


def hydrate(model, df, db):
    'Takes the Pandas DataFrame values and generates model instances.'
    for i in range(df.shape[0]):
        result = df.iloc[i].to_dict()

        for field, dtype, default_value in model()._schema.items():
            if '__' in field:
                continue
            if dtype is Set:
                result[field] = []

            if inspect.isclass(default_value):
                if db.has(default_value.__name__):
                    foreign_key_df = db[default_value.__name__]
                    if key := result.get(field):
                        foreign_keys = [key]
                    else:
                        foreign_keys = []
                    foreign_key_df_filtered = foreign_key_df[foreign_key_df.pk.isin(foreign_keys)]
                    if not foreign_key_df_filtered.empty:
                        result[field] = next(hydrate(default_value, foreign_key_df_filtered, db))
                    else:
                        result[field] = None

            elif isinstance(default_value, (list, set)):
                default_value = next(iter(default_value))
                if db.has(default_value.__name__):
                    foreign_key_df = db[default_value.__name__]
                    foreign_keys = result.get(field, [])
                    foreign_key_df_filtered = foreign_key_df[foreign_key_df.pk.isin(foreign_keys)]
                    if not foreign_key_df_filtered.empty:
                        result[field] = hydrate(default_value, foreign_key_df_filtered, db)
                    else:
                        result[field] = []

            elif isinstance(default_value, bool):
                if result[field]:
                    result[field] = True
                else:
                    result[field] = False

            elif default_value is None:
                if not result[field]:
                    result[field] = None

        yield result
