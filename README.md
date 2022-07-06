# lexicons
Backend Websocket server for simple db access and rapid development. 
**This project is currently in the prototype phase and the documentation is incomplete.**

Read the [full documentation](https://github.com/KalenWillits/lexicons/blob/main/docs/index.md) for more details.


# Quick Start

```
# main.py
from lexicons import Server, Signal, Channel


class Public(Channel):
    pass


def on_connect(ws=None, sv=None, db=None):
    sv.channels['Public'].subscribe(ws.pk)


class GetData(Signal):
    def execute(self, ws=None, **kwargs):
        return self.response('Hello World!', ['Public'])


server = Server(
        signals=[GetData],
        channels=[Public],
        on_connect=on_connect,
    )

if __name__ == '__main__':
    server.run()
```

# Usage
## Start the server
`python main.py run`

## Drop into the shell
`python main.py shell`
global variables db and sv for database and server.


# Abstract 
Lexicons is a stateless websocket server framework written in Python designed to handle small and medium sized data 
sets. The relational database is powered by Pandas and lives in memory at run time. Only json data types are supported. 
By default, the server is stateless and data will need to be populated on each restart. However, runtime hooks such as 
on_start, on_connect, on_disconnect, and on_shutdown can be configured to change the behavior if needed.


Server interaction is made from four building blocks. Models, 
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

	- Headers handle security checks and act as one-way endpoints.
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



# TODO 
- [] Complete base documentation
- [] Reverse foreign key lookups
- [] Write use-case examples
- [] Create script for starting a new project
- [] Create frontend websocket client for testing interaction
