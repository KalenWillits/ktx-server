import os
import string
from config.utils import generate_salt

class Settings:
    def __init__(self):
        self.data_path = 'data'
        self.assets_path = os.path.join(self.data_path, 'assets')
        self.render_playground = True
        self.token_required = False
        self.disable_constraints = False
        self.database_save_interval = 60*60*24  # Seconds
        self.time_to_token_expiration = 15  # Minutes
        self.reg_key_char_set = string.ascii_uppercase+string.digits
        self.reg_key_len = 9
        self.port = 5000
        self.host = 'localhost'
        self.path = ''
        self.server_timezone = 'UTC'
        self.debug = False
        generate_salt()
        with open(os.path.join('config', '.salt'), 'rb') as file:
            self.hash_salt = file.read()


settings = Settings()
