# Lexicons
Lexicons is a stateless middleware websocket server framework written in Python designed to handle small and medium sized data 
sets. The relational database is powered by Pandas and lives in memory at run time. Only json data types are supported. 
By default, the server is stateless and data will need to be populated on each restart. However, runtime hooks such as 
on_start, on_connect, on_disconnect, and on_shutdown can be configured to change the behavior if needed. 

Intended use-cases are for live chat and notification services, real-time location data, and as a backend connector
for simulation data streams. The server can run completely stateless or interface with other frameworks via the 
extendable components that build out the application.


Read the [full documentation](https://github.com/KalenWillits/lexicons/blob/main/docs/index.md) for more details.

See a working [public chat room](https://github.com/KalenWillits/lexicons-example) example.

# Usage
## Quick Start

```
# main.py
from lexicons import Server, Signal, Channel


# Define a public channel to broadcast on.
class Public(Channel):
    pass


# When a new websocket connection is made, subscribe it to the public channel.
def on_connect(ws=None, sv=None, db=None):
    sv.channels['Public'].subscribe(ws.pk)


# Create an endpoint that will respond to the websocket request across the channel.
class GetData(Signal):
    def execute(self, ws=None, **kwargs):
        return self.response('Hello World!', ['Public'])



# Install components and instantiate the server application.
sv = Server(Public, GetData, on_connect=on_connect)

if __name__ == '__main__':
    sv.run()
```

## Start the server
`python main.py run`

## Run the signal's execute function from a websocket client.
Send the following payload as a json string:
<- `{"GetData": {}}`

If configured correctly, the server will return on all connections subscribed to public:
-> `{"GetData": "Hello World!"}`

## Drop into the shell
`python main.py shell`
global variables db and sv for database and server.




### Supported Types:
	- str
	- int
	- float
	- bool
	- list
	- set
