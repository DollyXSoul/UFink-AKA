import json
import secrets
from crypto_group import G, modexp, hash_to_int
from biometric import extract_biometric, biometric_match
from anonymous_id import generate_anonymous_id
from server import Server

T = 30


def login():
    server = Server()

    uid = input("User ID: ")
    fp = input("Fingerprint: ")

    # Load smart card
    with open(f"smartcard_{uid}.json") as f:
        sc = json.load(f)

    # Biometric verification
    bio_in = extract_biometric(fp)
    a = secrets.randbits(128)
    A = modexp(G, a)

    if not biometric_match(sc["biometric"], bio_in, T):
        print("[CLIENT] Biometric failed")
        return

    # Anonymous identifier generation
    IDC, g_varpi = generate_anonymous_id(uid, sc["server_pk"])

    # Credential proof (from smart card, NOT server DB)
    AuthTag = sc["b_i"]

    # Optional debug prints (can remove later)
    print("IDC:", IDC)
    print("g_varpi:", g_varpi)
    print("AuthTag:", AuthTag)

    # Send to server
    B = server.authenticate(IDC, g_varpi, AuthTag, A)

    if not B:
        print("[CLIENT] Login failed")
        return

    K = modexp(B, a)

    session_key = hash_to_int(str(K))

    print("[CLIENT] Login success")
    print("[CLIENT] Session key:", session_key)


if __name__ == "__main__":
    login()
