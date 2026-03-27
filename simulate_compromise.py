import hashlib
import json
import glob
import time
import os

from server import Server
from crypto_group import modexp

DB_FILE = "server_db.json"


def file_fingerprint(path):
    if not os.path.exists(path):
        return "FILE_NOT_FOUND"
    with open(path, "r") as f:
        data = f.read()

    return hashlib.sha256(data.encode()).hexdigest()


def simulate(mode="rebuild"):
    """
    mode = "rebuild" OR "counting"
    """
    GBF_FILE = "cgbf_storage.json" if mode == "counting" else "gbf_storage.json"
    server = Server(mode=mode)

    print("\n--- Simulating Server Compromise ---\n")

    # Step 1 — attacker copies database snapshot
    db_before = file_fingerprint(DB_FILE)
    gbf_before = file_fingerprint(GBF_FILE)

    print("DB fingerprint (before):", db_before)
    print("GBF fingerprint (before):", gbf_before)

    # Step 2 — perform update
    print(f"\n[SERVER] Applying {mode.upper()} update...\n")

    start = time.time()

    if mode == "counting":
        alpha = server.global_update_counting()
    else:
        alpha = server.global_update_rebuild()

    end = time.time()

    print(f"[SERVER] Update complete in {end - start:.6f} sec")

    # Step 3 — snapshot after update
    db_after = file_fingerprint(DB_FILE)
    gbf_after = file_fingerprint(GBF_FILE)

    print("\nDB fingerprint (after):", db_after)
    print("GBF fingerprint (after):", gbf_after)

    # Step 4 — verify change
    if gbf_before != gbf_after:
        print("\n✔ Credentials successfully updated")
    else:
        print("\n✘ No change detected")

    # Step 5 — sync client smart cards
    print("\n[CLIENT] Synchronizing smart cards...\n")

    for card in glob.glob("smartcard_*.json"):

        with open(card) as f:
            sc = json.load(f)

        sc["b_i"] = modexp(sc["b_i"], alpha)

        with open(card, "w") as f:
            json.dump(sc, f)

    print("[CLIENT] Smart cards updated")

    print("\n--- Simulation Complete ---\n")

    return end - start


def compare():

    print("\n===== COMPARISON: REBUILD vs COUNTING GBF =====\n")

    t1 = simulate("rebuild")
    t2 = simulate("counting")

    print("\n===== RESULT =====")
    print(f"Rebuild Time:  {t1:.6f} sec")
    print(f"Counting Time: {t2:.6f} sec")

    improvement = ((t1 - t2) / t1) * 100 if t1 > 0 else 0

    print(f"Improvement: {improvement:.2f}% faster\n")


if __name__ == "__main__":
    compare()
