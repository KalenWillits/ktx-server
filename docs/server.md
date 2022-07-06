[<- Back](index.md)

# Server
The server is the main component and will manage the setup and instantiation of the database based on the set 
configuration. However, as a project scales it is more common to interact with the database component as that is where
the data is generally stored. 

It is entirely possible to forgo the use of the database component and instantiate a connector to a larger typical 
relational database. In this case, it is recommended to place the connector on the sv(Server) or db(Database) Component
as an attribute in a startup task or server hook.

Another possible configuration is to populated the database with only active session-based data and dump non-active
sessions. This would involve querying a large database via connector in a header or the on_connect hook and populating
session data from there. This could potentially slow login times but speed up application interaction.


### database, default None
see [Database](database.md)
If None, the database is instantiated automatically.


### data :  str or path, default './'
see [Database](database.md)


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

### channels : list of Channel objects, default []
See [Channel](channel.md)
### models : list of Model objects, default []
See [Model](model.md)
### signals : list of Signal objects, default []
See [Signal](signal.md)
### tasks : list of Task objects, default []
See [Task](task.md)
### headers : list of Header objects, default []
See [Header](header.md)
