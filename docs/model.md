[<- Back](index.md)

# Model
Models are objects that describe a the schema of a table in the database. 
Models have a primary key uuid as a string shortened to `pk`.

Any method, attribute, or type hint without a leading underscore will be treated as a field to the database. This is to include
properties as well as attributes. On non-exempt fields type hints are required. 

Underscore fields are exempt and can be used to write model logic.


An example of a user model could look like:
```
from lexicons import Model


class User(Model):
    first_name: str
    last_name: str
    is_online: bool = True


    _num_logins = 0

    @property
    def increment_logins(self) -> int:
	self._num_logins += 1
	return self._num_logins
```
