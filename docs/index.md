# Contents
[Server](server.md)
The server is the main object of which all other objects are built off of. This acts as the application node and handles
runtime logic. 

[Database](database.md)
The database object handles in-memory storage of the DataFrames. 

[Header](header.md)
Extendable functions that execute logic before a websocket connection is registered.

[Model](model.md)
Models are descriptions of DataFrames types and fields that may contain custom logic.

[Channel](channel.md)
Channels are named instances in which websockets and subscribe to.

[Signal](signal.md)
Signals are endpoints in which incoming data can be accepted and returned to subscribed channels.

[Task](task.md)
Tasks are asynchronous functions that can be scheduled during runtime.
