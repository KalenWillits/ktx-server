from apps.models import Account, Asset, AuthorizationToken, Group, Permission, RegistrationKey, Status, User
from apps.tasks import CreateAdminGroup, CreatePermissions, PeriodicDatabaseSave, PurgeExpiredTokens
from apps.actions import CreateAdminRegKey, Login, Register

from tasks import TaskManager
from actions import ActionManager
from models import ModelManager


MODELS = ModelManager([Account, Asset, AuthorizationToken, Group, Permission, RegistrationKey, Status, User])

TASKS = TaskManager([CreateAdminGroup, CreatePermissions, PeriodicDatabaseSave, PurgeExpiredTokens])

ACTIONS = ActionManager([Login, CreateAdminRegKey, Register])
