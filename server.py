import asyncio
import json
import websockets
import argparse

from websockets.exceptions import ConnectionClosedError

from database import db
from register import ACTIONS, MODELS, TASKS
from utils import get_snapshot, encrypt


class Server:
    def __init__(
        self,
        address: str = "localhost",
        port: int = 5000,
        debug: bool = True,
        db=None,
        tasks=None,
        models=None,
        actions=None,
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
        self.db = db
        self.tasks = tasks
        self.models = models
        self.actions = actions

    def log(self, *args):
        if self.debug:
            print(*args)

    async def check_credentials(self, username, password) -> bool:
        user_df = db.filter('user', username=username, password=encrypt(password))
        if not user_df.empty:
            user_pk = user_df.pk.iloc[0]
            account_df = db.filter('account', user=user_pk)
            if not account_df.empty:
                return True
        return False

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
        return lambda: websockets.serve(
            self.handle,
            "localhost",
            self.port,
            create_protocol=websockets.basic_auth_protocol_factory(
                realm="leviathan",
                check_credentials=self.check_credentials))

    def run_shell(self):
        from IPython import embed

        for model in MODELS:
            exec(f'from {model.__module__} import {model.__name__}', globals())

        import utils

        return lambda: embed()

    def state_event(self, websocket):
        self.log("[NOTIFY EVENT]")
        snapshot = get_snapshot(self.clients[websocket], db)
        return json.dumps(snapshot)

    async def notify_state(self, response):
        self.log("[NOTIFY STATE]")
        if self.clients:
            payload = json.dumps(response)
            for client in self.clients.keys():
                await client.send(payload)

    async def register(self, websocket):
        self.log("[REGISTER]")
        self.clients[websocket] = dict()

    async def unregister(self, websocket):
        self.log("[UNREGISTER]")
        del self.clients[websocket]

    async def handle(self, websocket, address):
        await self.register(websocket)
        try:
            await websocket.send(self.state_event(websocket))
            async for payload in websocket:
                data = json.loads(payload)
                for action_name in data.keys():
                    if response := ACTIONS[action_name].execute(
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
                self.log("[STARTING]", self.address)
                db.load()
                TASKS.execute_startup_tasks(db=db, MODELS=MODELS, server=self)

                asyncio.get_event_loop().run_until_complete(init_function())
                asyncio.get_event_loop().run_until_complete(TASKS.execute_periodic_tasks(db=db, models=MODELS,
                                                                                         server=self))
                asyncio.get_event_loop().run_forever()
            except KeyboardInterrupt:
                self.log("[SHUTDOWN]")
            finally:
                self.log("[CLEANUP-TASKS-STARTED]")
                TASKS.execute_shutdown_tasks(db=db, MODELS=MODELS, server=self)
                db.save()
                self.log("[CLEANUP-TASKS-COMPLETE]")
        else:
            self.log(f"[ERROR] -- {args.cmd} is not a valid option.")
