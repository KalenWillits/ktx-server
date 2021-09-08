from apps.server.models import models as server_models
from apps.accounts.models import models as accounts_models
from apps.client.models import models as client_models
from apps.game.models import models as game_models
from apps.assets.models import models as assets_models

models = [*accounts_models, *server_models, *client_models, *game_models, *assets_models]
