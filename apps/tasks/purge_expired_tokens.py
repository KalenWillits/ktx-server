from tasks import Task
import settings
import asyncio
import pytz
import pandas as pd
from datetime import datetime

class PurgeExpiredTokens(Task):
    type = "perodic"

    async def execute(*args, **kwargs):
        db = kwargs.get("db")
        if db.has('athorization_token'):
            await asyncio.sleep(settings.time_to_token_expiration*60*4)
            now = pytz.timezone(settings.server_timezone).localize(datetime.utcnow())
            expired_tokens_filter = pd.to_datetime(db.authorization_token.expiration) < now
            expired_token_indexes = db.authorization_token[expired_tokens_filter].indexes
            db.authorization_token = db.authorization_token.drop(expired_token_indexes)

            db.save()

