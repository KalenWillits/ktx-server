def options(field_name: str, options: list[str]):
    '''
    Inline snippit for an options field. Run exec on the result.
    '''
    return f"""_{field_name}_options = {{key: False for key in {options}}}

@property
def {field_name}(self) -> str:
    return next(
        filter(lambda value: value if self._{field_name}_options[value] else None, self._{field_name}_options),
        None
    )

@{field_name}.setter
def {field_name}(self, value: str):
    options = self._{field_name}_options.keys()
    assert value in options, f"invalid type option, choices are {options}."
    for option in options:
        if option.lower() == value.lower():
            self._{field_name}_options[option] = True
        else:
            self._{field_name}_options[option] = False"""
