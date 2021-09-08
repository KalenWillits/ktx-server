from .account import Account
from .asset import Asset
from .authorization_token import AuthorizationToken
from .group import Group
from .permission import Permission
from .registration_key import RegistrationKey
from .status import Status
from .user import User
from models import ModelManager

MODELS = ModelManager([Account, Asset, AuthorizationToken, Group, Permission, RegistrationKey, Status, User])
