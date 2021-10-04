import asyncio
import json

import websockets
import argparse

from websockets.exceptions import ConnectionClosedError

from .utils import get_snapshot
from .models import ModelManager
from .actions import ActionManager
from .tasks import TaskManager
from .database import Database


class Server:
    """
    host: String representing the origin address.
    port: Interger representing port used by server.
    debug: Boolean that toggles if log messages are printed to the terminal.
    database: Database object passed from the pandas database.
    data: String representing the location of the stored .csv files from the database.
        This allows for the database to be initialized outside of the server.
    trust: List of IP addresses the server will allow new websocket connections with.
        By default all connections are allowed.
    headers: Dictionary of custom header functions in the format of `{HEADER-NAME : HEADER-FUNCTION}`.
        The header function should return a boolean value. (This is where authorization takes place.)
    gate: Function taking a list of boolean values. These boolean values are a list of results genereated from the
        header. By default, as long as one header is true, the connection is allowed. Custom conditions for each
        header result can be accessed by using the index in order of the headers dict.
    models: ModelManager class connecting the server to the database models.
    actions: ActionManager class connecting the server to the action functions.
    tasks: TaskManager class connecting the server to the task functions.
    """
    def __init__(
        self,
        host: str = "localhost",
        port: int = 5000,
        debug: bool = True,
        db: Database = None,
        data: str = "/",
        trust: list = ["*"],
        headers: dict = dict(),
        gate=any,
        models: ModelManager = ModelManager([]),
        actions: ActionManager = ActionManager([]),
        tasks: TaskManager = TaskManager([]),
    ):
        self.host = host
        self.port = port
        self.debug = debug
        self.clients = dict()

        if hasattr(self, "db"):
            self.db = db
        else:
            self.db = Database(models=models, path=data)

        self.tasks = tasks
        self.models = models
        self.actions = actions
        self.trust = trust
        self.headers = headers
        self.gate = gate
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
        payload = get_snapshot(self.clients[websocket], self.db)
        if payload:
            self.log(f"[NOTIFY-EVENT] {websocket.remote_address}")
            return json.dumps(payload)

    def handle_headers(self, websocket_headers) -> bool:
        header_results = list()
        for header, function in self.headers.items():
            delivered_header_value = websocket_headers.get(header)
            header_function_result = function(delivered_header_value, db=db, server=self)
            header_results.append(header_function_result)

            if not header_function_result:
                self.log(f"[HEADER-FUNCTION-FAILED] Header: {header}, Value: {delivered_header_value}")

        return self.gate(header_results)

    async def notify_state(self, response):
        self.log(f"[NOTIFY STATE] {response}")
        if self.clients:
            payload = json.dumps(response)
            if payload:
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

        if self.check_if_trusted(websocket) and self.handle_headers(websocket.request_headers):
            await self.register(websocket)
            try:
                if event_payload := self.state_event(websocket):
                    await websocket.send(event_payload)
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
