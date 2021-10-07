class Channel:
    def __init__(self, publishers: list = [], subscribers: list = []):
        self.subscribers = subscribers
        self.publishers = publishers


class ChannelManager:
    def __init__(self, *channels):
        self.__channels__ = dict()
        for channel in channels:
            self.__channels__[channel.__name__] = channel

    def __getitem__(self, channel_name) -> Channel:
        return self.__channels__[channel_name]

    def __setitem__(self, channel_name, channel):
        self.__channels__[channel_name] = channel
