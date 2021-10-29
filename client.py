import asyncio
import websockets
import argparse
import json


class Sender:
    def __init__(self, url: str, commands: dict = {}, headers: dict = {}, actions: dict = {}):
        self.url = url
        self.cmd = None
        self.actions = actions
        self.headers = headers

    async def handle_input(self, websocket):
        # TODO: Change this to an async input so the connection does not time out.
        self.cmd = input("<- ")
        await self.parse_and_send(websocket)
        # await self.handle_input(websocket)

    async def parse_and_send(self, websocket):
        if data := self.actions.get(self.cmd):
            await websocket.send(json.dumps(data))

    async def connect(self):
        async with websockets.connect(self.url, extra_headers=self.headers) as websocket:
            while True:
                await self.handle_input(websocket)
                # self.data = json.loads(await websocket.recv())
                # print(f"->  {self.data}")
                await asyncio.sleep(0.1)

    async def run(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(await self.connect())
        loop.run_forever()


class Reciever:
    def __init__(self, url: str, headers: dict = {}):
        self.url = url
        self.headers = headers
        self.data = dict()
        self.previous_data = None

    async def connect(self):
        async with websockets.connect(self.url, extra_headers=self.headers) as websocket:
            while True:
                self.data = json.loads(await websocket.recv())
                print(f"->  {self.data}")
                await asyncio.sleep(0.1)

    async def run(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(await self.connect())
        loop.run_forever()


class Client:
    def __init__(self, protocol='ws', host='localhost', port=5000, commands={}, headers={}, actions={}):
        self.protocol = protocol
        self.host = host
        self.port = port
        self.commands = commands
        self.headers = headers
        self.sender = Sender(f'{protocol}://{host}:{port}', commands=commands, headers=headers, actions=actions)
        self.reciever = Reciever(f'{protocol}://{host}:{port}', headers=headers)

    async def run_sender(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(await self.sender.run())
        loop.run_forever()

    async def run_reciever(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(await self.reciever.run())
        loop.run_forever()

    def run(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('cmd')
        args = parser.parse_args()

        if args.cmd == 'sender':
            asyncio.run(self.run_sender())

        elif args.cmd == 'reciever':
            asyncio.run(self.run_reciever())
