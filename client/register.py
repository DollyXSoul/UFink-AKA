from biometric import extract_biometric
from server import Server
from crypto_group import G, hash_to_int, modexp

server = Server()


def register():
    uid = input("User ID: ").strip()
    fp = input("Fingerprint: ")

    bio = extract_biometric(fp)

    # Register user with server
    pk, b_i = server.register_user(uid, bio)

    # ----- Compute SAME blind credential as server -----
    bio_str = "".join(map(str, bio))
    exponent = hash_to_int(uid + bio_str)

    smart_card = {
        "user_id": uid,
        "biometric": bio,
        "server_pk": pk,
        "b_i": b_i
    }

    import json
    with open(f"smartcard_{uid}.json", "w") as f:
        json.dump(smart_card, f)

    print("[CLIENT] Registration complete")


if __name__ == "__main__":
    register()
