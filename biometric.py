"""
Biometric abstraction as assumed in the paper.
Bio_i is a feature vector supporting distance computation.
"""


def extract_biometric(fingerprint_input: str) -> list:
    """
    Simulated biometric feature vector.
    Each character is mapped to an integer feature.
    """
    return [ord(c) for c in fingerprint_input]


def biometric_distance(bio1: list, bio2: list) -> int:
    """
    Simple distance metric (L1 distance).
    """
    min_len = min(len(bio1), len(bio2))
    dist = sum(abs(bio1[i] - bio2[i]) for i in range(min_len))
    dist += abs(len(bio1) - len(bio2)) * 10
    return dist


def biometric_match(stored_bio, input_bio, threshold: int) -> bool:
    d = biometric_distance(stored_bio, input_bio)
    print(f"[DEBUG] Biometric distance = {d}, Threshold = {threshold}")
    return d <= threshold
