import asyncio
import websockets
from aioconsole import ainput
import json
# import pathlib
# import ssl

# ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
# localhost_pem = pathlib.Path(__file__).with_name("localhost.pem")
# ssl_context.load_verify_locations(localhost_pem)

class ClientIn:
    def __init__(self, uri="ws://localhost:5000"):
        self.uri = uri
        self.data = {"feed": ""}
        self.previous_data = None

    async def handle_input(self, websocket, middle_code):
        self.data["feed"] = await ainput("<- ")
        await middle_code(websocket)
        await self.handle_input(websocket, middle_code)

    async def parse_io(self, websocket):
        await websocket.send(json.dumps(self.data))

    async def connect(self):
        async with websockets.connect(self.uri) as websocket:
            await self.handle_input(websocket, self.parse_io)

    def run(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.connect())
        loop.run_forever()


if __name__ == "__main__":
    client = ClientIn()
    client.run()
