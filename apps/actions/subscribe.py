from actions import Action

class Subscribe(Action):
    key = "subscribe"

    def execute(*args, **kwargs):
        server = kwargs.get("server")
        websocket = kwargs.get("websocket")
        subscriptions = kwargs.get("subscriptions")
        server.clients[websocket].update(subscriptions)
