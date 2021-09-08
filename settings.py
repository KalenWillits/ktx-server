import os
import string
from utils import generate_salt

data_path = 'data'
assets_path = os.path.join(data_path, 'assets')
token_required = False
disable_constraints = False
database_save_interval = 60*60*24  # Seconds
time_to_token_expiration = 15  # Minutes
reg_key_char_set = string.ascii_uppercase+string.digits
reg_key_len = 9
port = 5000
host = 'localhost'
path = ''
server_timezone = 'UTC'
debug = False

generate_salt()
with open(os.path.join(".salt"), "rb") as file:
    hash_salt = file.read()
