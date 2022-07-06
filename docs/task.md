# Task
A task is a object with an asynchronous execute method that triggers automatically given a certain amount of time or during a
defined server event.

### Types
- Startup
- Interval
- Shutdown


Examples:

```
from lexicons import Task


### load in data on start.
class LoadData(Task.Startup):
    async def execute(self, db=None, **kwargs):
	db.load()

### Periodically save data to disk.
class PeriodicSave(Task.Interval):
    def timer(self, **kwargs):
	return 60*60  # Seconds

    async def execute(self, db=None, **kwargs):
	db.save()


### Save data when server shuts down.
class SaveData(Task.Shutdown):
    async def execute(self, db=None, **kwargs):
	db.save()

```
