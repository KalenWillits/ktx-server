# lexicons
Backend Websocket server for simple db access and rapid development. 
**This project is currently in the prototype phase and the documentation is incomplete.**


# Getting Started

```
# main.py

from lexicons import Database, Server, ModelManager, SignalManager, TaskManager, ChannelManager, HeaderManager

headers = HeaderManager()
models = ModelManager()
signals = SignalManager()
tasks = TaskManager()
channels = ChannelManager()

server = Server(protocol='ws', host='localhost', port=5000, models=models, tasks=tasks, signals=signals, 
		headers=headers, channels=channels, data="data/", trust=[])

if __name__ == "__main__":
    server.run()
```

# Usage
`python main.py run`


# Abstract 
lexicons is a websocket server framework written in Python designed to handle small and medium sized data sets. 
The database is powered by Pandas and lives in memory at run time. When a server shutdown event occurs, the data is 
written to disk in csv files. One csv for each DataFrame. Server interaction is made from four building blocks. Models, 
signals, tasks, and channels. 
	- Models are class representations of tables in the database. Class names define the name of the table, and
	  static attributes define each field. fields can also be defined by properties by using the property method.

	- Models are class representations of tables in the database. Class names define the name of the table, and
	  static attributes define each field. fields can also be defined by properties by using the property method.
	  
	- Signals are how clients can interact with the server. Each signal will have an *execute* method. This method
	  will run when a registered websocket client calls it by name. The signal will return a reponse payload and
	  a list of channels to broadcast on. If there are no channels to broadcast on there will be no response
	  returned. Signals are also required to allow clients to subscribe to channels.
	  
	- Tasks are automated server behaviors that can run at startup, shutdown, and in defined intervals. Intervals
	  can be defined dynammically by using the *set* method. This method should return the interval in seconds
	  as an integer. Task *execute* methods are asyncronous.
	  
	- Channels are the control gate for clients receiving information from an signal response. At least one channel
 	  and one subscribe signal is required for server communication to occur. Clients can be in as many or no 
	  channels, however each client can only be in any channel once. 

### Special Notes:
	- Authentication is handled in the connection headers by defining headers and gate arguments to Server.
	  headers is a list of functions that accept **kwargs and return a boolean value. The gate argument is a 
	  function that accepts an iterable and returns a boolean value. By default headers are an empty list and
	  the gate is an `all()` function. When header data is received, it is sent in the format: 
	  `HEADER_NAME:JSON_STRING`.
	- Interaction with the database requires some knowledge with pandas. However, there are some helper functions
	  for most simple operations. The database is passed as `db` and is a base class with each table as an 
	  attribute. Each table is a pandas DataFrame.
	
	  
	

### Supported Types:
	- str
	- int
	- float
	- bool
	- list
	- set


# Examples

### Headers
```
import orjson
import asyncio
from datetime import datetime

from packages.lexicons import Header
from packages.lexicons.utils import encrypt


class Login(Header):
    def execute(self, email=None, password=None, db=None, ws=None, sv=None, **kwargs):
        if not (email and password):
            return False
        password = encrypt(password)
        user = db.get('User', email=email, password=password)

        if user:
	    ws.auth = user.pk
            return True

        asyncio.ensure_future(ws.send(orjson.dumps([{'Errors': ['Authentication failed']}])))

        return False
```

### Models
```
from packages.lexicons import Model
from packages.lexicons.utils import encrypt


class User(Model):
    email: str

    @property
    def password(self) -> str:
        if hasattr(self, '_password'):
            return self._password
        else:
            return None

    @password.setter
    def password(self, raw_password: str):
        setattr(self, '_password', encrypt(raw_password))


class ChatMessage(Model):
    author: User
    channel: str
    content: str

```

### Channels
```
from packages.lexicons import Channel


class Public(Channel):
    pass

```

### Signals
```
from datetime import datetime

from packages.lexicons import Signal


class CreateChatMessage(Signal):
    def execute(self, channel=None, content=None, db=None, ws=None, **kwargs):
        timestamp = datetime.now().timestamp()
        message = db.create('ChatMessage', channel=channel, content=content, author=ws.auth,
                            timestamp=timestamp)
	
        return self.response(message._to_dict(), [channel])
```

### Tasks
```
from packages.leviathan import Task


class OnShutdown(Task.Shutdown):
    priority = 0

    def execute(self, db=None, **kwargs):
	pass
```

### Installing components to server
```
from lexicons import Database, Server, ModelManager, SignalManager, TaskManager, ChannelManager, HeaderManager

headers = HeaderManager(Login)
models = ModelManager(User, ChatMessage)
signals = SignalManager(CreateChatMessage)
tasks = TaskManager(OnShutdown)
channels = ChannelManager(Public)

server = Server(protocol='ws', host='localhost', port=5000, models=models, tasks=tasks, signals=signals, 
		headers=headers, channels=channels, data="data/", trust=[])

if __name__ == "__main__":
    server.run()

```
