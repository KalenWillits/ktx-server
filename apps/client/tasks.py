from tasks.tasks import Task
from database.database import db
from apps.client.models import Room

class CreateGeneralRoom(Task):
    def execute(self):
        existing_df = db.filter('room', title='General')
        if existing_df.empty:
            general_room = Room(title='General')
            db.add(general_room, skip_on_create=True)


tasks = [CreateGeneralRoom('startup')]
