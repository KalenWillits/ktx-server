from models.utils import hydrate


def get_snapshot(subscription, db):
    """
    Takes a websockets subscriptions and compiles them as a dictionary to represent
    server state.
    """
    snapshot = dict()
    for model, pks in subscription.items():
        df = db[model].isin({"pk": pks})
        snapshot[model] = hydrate(model, df, db)

    return snapshot

