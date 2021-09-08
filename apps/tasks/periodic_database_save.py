import asyncio
from tasks import Task
import settings

class PeriodicDatabaseSave(Task):
    type = "periodic"

    async def execute(*args, **kwargs):
        db = kwargs.get("db")
        await asyncio.sleep(settings.database_save_interval)
        db.save()

