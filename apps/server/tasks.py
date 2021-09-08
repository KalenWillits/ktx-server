from tasks.tasks import Task
import asyncio 
from config.settings import settings
from database.database import db

class PeriodicDatabaseSave(Task):
    async def execute(self):
        '''
        Writes the database to disk as a .pkl file after a interval of time.
        '''
        await asyncio.sleep(settings.database_save_interval)
        db.save()

class SaveDatabaseOnShutdown(Task):
    def execute(self):
        db.save()


tasks = [PeriodicDatabaseSave('loop'), SaveDatabaseOnShutdown('shutdown')]
