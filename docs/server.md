# Server
## Parameters
- protocol: string -> representing the websocket protocol. Use either `ws` or `wss`.
- host: string -> Host address to make available. Default value is `localhost`.
- port: integer -> Port number to broadcast on. Default value is `5000`.
- debug: boolean -> By default, logs and errors only execute in debug mode. Default value is `True`.
- trust: list of strings -> List of IP addresses that can be accept new connections. If `*` is in this list, any 
connection can be accepted. Default value is `['*']`.
- gate: function -> How to check header results. Header results comeback as a list of booleans, the default gate of `any` will check
if all values are `True` before allowing a new connection.
