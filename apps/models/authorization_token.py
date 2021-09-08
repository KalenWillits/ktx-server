from models import Model
import pytz
import secrets
from datetime import timedelta, datetime
import settings

class AuthorizationToken(Model):
    token: str = ''
    expiration: str = str(pytz.timezone(settings.server_timezone).localize(datetime.utcnow()))

    def on_create(self, db):
        self.token = secrets.token_hex()
        self.expiration = str(pytz.timezone(settings.server_timezone).localize(
            datetime.utcnow())+timedelta(minutes=settings.time_to_token_expiration))
        return super().on_create(db)
