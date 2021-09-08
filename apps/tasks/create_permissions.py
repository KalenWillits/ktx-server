from tasks import Task
from register import MODELS
from utils import to_snake

class CreatePermissions(Task):
    type = "startup"

    def run(*args, **kwargs):
        db = kwargs.get("db")
        permission_types = ('create', 'read', 'update', 'delete')
        for model in MODELS:
            model_name = to_snake(model.__name__)
            if db.has('permission'):
                if db.has('permission', column='model', value=model_name):
                    continue

            for permission_type in permission_types:
                permission = MODELS.Permission(type=permission_type, model=model_name)
                db.add(permission)
