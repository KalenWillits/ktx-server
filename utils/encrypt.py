import hashlib
from .generate_salt import generate_salt


def encrypt(string):
    salt = generate_salt()
    """
    Hashes a string for use in storing password to a database.
    Optional salt string for added security.
    """
    derived_key = hashlib.pbkdf2_hmac('sha256', bytes(string, 'UTF-8'), bytes(salt, 'UTF-8'), 100_000)

    return derived_key.hex()
