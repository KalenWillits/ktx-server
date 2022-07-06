[<- Back](index.md)


# Header
A header is an object that runs the execute method before a websocket connection is established.
The execute method returns a boolean value and is passed to the server.gate function. An example of a login header is:

kwargs is required at the end of any execute method to catch any additional parameters being sent to the endpoint

```
from lexicons import Header
from lexicons.utils import encrypt

class Login(Header):
    def execute(ws=None, db=None, email=None, **kwargs):
	user = db.get('User', email=email)
	
	if user:
		# Setting auth as user pk for session-based authentication.
		ws.auth = user.pk 
		return True
	
	return False
```
