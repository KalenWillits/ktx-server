def handle_sort(kwargs, df):
    if '_sort' in kwargs.keys():
        if kwargs.get('_sort'):
            if kwargs['_sort'][0] == '-':
                ascending = False
                kwargs['_sort'] = kwargs['_sort'][1:]
            else:
                ascending = True
            df = df.sort_values(kwargs['_sort'], ascending=ascending)
            del kwargs['_sort']

    return kwargs, df


def handle_limit(kwargs, df):
    if '_limit' in kwargs.keys():
        df = df.head(kwargs['_limit'])
        del kwargs['_limit']

    return kwargs, df


column_filters = {
    'find': lambda df, column, value: df[df[column].str.contains(value, regex=False)],  # find in column
    'regex': lambda df, column, value: df[df[column].str.contains(value)],  # regex in column
    'eq': lambda df, column, value: df[df[column] == value],  # equals
    'gt': lambda df, column, value: df[df[column] > value],  # greater than
    'lt': lambda df, column, value: df[df[column] < value],  # less than
    'ge': lambda df, column, value: df[df[column] >= value],  # greater than or equal to
    'le': lambda df, column, value: df[df[column] <= value],  # less than or equal to
    'max': lambda df, column, value: df[df[column] == df[column].max()],  # maximum (value is unused)
    'min': lambda df, column, value: df[df[column] == df[column].min()],  # minimum (value is unused)
    'in': lambda df, column, value: df[df[column].isin(value)],  # Find all values that are in a list
    'nin': lambda df, column, value: df[~df[column].isin(value)],  # Find all values that are not in a list
    'includes': lambda df, column, value: df[df[column].apply(lambda cell_value: value in cell_value)],
    'excludes': lambda df, column, value: df[df[column].apply(lambda cell_value: value in cell_value)]
}
