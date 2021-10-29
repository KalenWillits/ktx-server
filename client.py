import asyncio
import aioconsole
import websockets
import argparse
import json
import sys


class Sender:
    def __init__(self, url: str, commands: dict = {}, headers: dict = {}, actions: dict = {}):
        self.url = url
        self.cmd = None
        self.actions = actions
        self.headers = headers

    async def gather_input(self):
        self.cmd = await aioconsole.ainput(":")

    async def handle_input(self, websocket):
        await self.gather_input()
        await self.parse_and_send(websocket)

    async def parse_and_send(self, websocket):
        if data := self.actions.get(self.cmd):
            await aioconsole.aprint(f'[SENDER] {data}')
            await websocket.send(json.dumps(data))

    async def connect(self):
        try:
            async with websockets.connect(self.url, extra_headers=self.headers) as websocket:
                while True:
                    await self.handle_input(websocket)
        except Exception:
            await aioconsole.aprint('[RECIEVER] Connection closed.')

    async def run(self):
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(await self.connect())
            loop.run_forever()
        except websockets.exceptions.ConnectionClosedError:
            asyncio.ensure_future(aioconsole.aprint('[SENDER] Connection closed.'))
            sys.exit()


class Reciever:
    def __init__(self, url: str, headers: dict = {}):
        self.url = url
        self.headers = headers
        self.previous_data = None

    async def connect(self):
        try:
            async with websockets.connect(self.url, extra_headers=self.headers) as websocket:
                while True:
                    asyncio.ensure_future(aioconsole.aprint(f'[RECIEVER] {await websocket.recv()}'))
        except Exception:
            await aioconsole.aprint('[RECIEVER] Connection closed.')

    async def run(self):
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(await self.connect())
            loop.run_forever()
        except websockets.exceptions.ConnectionClosedError:
            asyncio.ensure_future(aioconsole.aprint('[RECIEVER] Connection closed.'))
            sys.exit()


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
