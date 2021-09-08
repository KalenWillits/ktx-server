from tasks import Task
from utils import hydrate
from apps.models import RegistrationKey, User, Account

class Register(Task):
    key = "register"

    def execute(*args, **kwargs):
        db = kwargs.get("db")
        key_df = db.filter('registration_key', key=kwargs.get('key', ''))
        if not key_df.empty:
            key_pk = key_df.iloc[0].pk
            key = db.get(RegistrationKey, key_pk)
            if key.active:
                user = User(username=kwargs.get('username', ''), password=kwargs.get('password', ''))
                db.add(user)
                account = Account(user=user.pk, key=key.pk, groups=key.groups, permissions=key.permissions)
                db.add(account)
                db.change(key, active=False, pk=key_pk)
                account_df = db.filter('account', user=user.pk)

            return next(hydrate(Account, account_df, db))
        raise Exception('Invalid registration key.')
