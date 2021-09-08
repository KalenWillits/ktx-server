from .create_admin_reg_key import CreateAdminRegKey
from .login import Login
from actions import ActionManager

ACTIONS = ActionManager([CreateAdminRegKey, Login])
