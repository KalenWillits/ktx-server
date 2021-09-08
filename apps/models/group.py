from models import Model
from .permission import Permission

class Group(Model):
    title: str = ''
    permissions: set = {Permission}
