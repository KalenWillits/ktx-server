import asyncio
import websockets
import json
# import pathlib
# import ssl

# ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
# localhost_pem = pathlib.Path(__file__).with_name("localhost.pem")
# ssl_context.load_verify_locations(localhost_pem)

class ClientIn:
    def __init__(self, uri="ws://localhost:5000"):
        self.uri = uri
        self.cmd = None
        self.data = dict()
        self.previous_data = None
        self.commands = {
            "!login": {"login": {"username": "test", "password": "pass"}}
        }

    async def handle_input(self, websocket, middle_code):
        self.cmd = input("<- ")
        await middle_code(websocket)
        await self.handle_input(websocket, middle_code)

    async def parse_io(self, websocket):
        if self.commands.get(self.cmd):
            self.data = self.commands[self.cmd]
        await websocket.send(json.dumps(self.data))

    async def connect(self):
        async with websockets.connect(self.uri) as websocket:
            await self.handle_input(websocket, self.parse_io)

    async def run(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(await self.connect())
        loop.run_forever()


if __name__ == "__main__":
    client = ClientIn()
    client.run()
