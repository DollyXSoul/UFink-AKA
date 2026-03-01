# 🔐 UFinAKA Prototype – Fingerprint-Based Blind Credential Authentication

## Overview

This project implements a research-oriented prototype of the **UFinAKA (Updatable Fingerprint-Based Authentication and Key Agreement)** protocol, with emphasis on:

- Anonymous authentication
- Updatable blind credentials
- Credential re-randomization after compromise
- Biometric-based user verification
- Persistent server key management

The implementation follows the design principles of the original paper, including system-wide credential update in case of database compromise.

---

## Cryptographic Model

The system uses:

- A cyclic multiplicative group $`( G \subset \mathbb{Z}_p^* )`$
- Modular exponentiation for blind credentials
- Hash-to-group mapping for pseudonymous identifiers
- Persistent long-term server secret key $`sk`$
- Random re-randomization factor $`\alpha `$ for global updates

All operations are implemented over a large prime field for pedagogical purposes.

---

## System Architecture

### Client

- Local biometric feature extraction (simulated)
- Threshold-based biometric verification
- Anonymous identifier generation per session
- Blind credential proof generation

### Server

- Persistent secret key (`sk`)
- Credential database indexed by $` g^{h(ID)} `$
- Anonymous identity recovery
- Blind credential verification
- Global re-randomization after compromise

---

## Security Properties Demonstrated

- ✔ No plaintext usernames stored
- ✔ No biometric data stored on server
- ✔ Anonymous login per session
- ✔ Unlinkability across sessions
- ✔ Forward security after compromise
- ✔ Global credential re-randomization
- ✔ Compromised database snapshot invalidation

---

## Assumptions

- Biometric feature extraction is abstracted as a deterministic feature vector.
- The hash function is instantiated using SHA-256.
- The discrete logarithm problem in the chosen group is assumed hard.
- The adversary may obtain a full snapshot of the credential database.
- Communication channel is considered insecure (Dolev–Yao model).

---

## Implemented Protocol Components

### 1. Registration

- Blind credential generation
- Pseudonymous identifier computation
- Persistent credential storage

### 2. Anonymous Authentication

- Session-specific anonymous identifier `(IDC, g^ϖ)`
- Server-side recovery of stable pseudonym
- Blind credential verification

### 3. Global Compromise Recovery

System-wide re-randomization:

$`[
b_i' = b_i^{\alpha}
]`$

- Database snapshot invalidation
- Forward security guarantee

### 4. Compromise Simulation

The file `simulate_compromise.py` demonstrates:

- Database snapshot fingerprinting
- Global credential update
- Verification that compromised snapshot becomes useless

---

## Project Structure

| File | Purpose |
|------|---------|
| `crypto_group.py` | Group and exponentiation primitives |
| `blind_credentials.py` | Blind credential generation and update |
| `anonymous_id.py` | Anonymous authentication logic |
| `server.py` | Persistent server implementation |
| `simulate_compromise.py` | Compromise simulation |
| `client/` | Registration, login, and update flows |

---

## Running the System

From the project root:

```bash
python -m client.register
python -m client.login
python simulate_compromise.py
