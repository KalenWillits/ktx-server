import asyncio
import json
import websockets
import argparse
from websockets.exceptions import ConnectionClosedError
from clients.client_in import ClientIn
from clients.client_out import ClientOut


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
        self.commands = {
            "run": self.run_std(),
            "dev": self.run_dev(),
            "shell": self.run_shell(),
            "client-in": self.run_client_in(),
            "client-out": self.run_client_out(),
        }

    def log(self, *args):
        if self.debug:
            print(*args)

    def run_client_in(self):
        client = ClientIn()
        return lambda: client.run()

    def run_client_out(self):
        client = ClientOut()
        return lambda: client.run()

    def run_std(self):
        return lambda: websockets.serve(self.handle, self.address, self.port)

    def run_dev(self):
        self.log("[DEVELOPMENT MODE]")
        self.debug = True
        return lambda: websockets.serve(self.handle, "localhost", self.port)

    def run_shell(self):
        from IPython import embed

        # for model in models:
        #     exec(f'from {model.__module__} import {model.__name__}', globals())
        # from database.database import db
        # from database.utils import file_to_string, string_to_file
        # from models.utils import hydrate
        return lambda: embed()

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

    async def handle(self, websocket, address):
        self.log("[STARTING]", self.address)
        # register(websocket) sends user_event() to websocket
        await self.register(websocket)
        try:
            await websocket.send(self.state_event())
            async for payload in websocket:
                data = json.loads(payload)
                if out_msg := data["feed"]:
                    self.state["feed"] = out_msg
                    await self.notify_state()
        except ConnectionClosedError:
            self.log(f"[CONNECTION ERROR] {websocket.host} -- {websocket.local_address}")

        finally:
            await self.unregister(websocket)

    def run(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('cmd')
        parser.add_argument('-p', '--port', default=self.port)
        parser.add_argument('-a', '--address', default=self.address)
        parser.add_argument('-d', '--debug', default=self.debug, action='store_false')
        args = parser.parse_args()
        self.port = args.port
        self.address = args.address
        self.debug = args.debug

        if args.cmd == 'shell':
            self.commands.get('shell')()

        elif init_function := self.commands.get(args.cmd):
            try:
                asyncio.get_event_loop().run_until_complete(init_function())
                asyncio.get_event_loop().run_forever()
            except KeyboardInterrupt:
                self.log("[SHUTDOWN]")
            finally:
                pass
        else:
            self.log(f"[ERROR] -- {args.cmd} is not a valid option.")
