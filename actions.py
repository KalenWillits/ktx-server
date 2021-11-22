class Action:
    def __init__(self):
        self._name = self.__class__.__name__

    def response(self, data, channels: list):
        return {self._name: data}, channels

    def execute(self, **kwargs):
        data = {}
        channels = []
        '''
        Overwrite this method to create a custom action.

        :: return :: dict, [...channel_names]
        '''
        raise Exception('Action - Execute method not implimented.')
        return self.response(data, channels)


class ActionManager:
    def __init__(self, *actions):
        self.__actions__ = {}
        for action in actions:
            action_instance = action()
            self.__actions__[action_instance._name] = action_instance

    def __getitem__(self, key):
        return self.__actions__.get(key)

    def __setitem__(self, key, value):
        self.__actions__[key] = value
