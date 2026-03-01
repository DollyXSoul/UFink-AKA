import json
import os
from crypto_group import G, hash_to_int, modexp, random_zq
from blind_credentials import create_blind_credential
from anonymous_id import generate_server_keys, recover_identity

DB_FILE = "server_db.json"
KEY_FILE = "server_keys.json"


class Server:
    def __init__(self):
        self.sk, self.pk = self.load_or_create_keys()
        self.users = self.load_users()

    # -----------------------------
    # Key Management (Long-term sk)
    # -----------------------------
    def load_or_create_keys(self):
        if os.path.exists(KEY_FILE):
            with open(KEY_FILE, "r") as f:
                data = json.load(f)
                if "sk" in data:
                    return int(data["sk"]), int(data["pk"])

        sk, pk = generate_server_keys()
        with open(KEY_FILE, "w") as f:
            json.dump({"sk": str(sk), "pk": str(pk)}, f, indent=2)
        return sk, pk

    # -----------------------------
    # Credential Database
    # -----------------------------
    def load_users(self):
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r") as f:
                data = json.load(f)
                return {int(k): v for k, v in data.items()}
        return {}

    def save_users(self):
        with open(DB_FILE, "w") as f:
            json.dump({str(k): v for k, v in self.users.items()}, f, indent=2)

    # -----------------------------
    # Registration
    # -----------------------------
    def register_user(self, user_id, bio_vector):
        cred = create_blind_credential(user_id, bio_vector)

        Psi_ID = modexp(G, hash_to_int(user_id))

        self.users[Psi_ID] = {
            "b_i": cred.b_i,
            "upd": cred.upd
        }

        self.save_users()
        return self.pk

    # -----------------------------
    # Authentication
    # -----------------------------
    def authenticate(self, IDC, g_varpi, AuthTag):
        Psi_ID = recover_identity(IDC, g_varpi, self.sk)

        record = self.users.get(Psi_ID)
        if record is None:
            print("[SERVER] Authentication failed")
            return False

        if AuthTag == record["b_i"]:
            print("[SERVER] Anonymous authentication success")
            return True

        print("[SERVER] Credential verification failed")
        return False

    # -----------------------------
    # GLOBAL COMPROMISE UPDATE
    # -----------------------------
    def global_update(self):
        print("[SERVER] Compromise detected — global re-randomization started")

        alpha = random_zq()

        for Psi_ID, record in self.users.items():
            record["b_i"] = modexp(record["b_i"], alpha)
            record["upd"] = record["upd"] * alpha

        self.save_users()

        print("[SERVER] GLOBAL credential re-randomization complete")
