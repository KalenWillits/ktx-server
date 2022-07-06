[<- Back](index.md)


# Signal
A signal is a websocket endpoint with a execute method. The execute method returns a response object that is serialized
into a json object and sent across all selected channels. The syntax looks like:

kwargs is required at the end of any execute method to catch any additional parameters being sent to the endpoint

```
from lexicons import Signal


class CreateChatMessage(Signal):
    def execute(db=None, ws=None, message=None, **kwargs):
	user = db.get('User', ws.auth)
	db.create('ChatMessage', body=message, author=user.pk)
	payload = db.hydrate('ChatMessage', db.query('ChatMessage'))
	return self.response(payload, ['Public'])
```
