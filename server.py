import os
import asyncio
import json
from json import JSONDecodeError
from uuid import uuid4
from datetime import datetime
import argparse

import websockets

from .utils import handle_connect, handle_disconnect
from .channels import ChannelManager
from .models import ModelManager
from .actions import ActionManager
from .tasks import TaskManager
from .headers import HeaderManager
from .database import Database


class Server:
    '''
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
    '''
    def __init__(
        self,
        protocol: str = os.environ.get('PROTOCOL', 'ws'),
        host: str = os.environ.get('HOST', 'localhost'),
        port: int = os.environ.get('PORT', 5000),
        debug: bool = os.environ.get('DEBUG', True),
        database: Database = None,
        data: str = os.environ.get('DATA', './'),
        trust: list[str, ...] = os.environ.get('TRUST', []),
        gate: callable = all,
        cache: dict = {},
        connect=handle_connect,
        disconnect=handle_disconnect,
        channels: ChannelManager = ChannelManager(),
        models: ModelManager = ModelManager(),
        actions: ActionManager = ActionManager(),
        tasks: TaskManager = TaskManager(),
        headers: HeaderManager = HeaderManager(),

    ):
        self.host = host
        self.port = port
        self.debug = debug
        self.cache = cache

        # TODO move clients to cache
        self.clients = {}

        if hasattr(self, 'database'):
            self.database = database
        else:
            self.database = Database(models=models, path=data)

        self.tasks = tasks
        self.models = models
        self.actions = actions
        self.channels = channels
        self.trust = trust
        self.headers = headers
        self.gate = gate
        self.connect = connect
        self.disconnect = disconnect
        self.commands = {
            'run': self.run_default(),
            'shell': self.run_shell,
            'migrate': self.run_migrations,
        }

    def log(self, *args):
        if self.debug:
            print(str(datetime.now()), *args)

    def run_default(self):
        return lambda: websockets.serve(self.handle, self.host, self.port)

    def run_shell(self):
        global db
        db = self.database
        db.audit_fields()
        global sv
        sv = self

        from IPython import embed

        for model in self.models:
            exec(f'from {model.__module__} import {model.__name__}', globals())

        embed()

    def run_migrations(self):
        self.database.migrate()
        self.database.save()

    def check_if_trusted(self, websocket) -> bool:
        if websocket.remote_address[0] in self.trust or not self.trust:
            return True

        self.log(f'[UNTRUSTED-SOURCE-DENIED] {websocket.remote_address}')
        return False

    def handle_headers(self, websocket_headers, websocket=None) -> bool:
        header_results = []
        errors = {'Errors': []}
        kwargs = {}
        incoming_headers = {header.title() for header in websocket_headers.keys()}
        local_headers = {header._name for header in self.headers}
        selected_headers = incoming_headers & local_headers

        for header_name in selected_headers:
            header = self.headers[header_name]
            if data_string := websocket_headers.get(header._name):
                try:
                    kwargs = json.loads(data_string)
                except (TypeError, JSONDecodeError):
                    kwargs = {'header': data_string}

            try:
                header_function_result = header.execute(
                    db=self.database,
                    sv=self,
                    ws=websocket,
                    **kwargs,
                )
                header_results.append(header_function_result)

                if not header_function_result:
                    self.log(f'[HEADER-CHECK-FAILED] {header._name}:{kwargs}')

            except Exception as error:
                errors['Errors'].extend(error.args)
                if self.debug:
                    raise error

        if errors['Errors']:
            asyncio.ensure_future(websocket.send(json.dumps(errors)))

        return self.gate(header_results)

    def broadcast(self, payload: dict, channels: list):
        self.log(f'[BROADCAST] {payload} on channels {channels}')
        for channel_name in channels:
            if channel := self.channels[channel_name]:
                for subscriber_pk in channel.subscribers:
                    if subscriber_pk in self.clients.keys():
                        asyncio.ensure_future(self.clients[subscriber_pk].send(json.dumps(payload)))

            else:
                self.log(f'[CHANNEL-NOT-FOUND] {channel_name}')

    async def register(self, websocket):
        self.log(f'[REGISTER-NEW-CONNECTION] {websocket.remote_address}')
        self.clients[websocket.pk] = websocket

    async def unregister(self, websocket):
        self.log(f'[UNREGISTER-CLOSE-CONNECTION] {websocket.remote_address}')
        del self.clients[websocket.pk]
        self.channels.unregister(websocket.pk)

    async def handle(self, websocket, host):
        self.log(f'[HANDLE-CONNECTION] {websocket.remote_address}')
        websocket.pk = str(uuid4())

        if self.check_if_trusted(websocket) and self.handle_headers(websocket.request_headers, websocket=websocket):
            self.connect(ws=websocket, sv=self, db=self.database)
            await self.register(websocket)
            try:
                async for payload in websocket:
                    response = []
                    channels = set()
                    errors = {'Errors': []}
                    incoming_actions = json.loads(payload)
                    if isinstance(incoming_actions, dict):
                        incoming_actions = [incoming_actions]

                    for incoming_action in incoming_actions:
                        action_name = next(iter(incoming_action.keys()), None)
                        if action := self.actions[action_name]:
                            try:
                                data, action_channels = action.execute(
                                    ws=websocket,
                                    sv=self,
                                    db=self.database,
                                    **incoming_action.get(action_name))

                                response.append(data)
                                channels.update(action_channels)
                            except Exception as error:
                                errors['Errors'].extend(error.args)
                                if self.debug:
                                    raise error

                        else:
                            await websocket.send(json.dumps([{'Errors': [f'No action [{action_name}]']}]))

                    if errors['Errors']:
                        response.append(errors)
                        channels.add(websocket.auth)

                    self.broadcast(response, list(channels))

            finally:
                self.disconnect(ws=websocket, sv=self, db=self.database)
                self.log(f'[CONNECTION CLOSED] {websocket.remote_address}')
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

        elif args.cmd == 'migrate':
            self.commands.get('migrate')()

        elif init_function := self.commands.get(args.cmd):
            try:
                self.log(f'[STARTING] {self.host}:{self.port}')
                self.database.migrate()
                self.tasks.execute_startup_tasks(
                    db=self.database,
                    sv=self)

                asyncio.get_event_loop().run_until_complete(init_function())
                asyncio.get_event_loop().run_until_complete(
                    self.tasks.execute_interval_tasks(
                        db=self.database,
                        sv=self))

                asyncio.get_event_loop().run_forever()

            except KeyboardInterrupt:
                self.log('[SHUTDOWN]')

            finally:
                self.log('[CLEANUP-TASKS-STARTED]')
                self.tasks.execute_shutdown_tasks(
                    db=self.database,
                    sv=self)

                self.database.save()
                self.log('[CLEANUP-TASKS-COMPLETE]')
        else:
            self.log(f'[ERROR] -- {args.cmd} is not a valid option.')
