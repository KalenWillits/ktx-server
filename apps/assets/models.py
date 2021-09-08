from models.models import Model
from apps.assets.utils import Asset

class Avatar(Asset):
    title: str = ''

class Icon(Asset):
    title: str = ''

class Map(Asset):
    title: str = ''


models = [Avatar, Icon, Map]
