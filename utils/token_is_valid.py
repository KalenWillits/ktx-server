import pandas as pd
from datetime import datetime
import pytz


def token_is_valid(db, token):
    if not db.has('authorization_token'):
        return None

    token_df = db.authorization_token[db.authorization_token.token == token]
    if token_df.empty:
        return False

    token_expiration = pd.to_datetime(token_df.expiration.iloc[0])
    now = pytz.timezone('UTC').localize(datetime.utcnow())
    if token_expiration > now:
        return True
    else:
        return False
