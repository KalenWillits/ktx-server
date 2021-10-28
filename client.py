import asyncio
import websockets
import json
import os
import sys


# class In:
#     def __init__(self, address='localhost', port='5000', commands: dict = {}, headers: list = []):
#         self.address = address
#         self.port = port
#         self.cmd = None
#         self.data = dict()
#         self.previous_data = None
#         self.commands = commands

#     async def handle_input(self, websocket, middle_code):
#         self.cmd = input("<- ")
#         await middle_code(websocket)
#         await self.handle_input(websocket, middle_code)

#     async def parse_io(self, websocket):
#         if self.commands.get(self.cmd):
#             self.data = self.commands[self.cmd]
#         await websocket.send(json.dumps(self.data))

#     async def connect(self):
#         async with websockets.connect(self.uri) as websocket:
#             await self.handle_input(websocket, self.parse_io)
#             while True:
#                 self.data = json.loads(await websocket.recv())
#                 print(f"->  {self.data}")
#                 await asyncio.sleep(0.1)


#     async def run(self):
#         loop = asyncio.get_event_loop()
#         loop.run_until_complete(await self.connect())
#         loop.run_forever()


# class Out:
#     def __init__(self, uri="ws://localhost:5000"):
#         self.uri = uri
#         self.data = dict()
#         self.previous_data = None

#     async def connect(self):
#         async with websockets.connect(self.uri) as websocket:
#             while True:
#                 self.data = json.loads(await websocket.recv())
#                 print(f"->  {self.data}")
#                 await asyncio.sleep(0.1)

#     async def run(self):
#         loop = asyncio.get_event_loop()
#         loop.run_until_complete(await self.connect())
#         loop.run_forever()

headers = {"Login":json.dumps({"username":"test", "password":"test"})}
commands = {"Echo": {"message": 'Hello!'}}



class Client:
    def __init__(self, protocol='ws', address='localhost', port='5000', commands: dict = commands, headers=headers):
        self.protocol = protocol
        self.cmd = None
        self.feed = []
        self.commands = commands
        self.address = address
        self.port = port
        self.cmd = None
        self.commands = commands
        self.headers = headers

    def build_url(self):
        return f'{self.protocol}://{self.address}:{self.port}'

    async def reciever(self, websocket):
        if recieved_data := await websocket.recv():
            print(recieved_data)



    async def ainput(self, string: str) -> str:
        await asyncio.get_event_loop().run_in_executor(
            None, lambda s=string: sys.stdout.write(s+' '))
        return await asyncio.get_event_loop().run_in_executor(
            None, sys.stdin.readline)

    async def send(self, websocket):
        if data := self.commands.get(self.cmd):
            await websocket.send(json.dumps(data))
            self.feed.append(f'[SEND] -> {data}')

    async def main(self):
        async with websockets.connect(self.build_url(), extra_headers=self.headers) as websocket:
            try:
                while True:
                    terminal = os.get_terminal_size()

                    # Get resulting contents
                    if command := await self.ainput('<-'):
                        self.cmd = command

                    # Json string
                    asyncio.ensure_future(self.reciever(websocket))

                    await asyncio.sleep(0.1)

            finally:
                pass

    async def run(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(await self.main())
        loop.run_forever()


if __name__ == '__main__':
    asyncio.run(Client().run())
