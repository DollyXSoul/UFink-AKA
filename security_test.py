import json
import secrets

from server import Server
from crypto_group import G, modexp, hash_to_int
from biometric import extract_biometric
from anonymous_id import generate_anonymous_id


def register_test_user(server, uid, fp):
    bio = extract_biometric(fp)
    pk, b_i = server.register_user(uid, bio)

    smart_card = {
        "user_id": uid,
        "biometric": bio,
        "server_pk": pk,
        "b_i": b_i
    }

    with open(f"smartcard_{uid}.json", "w") as f:
        json.dump(smart_card, f)

    return smart_card


# -----------------------------
# 1. Replay Attack Test
# -----------------------------
def replay_attack_test():
    print("\n[TEST] Replay Attack")

    server = Server()
    sc = register_test_user(server, "alice", "fingerprint123")

    a = secrets.randbits(128)
    A = modexp(G, a)

    IDC, g_varpi = generate_anonymous_id("alice", sc["server_pk"])
    AuthTag = sc["b_i"]

    # First authentication
    B1 = server.authenticate(IDC, g_varpi, AuthTag, A)

    # Replay same message
    B2 = server.authenticate(IDC, g_varpi, AuthTag, A)

    if B2:
        print("WARNING: Replay possible (protocol may rely on biometric freshness)")
    else:
        print("PASS: Replay rejected")


# -----------------------------
# 2. Impersonation Attack
# -----------------------------
def impersonation_test():
    print("\n[TEST] Impersonation Attack")

    server = Server()
    sc = register_test_user(server, "bob", "fingerprint456")

    a = secrets.randbits(128)
    A = modexp(G, a)

    # attacker generates fake ID
    IDC, g_varpi = generate_anonymous_id("attacker", sc["server_pk"])

    AuthTag = sc["b_i"]

    result = server.authenticate(IDC, g_varpi, AuthTag, A)

    if result:
        print("FAIL: Attacker authenticated")
    else:
        print("PASS: Impersonation prevented")


# -----------------------------
# 3. Credential Tampering
# -----------------------------
def credential_tamper_test():
    print("\n[TEST] Credential Tampering")

    server = Server()
    sc = register_test_user(server, "charlie", "fingerprint789")

    a = secrets.randbits(128)
    A = modexp(G, a)

    IDC, g_varpi = generate_anonymous_id("charlie", sc["server_pk"])

    fake_tag = sc["b_i"] + 1

    result = server.authenticate(IDC, g_varpi, fake_tag, A)

    if result:
        print("FAIL: Tampered credential accepted")
    else:
        print("PASS: Tampered credential rejected")


# -----------------------------
# 4. Session Key Freshness
# -----------------------------
def session_key_test():
    print("\n[TEST] Session Key Freshness")

    server = Server()
    sc = register_test_user(server, "david", "fingerprint999")

    a1 = secrets.randbits(128)
    A1 = modexp(G, a1)

    IDC, g_varpi = generate_anonymous_id("david", sc["server_pk"])
    AuthTag = sc["b_i"]

    B1 = server.authenticate(IDC, g_varpi, AuthTag, A1)

    a2 = secrets.randbits(128)
    A2 = modexp(G, a2)

    B2 = server.authenticate(IDC, g_varpi, AuthTag, A2)

    if B1 != B2:
        print("PASS: Session keys are fresh")
    else:
        print("FAIL: Session key reuse detected")


# -----------------------------
# 5. Credential Update Security - For normal gbf
# -----------------------------
def credential_update_test():
    print("\n[TEST] Credential Update Security  -using normal gbf")

    server = Server()
    sc = register_test_user(server, "eve", "fingerprintABC")

    a = secrets.randbits(128)
    A = modexp(G, a)

    IDC, g_varpi = generate_anonymous_id("eve", sc["server_pk"])
    AuthTag = sc["b_i"]

    # authenticate before compromise
    server.authenticate(IDC, g_varpi, AuthTag, A)

    alpha = server.global_update_rebuild()

    # try old credential again
    result = server.authenticate(IDC, g_varpi, AuthTag, A)

    if result:
        print("FAIL: Old credential still valid")
    else:
        print("PASS: Old credential invalidated after update")

# -----------------------------
# 6. Credential Update Security - For counting gbf
# -----------------------------


def credential_update_test_cgbf():
    print("\n[TEST] Credential Update Security  - using counting gbf")

    server = Server("counting")
    sc = register_test_user(server, "eve", "fingerprintABC")

    a = secrets.randbits(128)
    A = modexp(G, a)

    IDC, g_varpi = generate_anonymous_id("eve", sc["server_pk"])
    AuthTag = sc["b_i"]

    # authenticate before compromise
    server.authenticate(IDC, g_varpi, AuthTag, A)

    alpha = server.global_update_counting()

    # try old credential again
    result = server.authenticate(IDC, g_varpi, AuthTag, A)

    if result:
        print("FAIL: Old credential still valid")
    else:
        print("PASS: Old credential invalidated after update")


# -----------------------------
# 7. Man in The middle Attack Test
# -----------------------------

def mitm_attack_test():

    print("\n[TEST] Man-in-the-Middle Attack")

    server = Server()

    uid = "alice"
    fp = "fingerprint123"

    bio = extract_biometric(fp)
    pk, b_i = server.register_user(uid, bio)

    smartcard = {
        "user_id": uid,
        "biometric": bio,
        "server_pk": pk,
        "b_i": b_i
    }

    # Client generates authentication message
    a = secrets.randbits(128)
    A = modexp(G, a)

    IDC, g_varpi = generate_anonymous_id(uid, pk)
    AuthTag = b_i

    print("Original AuthTag:", AuthTag)

    # -------- Attacker intercepts --------
    tampered_A = A + 1
    tampered_tag = AuthTag + 123

    print("Attacker modified values")

    B = server.authenticate(IDC, g_varpi, tampered_tag, tampered_A)

    if B:
        print("FAIL: MITM succeeded")
    else:
        print("PASS: MITM detected and rejected")

# -----------------------------
# 8. Man in The middle Attack Test
# -----------------------------


def fabrication_attack():

    print("\n[TEST] Fabrication Attack")

    server = Server()

    # attacker generates fake parameters
    fake_IDC = secrets.randbits(128)
    fake_varpi = secrets.randbits(128)

    fake_tag = secrets.randbits(128)

    a = secrets.randbits(128)
    fake_A = modexp(G, a)

    result = server.authenticate(fake_IDC, fake_varpi, fake_tag, fake_A)

    if result:
        print("FAIL: Fabrication attack succeeded")
    else:
        print("PASS: Fabrication attack rejected")


# -----------------------------
# Run All Tests
# -----------------------------
def run_all_tests():

    print("\n===== SECURITY TEST SUITE =====")

    replay_attack_test()
    impersonation_test()
    credential_tamper_test()
    session_key_test()
    credential_update_test()
    credential_update_test_cgbf()
    mitm_attack_test()
    fabrication_attack()

    print("\n===== TESTING COMPLETE =====")


if __name__ == "__main__":
    run_all_tests()
