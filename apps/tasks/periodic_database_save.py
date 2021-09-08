import asyncio
from tasks import Task
import settings

class PeriodicDatabaseSave(Task):
    type = "periodic"

    async def execute(db):
        await asyncio.sleep(settings.database_save_interval)
        db.save()

