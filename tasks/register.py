from apps.server.tasks import tasks as server_tasks
from apps.accounts.tasks import tasks as accounts_tasks
from apps.client.tasks import tasks as client_tasks
from apps.game.tasks import tasks as game_tasks
from apps.assets.tasks import tasks as assets_tasks

tasks = [*accounts_tasks, *server_tasks, *client_tasks, *game_tasks, *assets_tasks]
