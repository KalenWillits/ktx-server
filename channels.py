

class Channel:
    def __init__(self, name: str = None, subscribers: set = set()):
        self.subscribers = set(subscribers)
        self.name = name if name else self.__class__.__name__

    def subscribe(self, websocket_pk):
        self.subscribers.add(websocket_pk)

    def unsubscribe(self, websocket_pk):
        self.subscribers.remove(websocket_pk)

    def __str__(self):
        return f'<Channel:{self.name}>'

    def __repr__(self):
        return self.__str__()


class ChannelManager:
    def __init__(self, *channels):
        self.__channels__ = {}
        for channel in channels:
            self.__channels__[channel.__name__] = channel()

    def __getitem__(self, channel_name: str) -> Channel:
        return self.__channels__.get(channel_name)

    def __setitem__(self, channel_name: str, channel: Channel):
        self.__channels__[channel_name] = channel

    def __iter__(self):
        for channel in self.__channels__.values():
            yield channel

    def add(self, channel: Channel):
        self.__channels__[channel.name] = channel

    def drop(self, channel_name: str):
        del self.__channels__[channel_name]

    def create(self, channel_name: str, subscribers: set):
        if (invalid_type := type(subscribers)) is not set:
            raise TypeError(f'Invalid type: {invalid_type} -> subscribers')

        channel = Channel(name=channel_name, subscribers=set(subscribers))
        self.add(channel)

    def unregister(self, subscriber_pk: str):
        for channel in self:
            if subscriber_pk in channel.subscribers:
                channel.unsubscribe(subscriber_pk)
