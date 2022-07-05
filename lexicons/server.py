import os
import asyncio
import orjson
from orjson import JSONDecodeError
from uuid import uuid4
import argparse

from IPython import embed
import websockets

from .utils import on_connect, on_disconnect, on_start, on_shutdown, on_log
from .channels import ChannelManager
from .models import ModelManager
from .signals import SignalManager
from .tasks import TaskManager
from .headers import HeaderManager
from .database import Database


class Server:
    '''
    # TODO - rewrite
    '''
    # TODO forget os.environ, user settings file. / Create default settings in package
    def __init__(
        self,
        protocol: str = os.environ.get('PROTOCOL', 'ws'),
        host: str = os.environ.get('HOST', 'localhost'),
        port: int = os.environ.get('PORT', 5000),
        debug: bool = os.environ.get('DEBUG', True),
        on_log=on_log,
        database: Database = None,
        data: str = os.environ.get('DATA', './'),
        trust: list[str, ...] = os.environ.get('TRUST', []),
        gate: callable = all,
        cache: dict = {},
        on_connect=on_connect,
        on_disconnect=on_disconnect,
        on_start=on_start,
        on_shutdown=on_shutdown,
        channels: ChannelManager = ChannelManager(),
        models: ModelManager = ModelManager(),
        signals: SignalManager = SignalManager(),
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
        self.signals = signals
        self.channels = channels
        self.trust = trust
        self.headers = headers
        self.gate = gate
        self.on_connect = on_connect
        self.on_disconnect = on_disconnect
        self.on_start = on_start
        self.on_shutdown = on_shutdown
        self.on_log = on_log
        self.commands = {
            'run': self.run_default(),
            'shell': self.run_shell,
            'migrate': self.run_migrations,
        }

    def run_default(self):
        return lambda: websockets.serve(self.handle, self.host, self.port)

    def run_shell(self):
        global db
        db = self.database
        db.audit_fields()
        global sv
        sv = self

        for model in self.models:
            exec(f'from {model.__module__} import {model.__name__}', globals())

        embed()

    def run_migrations(self):
        self.database.migrate()
        self.database.save()

    def check_if_trusted(self, websocket) -> bool:
        if websocket.remote_address[0] in self.trust or not self.trust:
            return True

        self.on_log(status='UNTRUSTED-SOURCE-DENIED', data={
            'address': websocket.remote_address,
        }, sv=self, db=self.database,
                 ws=websocket)
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
                    kwargs = orjson.loads(data_string.replace('\'', '\"'))
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
                    self.on_log(
                        status='HEADER-CHECK-FAILED',
                        data={
                            'header': header._name,
                            'kwargs': kwargs,
                        },
                        sv=self, db=self.database,
                        ws=websocket)
            except Exception as error:
                errors['Errors'].extend(error.args)
                if self.debug:
                    raise error

        if errors['Errors']:
            asyncio.ensure_future(websocket.send(orjson.dumps(errors)))

        return self.gate(header_results)

    def broadcast(self, payload: dict, channels: list):
        self.on_log(status='BROADCAST', data={
            'payload': payload,
            'channels': channels,
        }, sv=self, db=self.database)
        for channel_name in channels:
            if channel := self.channels[channel_name]:
                for subscriber_pk in channel.subscribers:
                    if subscriber_pk in self.clients.keys():
                        asyncio.ensure_future(self.clients[subscriber_pk].send(orjson.dumps(payload)))

            else:
                self.on_log(status='CHANNEL-NOT-FOUND', data={'channel': channel_name}, sv=self, db=self.database)

    async def register(self, websocket):
        self.on_log(status='REGISTER-NEW-CONNECTION', data={'address': websocket.remote_address}, sv=self,
                 db=self.database,
                 ws=websocket)
        self.clients[websocket.pk] = websocket

    async def unregister(self, websocket):
        self.on_log(status='UNREGISTER-CLOSE-CONNECTION', data={'address': websocket.remote_address}, sv=self,
                 db=self.database,
                 ws=websocket)
        del self.clients[websocket.pk]
        self.channels.unregister(websocket.pk)

    async def handle(self, websocket, host):
        self.on_log(status='HANDLE-CONNECTION', data={'address': websocket.remote_address}, sv=self, db=self.database,
                 ws=websocket)
        websocket.pk = str(uuid4())

        if self.check_if_trusted(websocket) and self.handle_headers(websocket.request_headers, websocket=websocket):
            self.on_connect(ws=websocket, sv=self, db=self.database)
            await self.register(websocket)
            try:
                async for payload in websocket:
                    response = []
                    channels = set()
                    errors = {'Errors': []}
                    incoming_signals = orjson.loads(payload)
                    if isinstance(incoming_signals, dict):
                        incoming_signals = [incoming_signals]

                    for incoming_signal in incoming_signals:
                        signal_name = next(iter(incoming_signal.keys()), None)
                        self.on_log(
                            status='SIGNAL',
                            data=incoming_signal,
                            sv=self,
                            ws=websocket,
                            db=self.database,
                        )
                        if signal := self.signals[signal_name]:
                            try:
                                data, signal_channels = signal.execute(
                                    ws=websocket,
                                    sv=self,
                                    db=self.database,
                                    **incoming_signal.get(signal_name))

                                response.append(data)
                                channels.update(signal_channels)
                            except Exception as error:
                                errors['Errors'].extend(error.args)
                                if self.debug:
                                    raise error

                        else:
                            await websocket.send(orjson.dumps([{'Errors': [f'No signal [{signal_name}]']}]))

                    if errors['Errors']:
                        response.append(errors)
                        channels.add(websocket.auth)

                    self.broadcast(response, list(channels))

            finally:
                self.on_disconnect(ws=websocket, sv=self, db=self.database)
                self.on_log(status='CONNECTION CLOSED', data=websocket.remote_address, sv=self, db=self.database,
                         ws=websocket)
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

        self.on_start(sv=self, db=self.database)

        if args.cmd == 'shell':
            self.commands.get('shell')()

        elif args.cmd == 'migrate':
            self.commands.get('migrate')()

        elif init_function := self.commands.get(args.cmd):
            try:
                self.on_log(status='STARTING', sv=self, db=self.database)
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
                self.on_log(status='SHUTDOWN', sv=self, db=self.database)

            finally:
                self.on_log(status='CLEANUP-TASKS-STARTED', sv=self, db=self.database)
                self.tasks.execute_shutdown_tasks(
                    db=self.database,
                    sv=self)

                self.on_log(status='CLEANUP-TASKS-COMPLETE', sv=self, db=self.database)

                self.on_shutdown(sv=self, db=self.database)
        else:
            self.on_log(status='ERROR', data={'arg': args.cmd}, sv=self, db=self.database)
