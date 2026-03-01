# crypto_group.py
import secrets
import hashlib

# Large prime (2^127 - 1), safe for coursework
P = 170141183460469231731687303715884105727
G = 3


def random_zq():
    return secrets.randbelow(P - 2) + 1


def modexp(base, exp):
    return pow(base, exp, P)


def hash_to_int(data: str) -> int:
    h = hashlib.sha256(data.encode()).hexdigest()
    return int(h, 16) % P
