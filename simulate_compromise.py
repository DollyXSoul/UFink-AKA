import json
import hashlib
from server import Server

DB_FILE = "server_db.json"


def db_fingerprint():
    """
    Compute a hash fingerprint of the credential database.
    This simulates an attacker copying the DB.
    """
    with open(DB_FILE, "r") as f:
        data = f.read()
    return hashlib.sha256(data.encode()).hexdigest()


def simulate():
    server = Server()

    print("\n--- Simulating Server Compromise ---\n")

    # Step 1: Attacker copies DB snapshot
    before_hash = db_fingerprint()
    print("Database snapshot hash (before update):")
    print(before_hash)

    # Step 2: Global re-randomization
    print("\nApplying global credential re-randomization...\n")
    server.global_update()

    # Step 3: Snapshot after update
    after_hash = db_fingerprint()
    print("Database snapshot hash (after update):")
    print(after_hash)

    # Step 4: Compare
    if before_hash != after_hash:
        print("\n✔ Credential database successfully re-randomized.")
    else:
        print("\n✘ No change detected — update failed.")

    print("\n--- Compromise simulation complete ---\n")


if __name__ == "__main__":
    simulate()
