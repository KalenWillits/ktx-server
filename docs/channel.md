# Channel

## Parameters

### name : str, default None
name and accessor of channel. If none, the class name is used instead.

### subscribers : set, default {}
Default set of subscriber websockets. 


## Methods

### subscribe(websocket_pk: str)
Adds a connection to the broadcast list.

### unsubscribe(websocket_pk: str)
Removes a connection from the broadcast list.

