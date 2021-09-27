import asyncio
import json

import websockets
import argparse

from websockets.exceptions import ConnectionClosedError

from .utils import get_snapshot, encrypt


class Server:
    def __init__(
        self,
        host: str = "localhost", port: int = 5000, debug: bool = True, db=None,
        tasks=None,
        models=None,
        actions=None,
        trust: list = ["*"],
        auth=lambda username, password: True,
    ):
        self.host = host
        self.port = port
        self.debug = debug
        self.clients = dict()
        self.db = db
        self.tasks = tasks
        self.models = models
        self.actions = actions
        self.auth = auth
        self.trust = trust
        self.commands = {
            "run": self.run_default(),
            "shell": self.run_shell(),
        }

    def log(self, *args):
        if self.debug:
            print(*args)

    def run_default(self):
        return lambda: websockets.serve(self.handle, self.host, self.port)

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

    def check_if_trusted(self, websocket) -> bool:
        if websocket.remote_address[0] in self.trust or "*" in self.trust:
            return True

        self.log(f"[UNTRUSTED-SOURCE-DENIED] {websocket.remote_address}")
        return False

    def state_event(self, websocket):
        self.log(f"[NOTIFY EVENT] {websocket.remote_address}")
        snapshot = get_snapshot(self.clients[websocket], self.db)
        return json.dumps(snapshot)

    def handle_auth(self, websocket) -> bool:
        username = websocket.request_headers.get("username")
        password = encrypt(websocket.request_headers.get("password"))
        if self.auth(username, password):
            return True
        else:
            return False

    async def notify_state(self, response):
        self.log(f"[NOTIFY STATE] {response}")
        if self.clients:
            payload = json.dumps(response)
            for client in self.clients.keys():
                await client.send(payload)

    async def register(self, websocket):
        self.log(f"[REGISTER-NEW-CONNECTION] {websocket.remote_address}")
        self.clients[websocket] = dict()

    async def unregister(self, websocket):
        self.log(f"[UNREGISTER-CLOSE-CONNECTION] {websocket.remote_address}")
        del self.clients[websocket]

    async def handle(self, websocket, host):
        self.log(f"[HANDLE-CONNECTION] {websocket.remote_address}")
        if self.check_if_trusted(websocket) and self.handle_auth(websocket):
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
                self.log(f"[CONNECTION CLOSED] {websocket.remote_address}")

            finally:
                await self.unregister(websocket)

    def run(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('cmd')
        parser.add_argument('--port', default=self.port)
        parser.add_argument('--host', default=self.host)
        parser.add_argument('--debug', default=self.debug, action='store_false')
        args = parser.parse_args()
        self.port = args.port
        self.host = args.host
        self.debug = args.debug

        if args.cmd == 'shell':
            self.commands.get('shell')()

        elif init_function := self.commands.get(args.cmd):
            try:
                self.log(f"[STARTING] {self.host}:{self.port}")
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
