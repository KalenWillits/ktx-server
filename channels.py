

class Channel:
    def __init__(self, publishers: set = set(), subscribers: set = set(), name: str = None):
        self._subscribers = subscribers
        self._name = name if name else self.__class__.__name__

    def subscribe(self, websocket_pk):
        self._subscribers.add(websocket_pk)

    def unsubscribe(self, websocket_pk):
        self._subscribers.remove(websocket_pk)


class ChannelManager:
    def __init__(self, *channels):
        self.__channels__ = {}
        for channel in channels:
            self.__channels__[channel.__name__] = channel()

    def __getitem__(self, channel_name: str) -> Channel:
        return self.__channels__[channel_name]

    def __setitem__(self, channel_name: str, channel: Channel):
        self.__channels__[channel_name] = channel

    def __iter__(self):
        for channel in self.__channels__.values():
            yield channel

    def add(self, channel: Channel):
        self.__channels__[channel._name] = channel

    def drop(self, channel_name: str):
        del self.__channels__[channel_name]
