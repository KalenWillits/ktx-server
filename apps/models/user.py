from models import Model
from models.utils import encrypt

class User(Model):
    username: str = ''

    @property
    def password(self) -> str:
        return self['password']

    @password.setter
    def password(self, new_password):
        self['password'] = encrypt(new_password)
