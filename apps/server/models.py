from models.models import Model
import pytz
from datetime import datetime
# from models.utils import to_snake


class ServerStatus(Model):
    pk: int = 0
    content: str = ''
    timestamp: str = str(pytz.timezone('UTC').localize(datetime.utcnow()))
    active: bool = True

    def on_create(self, db):
        now = str(pytz.timezone('UTC').localize(datetime.utcnow()))
        self.timestamp = now
        return super().on_create(db)


models = [ServerStatus]
