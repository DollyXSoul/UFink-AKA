# UFinAKA Prototype – Fingerprint-Based Blind Credential Authentication and Key Agreement (with Counting Garbled Bloom Filter Optimization)

## Overview

This project implements a **prototype of the UFinAKA protocol** described in the paper:

**UFinAKA: Fingerprint-Based Authentication and Key Agreement with Updatable Blind Credentials**

The system demonstrates how biometric authentication can be combined with **blind credentials, anonymous identities, and credential update mechanisms** to protect user privacy even if a credential database is compromised.
This implementation further extends the original protocol by introducing a **Counting Garbled Bloom Filter (CGBF)** to improve the efficiency of credential updates. The system also includes **security attack simulations** and **large-scale performance evaluation (100–500 users)** to demonstrate scalability and robustness.

This prototype is designed for **academic demonstration purposes** and simulates the main protocol mechanisms using simplified cryptographic primitives.

---

# Features

The current prototype implements the following components of the UFinAKA protocol.

## 1. Fingerprint-Based Authentication

Users authenticate using a simulated biometric input.

- Fingerprints are represented as strings
- Feature extraction converts fingerprints into biometric vectors
- Matching uses a configurable distance threshold

Example:

User ID: alice
Fingerprint: finger
[DEBUG] Biometric distance = 0

---

## 2. Anonymous Authentication

Instead of sending the real user identity, the client generates a **fresh anonymous identifier for every login session**.

Client computes:

IDC = $`g^{h(ID)} ⊕ (g^{sk})^ϖ`$

and sends:

(IDC , $`g^ϖ`$)

The server recovers the stable pseudonym:

$`Ψ_ID = IDC ⊕ (g^ϖ)^sk`$

This ensures:

- Every login appears with a **different identity**
- The server can still identify the correct user internally

Security property:

- Anonymous authentication
- Session unlinkability

---

## 3. Blind Credentials

Each user receives a **blind credential** derived from their identity and biometric template.

Credential form:

$`b_i = g^{h(ID || Bio)}`$

The credential is stored:

- On the **client smart card**
- Inside the server's **Garbled Bloom Filter**

The client proves possession of this credential during login without revealing the biometric data.

Security property:

- No plaintext biometrics stored on server

---

## 4. Garbled Bloom Filter (GBF)

Instead of storing credentials directly in the database, the server stores them in a **Garbled Bloom Filter**.

This provides:

- Obfuscated credential storage
- Privacy-preserving lookup
- Protection against database disclosure

The server database contains only metadata such as:

Ψ_ID\
upd

Actual credentials `b_i` are hidden inside the GBF.


### Limitation

The standard GBF does not support deletion or in-place updates. As a result, after credential updates, the GBF must be reconstructed, which introduces additional computational overhead.

---
## 5. Session Key Agreement

After successful authentication the client and server establish a shared session key using a **Diffie-Hellman key exchange**.

Client:

$`A = g^a`$

Server:

$`B = g^b`$

Both derive the shared secret:

$`K = g^{ab}`$\
SessionKey = $`H(K)`$

Example output:

[SERVER] Session key: 139401645261006859019668089474171342216
[CLIENT] Session key: 139401645261006859019668089474171342216

---

## 6. Credential Update After Database Compromise

If the server detects that the credential database has been compromised, all credentials are **globally re-randomized**.
Credentials are re-randomized using two approaches:

1. **Rebuild Mode (Original UFinAKA)**  
   - GBF is reconstructed after update

2. **Counting GBF Mode (Proposed)**  
   - Credentials are updated in-place without rebuilding

Update rule:

$`b_i' = b_i^α`$

where α is a random update factor.

This invalidates previously stolen credentials.

---


## 7. Counting Garbled Bloom Filter (Proposed Enhancement)

To improve the efficiency of credential updates, we extend the standard GBF into a **Counting Garbled Bloom Filter (CGBF)**.

Unlike the original GBF, CGBF supports:

- Insert
- Delete
- Update (in-place modification of credentials)

### Key Idea

Instead of rebuilding the entire GBF after credential updates, the system directly updates affected entries:

b_i' = b_i^α

### Benefits

- Eliminates GBF reconstruction
- Supports dynamic credential updates
- Improves scalability for large user bases

### Complexity Comparison

| Approach | Operation Cost |
|---------|--------------|
| Standard GBF | O(N) + rebuild |
| Counting GBF | O(N) |

---


## 8. Smart Card Synchronization

After credential update, client smart cards synchronize automatically:

$`b_i ← b_i^α`$

This allows users to continue authenticating normally.

---

## 9. Database Compromise Simulation

The script `simulate_compromise.py` demonstrates the recovery process after a database breach.

Steps simulated:

1. Attacker copies the database
2. Server detects compromise
3. Credentials are re-randomized
4. Smart cards synchronize

Example output:

--- Simulating Server Compromise ---

DB fingerprint (before update)
GBF fingerprint (before update)

[SERVER] Applying global credential re-randomization

DB fingerprint (after update)
GBF fingerprint (after update)

Credential storage successfully re-randomized

---

# System Architecture

Client \
├── Biometric verification \
├── Anonymous ID generation\
├── Blind credential storage\
├── Session key derivation

Server\
├── Long-term secret key (sk)\
├── Credential database\
├── Garbled Bloom Filter\
├── Credential verification\
├── Global credential update\
└── Session key agreement

---

# Project Structure

UFink-AKA\
│\
├── client\
│ ├── register.py\
│ └── login.py\
│\
├── server.py\
├── gbf.py\
├── biometric.py\
├── blind*credentials.py\
├── anonymous_id.py\
├── crypto_group.py\
├── security_tests.py\
├── benchmark_test.py\
├── bulk_setup.py\
│\
├── simulate_compromise.py\
│\
├── server_db.json\
├── gbf_storage.json\
└── smartcard*<user>.json

---

# Running the System

### Register a user

python -m client.register

### Login

python -m client.login

Example output:

[SERVER] Anonymous authentication success
[SERVER] Session key: ...
[CLIENT] Session key: ...

### Simulate database compromise

python simulate_compromise.py

### Run security tests

python security_tests.py

### Run large-scale benchmark (100 / 500 users)

python benchmark_test.py

---


# Security Evaluation

The system was tested against multiple attack scenarios to evaluate protocol robustness.

## Attacks Simulated

- Replay Attack
- Impersonation Attack
- Fabrication Attack
- Credential Tampering

## Results

| Attack Type | Result |
|------------|--------|
| Replay Attack | Partially vulnerable (no nonce tracking) |
| Impersonation | Prevented |
| Fabrication | Prevented |
| Credential Tampering | Prevented |

These results confirm that the protocol maintains strong authentication guarantees while highlighting areas for further improvement (e.g., replay protection).

---

# Performance Evaluation

The system was evaluated for scalability using **100 and 500 users**.

## Metrics Measured

- Authentication time
- Credential update time (post-compromise)

## Comparison

Two approaches were compared:

1. **Rebuild GBF (Original UFinAKA)**
2. **Counting GBF (Proposed)**

## Observations

- Counting GBF eliminates GBF reconstruction overhead
- Update time is significantly reduced
- Performance improvement increases with number of users

## Conclusion

The proposed Counting GBF improves system scalability and reduces recovery time after compromise.


# Security and Performance Summary

This prototype demonstrates:

- Secure biometric authentication
- Anonymous identity protection
- Blind credential verification
- Credential privacy using GBF
- Session key agreement
- Credential update after compromise
- Security testing against common attacks
- Performance optimization using Counting GBF
- Scalability evaluation up to 500 users

---
