# leviathan
Backend Websocket server for simple db access using websocket connects for top performance. 


### Getting Started

```
# main.py

from leviathan import Database, Server, ModelManager, ActionManager, TaskManager

models = ModelManager([])
actions = ActionManager([])
tasks = TaskManager([])

db = Database(path="data/", models=models)

server = Server(models=models, tasks=tasks, actions=actions, db=db)

if __name__ == "__main__":
    server.run()
```
Usage: `python main.py dev`

```
# main.py

from leviathan import Database, Server, ModelManager, ActionManager, TaskManager
from leviathan import Model, Action, Task

# Example Model
class User(Model):
	username: str = ""
	password: str = ""
	

class Token(Model): 
	user: int = User  # FK relationship
	key: str = "" 

class Lobby(Model):
	name: str = ""
	users: int = {User}  # Unique M2M field (user a list for non-unique)
	


models = ModelManager([])
actions = ActionManager([])
tasks = TaskManager([])

db = Database(path="data/", models=models)

server = Server(models=models, tasks=tasks, actions=actions, db=db)

if __name__ == "__main__":
    server.run()

```

