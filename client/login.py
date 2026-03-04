import json
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
    res = server.authenticate(IDC, g_varpi, AuthTag)

    if res:
        print("[CLIENT] Login success")
    else:
        print("[CLIENT] Login failed")


if __name__ == "__main__":
    login()
