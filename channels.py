import asyncio


class Channel:
    def __init__(self, publishers: set = {}, subscribers: set = {}):
        self.subscribers = subscribers
        self.publishers = publishers
        self.name = self.__class__.__name__

    def subscribe(self, websocket_pk):
        self.subscribers.add(websocket_pk)

    def unsubscribe(self, websocket_pk):
        self.subscribers.remove(websocket_pk)

    def broadcast(self, payload: dict):
        for subscriber in self.subscribers:
            asyncio.ensure_future(subscriber.send(payload))


class ChannelManager:
    def __init__(self, *channels):
        self.__channels__ = {}
        for channel in channels:
            self.__channels__[channel.__name__] = channel()

    def __getitem__(self, channel_name) -> Channel:
        return self.__channels__[channel_name]

    def __setitem__(self, channel_name, channel):
        self.__channels__[channel_name] = channel

    def __iter__(self):
        for channel in self.__channel__.values():
            yield channel

    def add(self, channel):
        self.__channels__[channel.name] = channel

    def drop(self, channel_name: str):
        del self.__channels__[channel_name]

