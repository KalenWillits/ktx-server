import asyncio
import json
import websockets
import argparse
from websockets.exceptions import ConnectionClosedError
from database.database import db
from actions.actions import ActionManager
from apps.actions import actions
from tasks.tasks import TaskManager
from tasks.register import tasks
from models.register import models
from models.models import Model
from utils.get_snapshot import get_snapshot

TASKS = TaskManager(tasks)
ACTIONS = ActionManager(actions)
db.load()


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
        self.clients = dict()
        self.commands = {
            "run": self.run_default(),
            "dev": self.run_dev(),
            "shell": self.run_shell(),
            "client-in": self.run_client_in(),
            "client-out": self.run_client_out(),
        }

    def log(self, *args):
        if self.debug:
            print(*args)

    def run_client_in(self):
        from utils.client_in import ClientIn
        client = ClientIn()
        return lambda: client.run()

    def run_client_out(self):
        from utils.client_out import ClientOut
        client = ClientOut()
        return lambda: client.run()

    def run_default(self):
        return lambda: websockets.serve(self.handle, self.address, self.port)

    def run_dev(self):
        self.log("[DEVELOPMENT MODE]")
        self.debug = True
        return lambda: websockets.serve(self.handle, "localhost", self.port)

    def run_shell(self):
        from IPython import embed

        for model in models:
            exec(f'from {model.__module__} import {model.__name__}', globals())

        from database.utils import file_to_string, string_to_file
        from models.utils import hydrate

        return lambda: embed()

    def state_event(self, websocket):
        snapshot = get_snapshot(self.clients[websocket], db)
        return json.dumps(snapshot)

    async def notify_state(self, response):
        self.log("[NOTIFY STATE]")
        if self.clients:  # asyncio.wait doesn't accept an empty list
            payload = json.dumps(response)
            for client in self.clients.keys():
                await client.send(payload)

    async def register(self, websocket):
        self.log("[REGISTER]")
        self.clients[websocket] = dict()

    def subscribe(self, websocket, model: Model = None, pks: set = set()):
        self.clients[websocket][model] = pks

    async def unregister(self, websocket):
        self.log(["UNREGISTER"])
        del self.clients[websocket]

    async def handle(self, websocket, address):
        self.log("[STARTING]", self.address)
        await self.register(websocket)
        try:
            await websocket.send(self.state_event(websocket))
            async for payload in websocket:
                data = json.loads(payload)
                print(data)
                for action_name in data.keys():
                    if response := ACTIONS[action_name].run(
                        websocket=websocket,
                        server=self,
                        db=db,
                        **data.get(action_name)
                    ):
                        await self.notify_state(response)

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
                db.save()
        else:
            self.log(f"[ERROR] -- {args.cmd} is not a valid option.")
