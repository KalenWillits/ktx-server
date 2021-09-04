import asyncio
import websockets
import json
# import pathlib
# import ssl

# ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
# localhost_pem = pathlib.Path(__file__).with_name("localhost.pem")
# ssl_context.load_verify_locations(localhost_pem)

class ClientOut:
    def __init__(self, uri="ws://localhost:5000"):
        self.uri = uri
        self.data = {"feed": ""}
        self.previous_data = None

    async def connect(self):
        async with websockets.connect(self.uri) as websocket:
            while True:
                self.data = json.loads(await websocket.recv())
                print(f"->  {self.data.get('feed')}")
                await asyncio.sleep(1)

    def run(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.connect())
        loop.run_forever()


if __name__ == "__main__":
    client = ClientOut()
    client.run()
