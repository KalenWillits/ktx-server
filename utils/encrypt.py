import hashlib
from .generate_salt import generate_salt


def encrypt(string):
    """
    Hashes a string for use in storing password to a database.
    Optional salt string for added security.
    """
    salt = generate_salt()
    derived_key = hashlib.pbkdf2_hmac('sha256', bytes(string, 'UTF-8'), bytes(salt, 'UTF-8'), 100_000)

    return derived_key.hex()
