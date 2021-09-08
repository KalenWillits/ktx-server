from apps.accounts.models import RegistrationKey, Permission
from database.database import db
from commands.commands import Command

class CreateAdminRegKey(Command):
    def execute(self, *args, **kwargs):
        if db.has('permission'):
            admin_group_df = db.filter('group', title='Admin')
            if not admin_group_df.empty:
                admin_group_pk = admin_group_df.iloc[0].pk
                reg_key = RegistrationKey(groups={admin_group_pk})
                df = db.add(reg_key)
                print(f'Registration Key: {df.iloc[0].key}')
                db.save()
                return
            raise Exception('No table [group].')
        raise Exception('No table [permission].')


commands = [CreateAdminRegKey()]
