import time
import json
import secrets

from server import Server
from bulk_setup import create_users
from crypto_group import G, modexp
from anonymous_id import generate_anonymous_id


import os
import glob


def cleanup():

    files = ["server_db.json", "gbf_storage.json"]

    for f in files:
        if os.path.exists(f):
            os.remove(f)

    for f in glob.glob("smartcard_*.json"):
        os.remove(f)

    print("[CLEANUP] Old data removed")


def test_authentication(n):

    server = Server()

    users = list(server.users.keys())

    start = time.time()

    for i, Psi_ID in enumerate(users):

        uid = f"user{i}"

        with open(f"smartcard_{uid}.json") as f:
            sc = json.load(f)

        a = secrets.randbits(128)
        A = modexp(G, a)

        IDC, g_varpi = generate_anonymous_id(uid, sc["server_pk"])

        server.authenticate(IDC, g_varpi, sc["b_i"], A)

    end = time.time()

    return end - start


def benchmark_update(n):

    from bulk_setup import create_users

    # REBUILD
    server = Server(mode="rebuild")
    create_users(n)

    import time
    start = time.time()
    server.global_update_rebuild()
    t1 = time.time() - start

    # COUNTING
    server = Server(mode="counting")
    create_users(n)

    start = time.time()
    server.global_update_counting()
    t2 = time.time() - start

    print(f"\nUsers: {n}")
    print(f"Rebuild Time:  {t1:.6f}")
    print(f"Counting Time: {t2:.6f}")

    improvement = ((t1 - t2) / t1) * 100 if t1 > 0 else 0
    print(f"Improvement: {improvement:.2f}%")


def run():

    for n in [5]:

        print(f"\n===== TESTING FOR {n} USERS =====")

        create_users(n)

        auth_time = test_authentication(n)
        print(f"Authentication Time: {auth_time:.6f}")

        benchmark_update(n)


if __name__ == "__main__":
    cleanup()
    run()
