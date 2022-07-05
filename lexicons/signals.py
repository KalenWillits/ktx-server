class Signal:
    def __init__(self):
        self._name = self.__class__.__name__

    def response(self, data: dict | list | str | int, channels: list):
        return {self._name: data}, channels

    def execute(self, **kwargs):
        data = {}
        channels = []
        '''
        Overwrite this method to create a custom signal.

        :: return :: dict, [...channel_names]
        '''
        raise Exception('Signal - Execute method not implemented.')
        return self.response(data, channels)


class SignalManager:
    def __init__(self, *signals):
        self.__signals__ = {}
        for signal in signals:
            signal_instance = signal()
            self.__signals__[signal_instance._name] = signal_instance

    def __getitem__(self, key):
        return self.__signals__.get(key)

    def __setitem__(self, key, value):
        self.__signals__[key] = value
