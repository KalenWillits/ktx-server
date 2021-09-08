import os
import secrets

def generate_salt():
    '''Checks if a salt hash has been made, if not a .salt file is created.'''
    salt_file = os.path.join(".salt")
    if not os.path.isfile(salt_file):
        with open(salt_file, 'w+') as file:
            file.write(secrets.token_hex())
