# leviathan
Backend Websocket server for simple db access using websocket connects for top performance. 


### Getting Started

```
# main.py

from leviathan import Database, Server, ModelManager, ActionManager, TaskManager, ChannelManager

models = ModelManager()
actions = ActionManager()
tasks = TaskManager()
channels = ChannelManager()

merver = Server(models=models, tasks=tasks, actions=actions, path="data/")

if __name__ == "__main__":
    server.run()
```
Usage: `python main.py run`


### Abstract 
Leviathan is a websocket server framework written in Python designed to handle small and medium sized data sets. 
The database is powered by Pandas and lives in memory at run time. When a server shutdown event occurs, the data is 
written to disk in csv files. One csv for each DataFrame. Server interaction is made from four building blocks. Models, 
actions, tasks, and channels. 

	- Models are class representations of tables in the database. Class names define the name of the table, and
	  static attributes define each field. fields can also be defined by properties by using the property method.
	  
	- Actions are how clients can interact with the server. Each action will have an *execute* method. This method
	  will run when a registered websocket client calls it by name. The action will return a reponse payload and
	  a list of channels to broadcast on. If there are no channels to broadcast on there will be no response
	  returned. Actions are also required to allow clients to subscribe to channels.
	  
	- Tasks are automated server behaviors that can run at startup, shutdown, and in defined intervals. Intervals
	  can be defined dynammically by using the *set* method. This method should return the interval in seconds
	  as an integer. Task *execute* methods are asyncronous.
	  
	- Channels are the control gate for clients recieving information from an action response. At least one channel
 	  and one subscribe action is required for server communication to occur. Clients can be in as many or no 
	  channels, however each client can only be in any channel once. 

### Special Notes:
	- Authentication is handled in the connection headers by defining headers and gate arguments to Server.
	  headers is a list of functions that accept **kwargs and return a boolean value. The gate argument is a 
	  function that accepts an iterable and returns a boolean value. By default headers are an empty list and
	  the gate is an `all()` function. When header data is recieved, it is sent in the format: 
	  `HEADER_NAME:JSON_STRING`.
	  
	- Interaction with the database requires some knowledge with pandas. However, there are some helper functions
	  for most simple operations. The database is passed as `db` and is a base class with each table as an 
	  attribute. Each table is a pandas DataFrame.

