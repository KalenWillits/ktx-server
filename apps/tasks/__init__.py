from .create_admin_group import CreateAdminGroup
from .create_permissions import CreatePermissions
from .periodic_database_save import PeriodicDatabaseSave
from .purge_expired_tokens import PurgeExpiredTokens

from tasks import TaskManager

TASKS = TaskManager([CreateAdminGroup, CreatePermissions, PeriodicDatabaseSave,
                     PurgeExpiredTokens])

