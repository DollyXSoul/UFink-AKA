import hashlib
import json
import glob
from server import Server
from crypto_group import modexp

DB_FILE = "server_db.json"
GBF_FILE = "gbf_storage.json"


def file_fingerprint(path):
    """
    Compute SHA256 fingerprint of a file.
    Used to show database change after compromise recovery.
    """
    with open(path, "r") as f:
        data = f.read()

    return hashlib.sha256(data.encode()).hexdigest()


def simulate():

    server = Server()

    print("\n--- Simulating Server Compromise ---\n")

    # Step 1 — attacker copies database snapshot
    db_before = file_fingerprint(DB_FILE)
    gbf_before = file_fingerprint(GBF_FILE)

    print("DB fingerprint (before update):")
    print(db_before)

    print("\nGBF fingerprint (before update):")
    print(gbf_before)

    # Step 2 — server performs credential re-randomization
    print("\n[SERVER] Applying global credential re-randomization...\n")

    alpha = server.global_update()

    print("[SERVER] Credentials re-randomized")

    # Step 3 — snapshot after update
    db_after = file_fingerprint(DB_FILE)
    gbf_after = file_fingerprint(GBF_FILE)

    print("DB fingerprint (after update) — metadata unchanged:")
    print(db_after)

    print("GBF fingerprint (after update) — credentials updated:")
    print(gbf_after)

    # Step 4 — check if update worked
    if db_before != db_after or gbf_before != gbf_after:
        print("\n✔ Credential storage successfully re-randomized.")
    else:
        print("\n✘ No change detected — update failed.")

    # Step 5 — synchronize client smart cards
    print("\n[CLIENT] Synchronizing smart cards...\n")

    for card in glob.glob("smartcard_*.json"):

        with open(card) as f:
            sc = json.load(f)

        sc["b_i"] = modexp(sc["b_i"], alpha)

        with open(card, "w") as f:
            json.dump(sc, f)

    print("[CLIENT] Smart cards updated")

    print("\n--- Compromise simulation complete ---\n")


if __name__ == "__main__":
    alpha = simulate()
