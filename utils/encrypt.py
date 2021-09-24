import hashlib


def encrypt(string, hash_salt=""):
    derived_key = hashlib.pbkdf2_hmac('sha256', bytes(string, 'UTF-8'), hash_salt, 100_000)
    return derived_key.hex()
