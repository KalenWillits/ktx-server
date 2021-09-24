import asyncio
import json
import websockets
import argparse

from websockets.exceptions import ConnectionClosedError

from .utils import get_snapshot


class Server:
    def __init__(
        self,
        address: str = "localhost", port: int = 5000, debug: bool = True, db=None,
        tasks=None,
        models=None,
        actions=None,
    ):
        self.address = address
        self.port = port
        self.debug = debug
        self.clients = dict()
        self.db = db
        self.tasks = tasks
        self.models = models
        self.actions = actions
        self.commands = {
            "run": self.run_default(),
            "dev": self.run_dev(),
            "shell": self.run_shell(),
        }

    def log(self, *args):
        if self.debug:
            print(*args)

    def run_default(self):
        return lambda: websockets.serve(self.handle, self.address, self.port)

    def run_dev(self):
        self.log("[DEVELOPMENT MODE]")
        self.debug = True
        return lambda: websockets.serve(
            self.handle,
            "localhost",
            self.port,
        )

    def run_shell(self):
        global db
        db = self.db
        global models
        models = self.models
        global actions
        actions = self.actions
        global tasks
        tasks = self.tasks

        from IPython import embed

        for model in self.models:
            exec(f'from {model.__module__} import {model.__name__}', globals())

        return lambda: embed()

    def state_event(self, websocket):
        self.log(f"[NOTIFY EVENT] {websocket.host} -- {websocket.local_address}")
        snapshot = get_snapshot(self.clients[websocket], self.db)
        return json.dumps(snapshot)

    async def notify_state(self, response):
        self.log(f"[NOTIFY STATE] {response}")
        if self.clients:
            payload = json.dumps(response)
            for client in self.clients.keys():
                await client.send(payload)

    async def register(self, websocket):
        self.log(f"[REGISTER] {websocket.host} -- {websocket.local_address}")
        self.clients[websocket] = dict()

    async def unregister(self, websocket):
        self.log(f"[UNREGISTER] {websocket.host} -- {websocket.local_address}")
        del self.clients[websocket]

    async def handle(self, websocket, address):
        await self.register(websocket)
        try:
            await websocket.send(self.state_event(websocket))
            async for payload in websocket:
                data = json.loads(payload)
                for action_name in data.keys():
                    if response := self.actions[action_name].execute(
                        websocket=websocket,
                        server=self,
                        db=self.db,
                        **data.get(action_name)
                    ):
                        await self.notify_state(response)

        except ConnectionClosedError:
            self.log(f"[CONNECTION CLOSED] {websocket.host} -- {websocket.local_address}")

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
                self.log(f"[STARTING] {self.address}:{self.port}")
                self.db.load()
                self.tasks.execute_startup_tasks(db=self.db, models=self.models, server=self)

                asyncio.get_event_loop().run_until_complete(init_function())
                asyncio.get_event_loop().run_until_complete(self.tasks.execute_periodic_tasks(
                                                            db=self.db, server=self)
                                                            )
                asyncio.get_event_loop().run_forever()
            except KeyboardInterrupt:
                self.log("[SHUTDOWN]")
            finally:
                self.log("[CLEANUP-TASKS-STARTED]")
                self.tasks.execute_shutdown_tasks(db=self.db, models=self.models, server=self)
                self.db.save()
                self.log("[CLEANUP-TASKS-COMPLETE]")
        else:
            self.log(f"[ERROR] -- {args.cmd} is not a valid option.")
