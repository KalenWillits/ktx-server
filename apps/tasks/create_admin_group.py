from tasks import Task
from register import MODELS

class CreateAdminGroup(Task):
    type = "startup"

    def execute(*args, **kwargs):
        db = kwargs.get("db")
        if db.has('permission'):
            all_permissions = set(db.permission.pk.values)

            if db.has('group'):
                if db.has('group', column='title', value='Admin'):
                    group_pk = db.filter('group', title='Admin').iloc[0].pk
                    instance = db.get(MODELS.Group, group_pk)
                    if hasattr(instance, 'permissions'):
                        if set(instance.permissions).difference(all_permissions):
                            return
                        else:
                            db.change(instance, pk=group_pk, permissions=all_permissions)
                            return

            admin_user_group = MODELS.Group(title='Admin', permissions=all_permissions)

            db.add(admin_user_group)

