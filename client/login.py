import json
from biometric import extract_biometric, biometric_match
from anonymous_id import generate_anonymous_id
from server import Server
from crypto_group import G, hash_to_int, modexp

T = 50


def login():
    server = Server()

    uid = input("User ID: ")
    fp = input("Fingerprint: ")

    with open(f"smartcard_{uid}.json") as f:
        sc = json.load(f)

    bio_in = extract_biometric(fp)

    if not biometric_match(sc["biometric"], bio_in, T):
        print("[CLIENT] Biometric failed")
        return

    IDC, g_varpi = generate_anonymous_id(uid, sc["server_pk"])

    # Compute credential proof
    Psi_ID = modexp(G, hash_to_int(uid))
    record = server.users.get(Psi_ID)
    b_i = record["b_i"]

    AuthTag = b_i
    print("IDC:", IDC)
    print("g_varpi:", g_varpi)
    print("AuthTag:", AuthTag)

    res = server.authenticate(IDC, g_varpi, AuthTag)

    if res:
        print("[CLIENT] Login success")
    else:
        print("[CLIENT] Login failed")


if __name__ == "__main__":
    login()
