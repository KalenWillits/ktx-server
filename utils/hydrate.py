import inspect
from .to_snake import to_snake


def hydrate(model, df, db):
    'Takes the Pandas DataFrame values and generates model instances.'
    for i in range(df.shape[0]):
        result = df.iloc[i].to_dict()

        for field, dtype, default_value in model().schema.items():
            if '__' in field:
                continue
            if dtype is set:
                result[field] = list()

            if inspect.isclass(default_value):
                if db.has(to_snake(default_value.__name__)):
                    foreign_key_df = db.__dict__[to_snake(default_value.__name__)]
                    if key := result.get(field):
                        foreign_keys = [key]
                    else:
                        foreign_keys = list()
                    foreign_key_df_filtered = foreign_key_df[foreign_key_df.pk.isin(foreign_keys)]
                    if not foreign_key_df_filtered.empty:
                        result[field] = next(hydrate(default_value, foreign_key_df_filtered, db))

            elif isinstance(default_value, (list, set)):
                default_value = next(iter(default_value))
                if db.has(to_snake(default_value.__name__)):
                    foreign_key_df = db[to_snake(default_value.__name__)]
                    foreign_keys = result.get(field, list())
                    foreign_key_df_filtered = foreign_key_df[foreign_key_df.pk.isin(foreign_keys)]
                    if not foreign_key_df_filtered.empty:
                        result[field] = hydrate(default_value, foreign_key_df_filtered, db)
                    else:
                        result[field] = list()

            elif isinstance(default_value, bool):
                if result[field]:
                    result[field] = True
                else:
                    result[field] = False

        yield result
