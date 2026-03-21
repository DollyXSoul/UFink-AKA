import os
import json
import secrets

from gbf import GarbledBloomFilter, CountingGarbledBloomFilter
from crypto_group import G, modexp, hash_to_int
from crypto_group import random_zq
from blind_credentials import create_blind_credential
from anonymous_id import generate_server_keys, recover_identity

DB_FILE = "server_db.json"
KEY_FILE = "server_keys.json"


class Server:

    def __init__(self, mode="rebuild"):
        self.sk, self.pk = self.load_or_create_keys()
        self.users = self.load_users()

        if mode == "counting":
            self.gbf = CountingGarbledBloomFilter()
        else:
            self.gbf = GarbledBloomFilter()

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
            "b_i": cred.b_i
        }

        self.gbf.insert(str(Psi_ID), cred.b_i)

        print("Inserted Psi_ID into GBF:", Psi_ID)

        self.save_users()

        return self.pk, cred.b_i

    # -----------------------------
    # Authentication + Key Agreement
    # -----------------------------
    def authenticate(self, IDC, g_varpi, AuthTag, A):

        Psi_ID = recover_identity(IDC, g_varpi, self.sk)

        record = self.users.get(Psi_ID)

        if record is None:
            print("[SERVER] Authentication failed")
            return False

        stored_bi = self.gbf.retrieve(str(Psi_ID))

        print("Recovered Psi_ID:", Psi_ID)
        print("GBF retrieved value:", stored_bi)

        if stored_bi is None:
            print("[SERVER] Authentication failed (GBF miss)")
            return False

        if AuthTag != stored_bi:
            print("[SERVER] Credential verification failed")
            return False

        print("[SERVER] Anonymous authentication success")

        # -----------------------------
        # Session Key Agreement (DH)
        # -----------------------------

        b = secrets.randbits(128)

        B = modexp(G, b)

        # store temporary secret
        self.session_secret = b

        K = modexp(A, b)

        server_session_key = hash_to_int(str(K))
        print("[SERVER] Session key:", server_session_key)

        return B

    def rebuild_gbf(self):

        new_gbf = GarbledBloomFilter()

        for Psi_ID in self.users:
            bi = self.users[Psi_ID]["b_i"]
            new_gbf.insert(str(Psi_ID), bi)

        self.gbf = new_gbf
    # -----------------------------
    # GLOBAL COMPROMISE UPDATE
    # -----------------------------

    def global_update_rebuild(self):

        alpha = random_zq()

        for Psi_ID in self.users:
            old_bi = self.users[Psi_ID]["b_i"]
            new_bi = modexp(old_bi, alpha)

            self.users[Psi_ID]["b_i"] = new_bi

        self.rebuild_gbf()
        return alpha

    def global_update_counting(self):

        print("[SERVER] GLOBAL UPDATE (Counting GBF Mode)")

        alpha = random_zq()

        for Psi_ID in self.users:

            old_bi = self.users[Psi_ID]["b_i"]

            new_bi = modexp(old_bi, alpha)

            self.users[Psi_ID]["b_i"] = new_bi

        # 🔥 no rebuild
            self.gbf.update(str(Psi_ID), old_bi, new_bi)

        return alpha
