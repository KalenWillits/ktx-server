import asyncio
import json
import websockets


class Server:
    def __init__(
        self,
        address: str = "localhost",
        port: int = 5000,
        debug: bool = True,
    ):
        self.address = address
        self.port = port
        self.debug = debug
        self.state = {"feed": ""}
        self.clients = set()

    def log(self, *args):
        if self.debug:
            print(*args)

    def state_event(self):
        return json.dumps(self.state)

    async def notify_state(self):
        self.log("[NOTIFY STATE]")
        if self.clients:  # asyncio.wait doesn't accept an empty list
            message = self.state_event()
            for client in self.clients:
                await client.send(message)

    async def register(self, websocket):
        self.log("[REGISTER]")
        self.clients.add(websocket)

    async def unregister(self, websocket):
        self.log(["UNREGISTER"])
        self.clients.remove(websocket)

    async def handle(self, websocket, path):
        self.log("[STARTING]")
        # register(websocket) sends user_event() to websocket
        await self.register(websocket)
        try:
            await websocket.send(self.state_event())
            async for payload in websocket:
                data = json.loads(payload)
                if out_msg := data["feed"]:
                    self.state["feed"] = out_msg
                    await self.notify_state()

        finally:
            await self.unregister(websocket)

    def run(self):
        start_server = websockets.serve(self.handle, self.address, self.port)
        try:
            asyncio.get_event_loop().run_until_complete(start_server)
            asyncio.get_event_loop().run_forever()
        except KeyboardInterrupt:
            self.log("[SHUTDOWN]")
        finally:
            pass
