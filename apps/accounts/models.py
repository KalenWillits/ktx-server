from models.models import Model
from datetime import datetime, timedelta
from config.settings import settings
import pytz
from models.utils import encrypt
import secrets
from random import choice


class User(Model):
    username: str = ''

    @property
    def password(self) -> str:
        return self['password']

    @password.setter
    def password(self, new_password):
        self['password'] = encrypt(new_password)

class Permission(Model):
    type: str = ''
    model: str = ''

class Group(Model):
    title: str = ''
    permissions: set = {Permission}

class AuthorizationToken(Model):
    token: str = ''
    expiration: str = str(pytz.timezone(settings.server_timezone).localize(datetime.utcnow()))

    def on_create(self, db):
        self.token = secrets.token_hex()
        self.expiration = str(pytz.timezone(settings.server_timezone).localize(
            datetime.utcnow())+timedelta(minutes=settings.time_to_token_expiration))
        return super().on_create(db)

class RegistrationKey(Model):
    key: str = ''
    active: bool = True
    groups: set = {Group}
    permissions: set = {Permission}

    def on_create(self, db):
        self.key = ''.join([choice(settings.reg_key_char_set) for _ in range(settings.reg_key_len)])
        return super().on_create(db)

class Account(Model):
    key: int = RegistrationKey
    user: int = User
    token: int = AuthorizationToken
    permissions: set = {Permission}
    groups: set = {Group}
    active: bool = True


models = [User, AuthorizationToken, Account, Permission, Group, RegistrationKey]
