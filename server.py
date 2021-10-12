import asyncio
import json
from uuid import uuid4

import websockets
import argparse

from websockets.exceptions import ConnectionClosedError

from .channels import ChannelManager
from .models import ModelManager
from .actions import ActionManager
from .tasks import TaskManager
from .headers import HeaderManager
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
        data: str = "./",
        trust: list = [],
        gate=all,
        channels: ChannelManager = ChannelManager(),
        models: ModelManager = ModelManager(),
        actions: ActionManager = ActionManager(),
        tasks: TaskManager = TaskManager(),
        headers: HeaderManager = HeaderManager(),
    ):
        self.host = host
        self.port = port
        self.debug = debug
        self.clients = {}

        if hasattr(self, "db"):
            self.db = db
        else:
            self.db = Database(models=models, path=data)

        self.tasks = tasks
        self.models = models
        self.actions = actions
        self.channels = channels
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
        global channels
        channels = self.channels
        global tasks
        tasks = self.tasks

        from IPython import embed

        for model in self.models:
            exec(f'from {model.__module__} import {model.__name__}', globals())

        return lambda: embed()

    def check_if_trusted(self, websocket) -> bool:
        if websocket.remote_address[0] in self.trust or not self.trust:
            return True

        self.log(f"[UNTRUSTED-SOURCE-DENIED] {websocket.remote_address}")
        return False

    def handle_headers(self, websocket_headers, websocket=None) -> bool:
        header_results = []
        for header in self.headers:
            kwargs = json.loads(websocket_headers.get(header))
            header_function_result = header.execute(
                db=db,
                models=self.models,
                channels=self.channels,
                tasks=self.tasks,
                actions=self.actions,
                server=self,
                websocket=websocket,
                **kwargs,
            )
            header_results.append(header_function_result)

            if not header_function_result:
                self.log(f"[HEADER-FAILED] {header._name}:{kwargs}")

        return self.gate(header_results)

    def broadcast(self, payload: json, channels: list):
        self.log(f"[BROADCAST] {payload} on channels {channels}")
        for channel_name in channels:
            for subscriber_pk in self.channels[channel_name]._subscribers:
                asyncio.ensure_future(self.clients[subscriber_pk].send(payload))

    async def register(self, websocket):
        self.log(f"[REGISTER-NEW-CONNECTION] {websocket.remote_address}")
        websocket.pk = str(uuid4())
        self.clients[websocket.pk] = websocket

    async def unregister(self, websocket):
        self.log(f"[UNREGISTER-CLOSE-CONNECTION] {websocket.remote_address}")
        del self.clients[websocket.pk]

    async def handle(self, websocket, host):
        self.log(f"[HANDLE-CONNECTION] {websocket.remote_address}")
        if self.check_if_trusted(websocket) and self.handle_headers(websocket.request_headers, websocket=websocket):
            await self.register(websocket)
            try:
                async for payload in websocket:
                    response = {}
                    channels = set()
                    errors = {"Errors": []}
                    query = json.loads(payload)
                    for action_name in query.keys():
                        if action := self.actions[action_name]:
                            try:
                                data, action_channels = action.execute(
                                    websocket=websocket,
                                    server=self,
                                    db=self.db,
                                    channels=self.channels,
                                    **query.get(action_name))

                                response.update(data)
                                channels.update(action_channels)

                            except Exception as error:
                                errors["Errors"].append(str(error))

                        else:
                            await websocket.send(json.dumps({"Errors": [f"No action [{action_name}]"]}))

                    if errors["Errors"]:
                        response.update(errors)

                    self.broadcast(json.dumps(response), list(channels))

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
                asyncio.get_event_loop().run_until_complete(
                    self.tasks.execute_startup_tasks(
                        db=self.db,
                        models=self.models,
                        tasks=self.tasks,
                        actions=self.actions,
                        channels=self.channels,
                        server=self))

                asyncio.get_event_loop().run_until_complete(init_function())
                asyncio.get_event_loop().run_until_complete(
                    self.tasks.execute_interval_tasks(
                        db=self.db,
                        models=self.models,
                        tasks=self.tasks,
                        actions=self.actions,
                        channels=self.channels,
                        server=self))

                asyncio.get_event_loop().run_forever()
            except KeyboardInterrupt:
                self.log("[SHUTDOWN]")
            finally:
                self.log("[CLEANUP-TASKS-STARTED]")
                asyncio.get_event_loop().run_until_complete(
                    self.tasks.execute_shutdown_tasks(
                        db=self.db,
                        models=self.models,
                        tasks=self.tasks,
                        actions=self.actions,
                        channels=self.channels,
                        server=self))

                self.db.save()
                self.log("[CLEANUP-TASKS-COMPLETE]")
        else:
            self.log(f"[ERROR] -- {args.cmd} is not a valid option.")
