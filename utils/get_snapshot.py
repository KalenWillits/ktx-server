from models.utils import hydrate


def get_snapshot(subscription, db):
    snapshot = dict()
    for model, pks in subscription.items():
        df = db[model].isin({"pk": pks})
        snapshot[model] = hydrate(model, df, db)

    return snapshot

