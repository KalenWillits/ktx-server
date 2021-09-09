from tasks import Task
import settings
from utils import token_is_valid, hydrate
from apps.models import Account, AuthorizationToken

class Logout(Task):
    key = "logout"

    def execute(*args, **kwargs):
        db = kwargs.get("db")
        token = args[1].context.get('request')._headers.get('bearer', '')

        if token_is_valid(db, token):
            account_pk = kwargs.get('pk')
            account = db.get(Account, account_pk)
            db.change(account, pk=account_pk, token=None)
            token_df = db.authorization_token[db.authorization_token.token == token]
            if not settings.token_required:
                raise Exception('Unable to confirm response when "settings.token_required" is set to "False".')
            if not token_df.empty:
                token_pk = token_df.iloc[0].pk
                instance = db.get(AuthorizationToken, token_pk)
                db.drop(instance, **token_df.to_dict())
                return next(hydrate(AuthorizationToken, instance.df(), db))

            raise Exception('Unable to logout.')

        raise Exception('Access denied.')
