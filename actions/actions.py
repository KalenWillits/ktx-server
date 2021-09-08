from models.utils import to_snake


class Action:
    def __init__(self, key: str = None):
        self.key = key

    def run(self, *args, **kwargs):
        """
        Overwrite this method to create a custom action.
        """
        raise Exception(f"[{self.key}] - Action - Run Method not implimented.")


class ActionManager:
    def __init__(self, actions: list):
        self.actions = dict()
        for action in actions:
            self.actions[action.key] = action

    def __getitem__(self, key):
        return self.actions[key]

    def __setitem__(self, key, value):
        self.actions[key] = value
