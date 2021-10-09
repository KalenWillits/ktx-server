import json


class Action:
    def __init__(self):
        self.name = self.__class__.__name__

    def response(self, data: dict, channels: list):
        return json.dumps({self.name: data}), channels

    def execute(self, **kwargs):
        data = {}
        channels = []
        """
        Overwrite this method to create a custom action.

        :: return :: dict, [...channel_names]
        """
        raise Exception("Action - Execute method not implimented.")
        return self.response(data, channels)


class ActionManager:
    def __init__(self, *actions):
        self.__actions__ = {}
        for action in actions:
            self.__actions__[action.name] = action()

    def __getitem__(self, key):
        return self.__actions__[key]

    def __setitem__(self, key, value):
        self.__actions__[key] = value
