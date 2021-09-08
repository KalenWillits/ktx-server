from models import Model
from .group import Group
from .permission import Permission
from random import choice
import settings

class RegistrationKey(Model):
    key: str = ''
    active: bool = True
    groups: set = {Group}
    permissions: set = {Permission}

    def on_create(self, db):
        self.key = ''.join([choice(settings.reg_key_char_set) for _ in range(settings.reg_key_len)])
        return super().on_create(db)
