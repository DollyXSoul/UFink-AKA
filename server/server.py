import json
from crypto_utils import H, gen_nonce

DB_PATH = "server/database.json"
SERVER_SECRET = "server_secret_x"   # fixed for prototype


def load_db():
    with open(DB_PATH, "r") as f:
        return json.load(f)


def save_db(db):
    with open(DB_PATH, "w") as f:
        json.dump(db, f, indent=4)

# ---------------- Registration ----------------


def register_user(user_id, masked_value):
    db = load_db()

    verifier = H(masked_value + SERVER_SECRET)

    db["users"][user_id] = {
        "verifier": verifier,
        "failed_attempts": 0
    }

    save_db(db)

    smart_card = {
        "user_id": user_id,
        "masked_value": masked_value
    }

    return smart_card

# ---------------- Authentication ----------------


def authenticate_user(user_id, login_value, nonce_u):
    db = load_db()

    if user_id not in db["users"]:
        return None

    stored_verifier = db["users"][user_id]["verifier"]

    expected = H(login_value + SERVER_SECRET)
    if expected != stored_verifier:
        db["users"][user_id]["failed_attempts"] += 1
        save_db(db)
        return None

    nonce_s = gen_nonce()
    save_db(db)

    return nonce_s

# ---------------- Credential Update ----------------


def update_verifier(user_id, new_masked_value):
    db = load_db()

    db["users"][user_id]["verifier"] = H(new_masked_value + SERVER_SECRET)
    db["users"][user_id]["failed_attempts"] = 0

    save_db(db)
    return True
