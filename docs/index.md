# Lexicons | Documentation

**This project is currently in the prototype phase and the documentation is considered a draft**

Lexicons is a stateless websocket server framework written in Python designed to handle in-memory small and medium 
sized data sets. The relational database is powered by Pandas and lives in memory at run time. Only json data types are 
supported. By default, the server is stateless and data will need to be populated on each restart. However, runtime 
hooks such as on_start, on_connect, on_disconnect, and on_shutdown can be configured to change the behavior if needed. 

Intended use-cases are for live chat and notification services, real-time location data, and as a backend connector
for online multiplayer games. The server can run completely stateless or interface with other frameworks via the 
extendable components that build out the application.

# Components
The server is the main component and will manage the setup and instantiation of the database based on the set 
configuration. However, as a project scales it is more common to interact with the database component as that is where
the data is generally stored. 

It is entirely possible to forgo the use of the database component and instantiate a connector to a larger typical 
relational database. In this case, it is recommended to place the connector on the sv(Server) or db(Database) Component
as an attribute in a startup task or server hook.

[Server](server.md)
The server is the main object of which all other objects are built off of. This acts as the application node and handles
runtime logic. 

[Database](database.md)
The database object handles in-memory storage of the DataFrames, enforces model typing, and foreign key relationships.




### Component commonalities
Although building out a Lexicons server usually consists of interacting with the below seven different components, 
there are some commonalities and jargon that should be addressed before moving on.

### def execute(`**kwargs`)
The execute method appears on headers, signals, and tasks. Tasks carry an asynchronous version. The execute method must
have a kwargs argument to capture stray and unused keyword arguments that are conditionally passed to the method. 
Depending on the component, the execute method will capture at least `sv` and `db` keyword arguments. Signals and 
headers will also consistently capture `ws` a keyword argument.

### sv : (Server)
The shorthand variable for server. Passed as a key word argument to all execute methods.

### db : (Database)
The shorthand for the database model passed as a key word argument to all execute methods.

### ws : (Websocket)
The shorthand variable for websocket. Passed as a keyword argument to header and signal execute methods.

### Installing a component
Installing a component on the server object means to pass it as a list to the corresponding kwarg during instantiation. 
A manager object will be created to handle the management of the objects within the server from there.

For example, to install a `User` model on the server:
```
from lexicons import Server

sv = Server(User)
```

Depending on your project architecture, you may want to categorize your component lists manually.
In this case, you could install your `User` component like this:

```
from lexicons import Server

sv = Server(models=[User])
```


[Header](header.md)
- Headers handle security checks and act as one-way endpoints.
headers are a list of objects with an execute method and returns a boolean value. The gate argument is a 
function that accepts an iterable and returns a boolean value. By default headers are an empty list and
the gate is an `all()` function. When header data is received, it is sent in the format: 
`HEADER_NAME:JSON_STRING`.

[Model](model.md)
- Models are class representations of tables in the database. Class names define the name of the table, and
static attributes define each field. fields can also be defined by properties by using the property method.

[Channel](channel.md)
- Channels are the control gate for clients receiving information from an signal response. At least one channel
and one subscribe signal is required for server communication to occur. Clients can be in as many or no 


[Signal](signal.md)
- Signals are how clients can interact with the server. Each signal will have an *execute* method. This method
will run when a registered websocket client calls it by name. The signal will return a reponse payload and
a list of channels to broadcast on. If there are no channels to broadcast on there will be no response
returned. Signals are also required to allow clients to subscribe to channels.


[Task](task.md)
- Tasks are asynchronous functions that can be scheduled during runtime. There are tree types of tasks each with their 
own asynchronous execute method. Startup, Interval, and Shutdown. Interval tasks require a "timer" method to also be
overwritten. The timer method returns the interval in seconds between execute method executions.



# TODO 
- [] Complete base documentation
- [] Reverse foreign key lookups
- [] Write use-case examples
- [] Create script for starting a new project
- [] Create frontend websocket client for testing interaction
