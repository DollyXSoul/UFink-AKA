import json
from server import Server
from biometric import extract_biometric


def create_users(n):

    server = Server()

    for i in range(n):

        uid = f"user{i}"
        fp = f"fingerprint{i}"

        bio = extract_biometric(fp)

        # register on server
        pk, b_i = server.register_user(uid, bio)

        # 🔥 create smartcard (IMPORTANT)
        smart_card = {
            "user_id": uid,
            "biometric": bio,
            "server_pk": pk,
            "b_i": b_i
        }

        with open(f"smartcard_{uid}.json", "w") as f:
            json.dump(smart_card, f)

    print(f"[SETUP] Created {n} users + smartcards")
