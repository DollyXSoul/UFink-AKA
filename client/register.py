from biometric import extract_biometric
from server import Server

server = Server()


def register():
    uid = input("User ID: ")
    fp = input("Fingerprint: ")

    bio = extract_biometric(fp)
    pk = server.register_user(uid, bio)

    smart_card = {
        "user_id": uid,
        "biometric": bio,
        "server_pk": pk
    }

    import json
    with open(f"smartcard_{uid}.json", "w") as f:
        json.dump(smart_card, f)

    print("[CLIENT] Registration complete")


if __name__ == "__main__":
    register()
