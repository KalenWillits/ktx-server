from models.models import Model
from config.settings import settings
from datetime import datetime
import pytz
from apps.accounts.models import Account
from apps.game.models import Scenario, Character


# class TurnController(Model):


class Room(Model):
    title: str = ''
    characters: set = {Character}
    players: set = {Account}
    ready: set = {Account}
    scenario: int = Scenario
    password: str = ''

class Chat(Model):
    author: int = Character
    room: int = Room
    content: str = ''
    timestamp: str = str(pytz.timezone(settings.server_timezone).localize(datetime.utcnow()))

    def on_create(self, db):
        now = str(pytz.timezone(settings.server_timezone).localize(datetime.utcnow()))
        self.timestamp = now
        return super().on_create(db)


models = [Chat, Room]



