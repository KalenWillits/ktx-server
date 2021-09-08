from actions.actions import Action
from apps.models.account import Account
from apps.models.authorization_token import AuthorizationToken
from models.utils import encrypt
from models.utils import hydrate

class Login(Action):
    def run(*args, **kwargs):
        websocket = kwargs.get("websocket")
        server = kwargs.get("server")
        db = kwargs.get("db")
        if (username := kwargs.get("username")) and (password := encrypt(kwargs.get("password"))):
            user_df = db.filter('user', username=username, password=password)
            if not user_df.empty:
                user_pk = user_df.pk.iloc[0]
                account_df = db.filter('account', user=user_pk)
                if not account_df.empty:
                    account_pk = account_df.pk.iloc[0]
                    token = AuthorizationToken()
                    db.add(token)
                    token_df = db.filter('authorization_token', token=token.token)
                    server.subscribe(websocket, model=Account, pks={account_pk})
                    if not token_df.empty:
                        token_pk = token_df.pk.iloc[0]
                        account = Account(**account_df.iloc[0].to_dict())
                        db.change(account, pk=account_pk, token=token_pk)
                        account_df_with_token = db.filter('account', user=user_pk)
                        if not account_df_with_token.empty:
                            return next(hydrate(Account, account_df_with_token, db))

            raise Exception('Access denied.')



