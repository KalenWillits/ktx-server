# Server

Entry point of the application.

## Parameters

### protocol : {'ws', 'wss'}, default 'ws'
representing the websocket protocol. Use either `ws` or `wss`.

### host : str, default 'localhost'
The hostname or ip address from where the broadcast is coming from.

### port : int, default 5000
Port number that connections are made on.

### debug : bool, default True
By default, logs and errors only execute in debug mode. Default value is `True`.

### trust: list-like, default `['*']`
List of IP addresses that can be accept new connections. If `*` is in this list, any connection can be accepted. Default value is `['*']`.


### gate: function accepting an array of bools
Function handling header results. Header results comeback as a list of booleans, the default gate of `any` will check
if all values are `True` before allowing a new connection.

### on_connect: function accepting ws, sv, and db keyword arguments
```
def on_connect(ws: Websocket = None, sv: Server = None, db: Database = None):
	pass
```
- ws: The active websocket
- sv: The instantiated Server
- db: The instantiated Database
Executes when a new websocket connection is accepted.


### on_disconnect: function accepting ws, sv, and db keyword arguments
```
def on_disconnect(ws: Websocket = None, sv: Server = None, db: Database = None):
	pass
```
- ws: The active websocket
- sv: The instantiated Server
- db: The instantiated Database
Executes when a websocket connection in unregistered.


### on_start : function accepting sv, and db keyword arguments
```
def on_start(sv: Server = None, db: Database = None):
	pass
```
- sv: The instantiated Server
- db: The instantiated Database
Executes when the server starts.
Use this to load in database connections or load the default local storage. 

### on_shutdown : function accepting sv, and db keyword arguments
```
def on_shutdown(sv: Server = None, db: Database = None):
	pass
```
- sv: The instantiated Server
- db: The instantiated Database
Executes when the server shuts down.
Use this resolve database connections or save the current data to disk.

### Channels : list of Channels










