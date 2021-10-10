import asyncio


class Channel:
    def __init__(self, publishers: set = set(), subscribers: set = set()):
        self.subscribers = subscribers
        self.publishers = publishers
        self.name = self.__class__.__name__

    def subscribe(self, websocket_pk):
        self.subscribers.add(websocket_pk)

    def unsubscribe(self, websocket_pk):
        self.subscribers.remove(websocket_pk)


class ChannelManager:
    def __init__(self, *channels):
        for channel in channels:
            self.__dict__[channel.__name__] = channel()

    def __getitem__(self, channel_name) -> Channel:
        return getattr(self, channel_name)

    def __setitem__(self, channel_name, channel):
        setattr(self, channel_name, channel)

    def __iter__(self):
        for value in self.__dict__.values():
            if isinstance(Channel, value):
                yield channel

    def add(self, channel):
        setattr(self, channel.name, channel)

    def drop(self, channel_name: str):
        delattr(self, channel_name)

