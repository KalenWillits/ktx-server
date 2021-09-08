import hashlib
from config import settings


def encrypt(string):
    derived_key = hashlib.pbkdf2_hmac('sha256', bytes(string, 'UTF-8'), settings.hash_salt, 100_000)
    return derived_key.hex()
