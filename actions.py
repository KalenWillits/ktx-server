
class Action:
    def execute(*args, **kwargs):
        """
        Overwrite this method to create a custom action.
        """
        raise Exception("Action - Execute method not implimented.")


class ActionManager:
    def __init__(self, *actions):
        self.__actions__ = dict()
        for action in actions:
            self.__actions__[action.__name__] = action

    def __getitem__(self, key):
        return self.__actions__[key]

    def __setitem__(self, key, value):
        self.__actions__[key] = value
