from models.utils import to_snake
from apps.accounts.models import Permission, Group, User
from tasks.tasks import Task
from models.register import models
from database.database import db
import pytz
from datetime import datetime
from config import settings
import asyncio
import pandas as pd


class CreatePermissions(Task):
    def execute(self):
        permission_types = ('create', 'read', 'update', 'delete')
        for model in models:
            model_name = to_snake(model.__name__)
            if db.has('permission'):
                if db.has('permission', column='model', value=model_name):
                    continue

            for permission_type in permission_types:
                permission = Permission(type=permission_type, model=model_name)
                db.add(permission)

class CreateAdminGroup(Task):
    def execute(self):
        if db.has('permission'):
            all_permissions = set(db.permission.pk.values)

            if db.has('group'):
                if db.has('group', column='title', value='Admin'):
                    group_pk = db.filter('group', title='Admin').iloc[0].pk
                    instance = db.get(Group, group_pk)
                    if hasattr(instance, 'permissions'):
                        if set(instance.permissions).difference(all_permissions):
                            return
                        else:
                            db.change(instance, pk=group_pk, permissions=all_permissions)
                            return

            admin_user_group = Group(title='Admin', permissions=all_permissions)

            db.add(admin_user_group)

class PurgeExpiredTokens(Task):
    async def execute(self):
        if db.has('athorization_token'):
            await asyncio.sleep(settings.time_to_token_expiration*60*4)
            now = pytz.timezone(settings.server_timezone).localize(datetime.utcnow())
            expired_tokens_filter = pd.to_datetime(db.authorization_token.expiration) < now
            expired_token_indexes = db.authorization_token[expired_tokens_filter].indexes
            db.authorization_token = db.authorization_token.drop(expired_token_indexes)

            db.save()


tasks = [CreatePermissions('startup'), CreateAdminGroup('startup'),
         PurgeExpiredTokens('loop')]
