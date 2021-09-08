from apps.models import RegistrationKey
from actions import Action

class CreateAdminRegKey(Action):
    key = "create-admin-reg-key"

    def execute(*args, **kwargs):
        db = kwargs.get("db")
        if db.has('permission'):
            admin_group_df = db.filter('group', title='Admin')
            if not admin_group_df.empty:
                admin_group_pk = admin_group_df.iloc[0].pk
                reg_key = RegistrationKey(groups={admin_group_pk})
                df = db.add(reg_key)
                print(f'Registration Key: {df.iloc[0].key}')
                return {"key": reg_key.key}
            raise Exception('No table [group].')
        raise Exception('No table [permission].')

