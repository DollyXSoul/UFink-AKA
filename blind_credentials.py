# blind_credentials.py
from crypto_group import G, P, modexp, random_zq, hash_to_int


class BlindCredential:
    def __init__(self, b_i: int, upd: int):
        self.b_i = b_i        # blind credential
        self.upd = upd        # update factor


def create_blind_credential(user_id: str, bio_vector: list[int]):
    bio_str = "".join(map(str, bio_vector))

    id_token = modexp(G, hash_to_int(user_id))   # g^{h(ID)}
    bio_hash = hash_to_int(bio_str)

    b_i = modexp(id_token, bio_hash)
    upd = random_zq()

    return BlindCredential(b_i, upd)


def update_blind_credential(cred: BlindCredential):
    alpha = random_zq()

    b_new = modexp(cred.b_i, alpha)
    upd_new = (cred.upd * alpha) % P
    w = modexp(G, upd_new)

    cred.b_i = b_new
    cred.upd = upd_new

    return w   # sent to client for synchronization
