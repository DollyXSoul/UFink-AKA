from crypto_utils import H, xor_hex
from server.server import register_user
from biometric import extract_biometric
import json


def register():
    user_id = input("User ID: ")
    password = input("Password: ")
    fingerprint = input("Fingerprint (simulated): ")

    HPW = H(user_id + password)

    BF = extract_biometric(fingerprint)

    masked_value = HPW

    smart_card = register_user(user_id, masked_value)

# Personalize smart card locally with biometric template
    smart_card["biometric_template"] = BF

    with open(f"smartcard_{user_id}.json", "w") as f:
        json.dump(smart_card, f, indent=4)

    print("[INFO] Registration successful")


if __name__ == "__main__":
    register()
