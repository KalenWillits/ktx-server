from models import Model
from .registration_key import RegistrationKey
from .authorization_token import AuthorizationToken
from .group import Group
from .permission import Permission
from .user import User


class Account(Model):
    key: int = RegistrationKey
    user: int = User
    token: int = AuthorizationToken
    permissions: set = {Permission}
    groups: set = {Group}
    active: bool = True
