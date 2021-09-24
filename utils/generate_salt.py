import os
import secrets

def generate_salt() -> str:
    '''Checks if a salt hash has been made, if not a .salt file is created.'''
    salt_file = os.path.join(".salt")
    if not os.path.isfile(salt_file):
        with open(salt_file, "w") as file:
            salt = secrets.token_hex()
            file.write(salt)

    else:
        with open(salt_file, "r") as file:
            salt = file.read()

    return salt
