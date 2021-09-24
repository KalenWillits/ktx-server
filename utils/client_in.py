import asyncio
import websockets
import json
# import pathlib
# import ssl

# ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
# localhost_pem = pathlib.Path(__file__).with_name("localhost.pem")
# ssl_context.load_verify_locations(localhost_pem)


def echo():
    content = input("content: ")
    return {"echo": {"content": content}}

class ClientIn:
    def __init__(self, address="localhost", port=5000):
        self.port = port
        self.address = address
        self.cmd = None
        self.data = dict()
        self.previous_data = None
        self.commands = {
            "!login": lambda: {"login": {"username": "development", "password": "pass"}},
            "!register": {"register": lambda: {"username": "development2", "password": "pass", "key": "MZBQOV0SA"}},
            "!create-admin-reg-key": lambda: {"create-admin-reg-key": {}},
            "!subscribe": lambda: {"subscribe": {"chat": {}}},
            "!echo": echo,
        }

    async def handle_input(self, websocket, middle_code):
        self.cmd = input("<- ")
        await middle_code(websocket)
        await self.handle_input(websocket, middle_code)

    async def parse_io(self, websocket):
        if self.commands.get(self.cmd):
            self.data = self.commands[self.cmd]()
        await websocket.send(json.dumps(self.data))

    async def connect(self):
        async with websockets.connect(self.uri) as websocket:
            await self.handle_input(websocket, self.parse_io)

    async def run(self):
        username = input("username: ")
        password = input("password: ")
        self.uri = f"ws://{username}:{password}@{self.address}:{self.port}"
        loop = asyncio.get_event_loop()
        loop.run_until_complete(await self.connect())
        loop.run_forever()


if __name__ == "__main__":
    client = ClientIn()
    client.run()
