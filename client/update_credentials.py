from crypto_utils import H, xor_hex
from server.server import update_verifier


def update():
    user_id = input("User ID: ")
    new_password = input("New Password: ")
    new_fingerprint = input("New Fingerprint: ")

    HPW_new = H(user_id + new_password)
    BF_new = H(new_fingerprint)

    new_masked = xor_hex(HPW_new, BF_new)

    update_verifier(user_id, new_masked)
    print("[INFO] Credentials updated successfully")


if __name__ == "__main__":
    update()
