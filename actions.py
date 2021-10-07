
class Action:
    def execute(*args, **kwargs):
        """
        Overwrite this method to create a custom action.
        """
        raise Exception("Action - Execute method not implimented.")


class ActionManager:
    def __init__(self, actions: list):
        self.actions = dict()
        for action in actions:
            self.actions[action.__name__] = action

    def __getitem__(self, key):
        return self.actions[key]

    def __setitem__(self, key, value):
        self.actions[key] = value
