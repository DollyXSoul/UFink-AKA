import hashlib
import secrets


def H(data: str) -> str:
    """
    SHA-256 hash function
    Input: string
    Output: hex string
    """
    return hashlib.sha256(data.encode()).hexdigest()


def gen_nonce(length: int = 16) -> str:
    """
    Generate secure random nonce
    """
    return secrets.token_hex(length)


def xor_hex(a: str, b: str) -> str:
    """
    XOR two hex strings
    """
    return hex(int(a, 16) ^ int(b, 16))[2:]


if __name__ == "__main__":
    # basic sanity test
    x = H("test")
    y = gen_nonce()
    print("Hash:", x)
    print("Nonce:", y)
