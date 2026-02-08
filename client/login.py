import json
from crypto_utils import H, xor_hex
from server.server import authenticate_user
from biometric import extract_biometric, biometric_match

T_BASE = 50    # base threshold


def login():
    user_id = input("User ID: ")
    password = input("Password: ")
    fingerprint = input("Fingerprint (simulated): ")

    with open(f"smartcard_{user_id}.json", "r") as f:
        smart_card = json.load(f)

    HPW = H(user_id + password)
    BF_input = extract_biometric(fingerprint)
    BF_stored = smart_card["biometric_template"]
    login_value = HPW
    if not biometric_match(BF_stored, BF_input, T_BASE):
        print("[ERROR] Biometric verification failed")
        return

    nonce_u = "nonce_user"

    nonce_s = authenticate_user(user_id, login_value, nonce_u)

    if nonce_s is None:
        print("[ERROR] Authentication failed")
        return

    SK_client = H(nonce_u + nonce_s + login_value)
    print("[SUCCESS] Authentication successful")
    print("Session Key:", SK_client)


if __name__ == "__main__":
    login()
