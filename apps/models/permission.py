from models import Model
from .special_permission import SpecialPermission


class Permission(Model):
    model: str = ''
    type: str = ''
    special_permissions: int = {SpecialPermission}
