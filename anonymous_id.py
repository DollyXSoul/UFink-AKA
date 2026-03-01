# anonymous_id.py
from crypto_group import G, modexp, random_zq, hash_to_int


def generate_server_keys():
    sk = random_zq()
    pk = modexp(G, sk)
    return sk, pk


def xor_int(a: int, b: int) -> int:
    return a ^ b

# -------- Client side --------


def generate_anonymous_id(user_id: str, pk: int):
    varpi = random_zq()
    g_varpi = modexp(G, varpi)

    hid = hash_to_int(user_id)
    part1 = modexp(G, hid)
    part2 = modexp(pk, varpi)

    IDC = xor_int(part1, part2)
    return IDC, g_varpi

# -------- Server side --------


def recover_identity(IDC: int, g_varpi: int, sk: int):
    shared = modexp(g_varpi, sk)
    Psi_ID = xor_int(IDC, shared)
    return Psi_ID
