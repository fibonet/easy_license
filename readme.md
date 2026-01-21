# Eazy Licensing Tool

This repository provides a **minimal offline license signing and verification system**
using Ed25519 asymmetric cryptography.

The goal is deliberately simple:

* Verify that a license was issued by the holder of the private key
* Detect any modifications to the license data
* Enforce date-based validity

This is **not DRM** — it is a traditional, lightweight system to keep honest customers honest.

---

## Design Principles

* **Asymmetric signing**: private key signs, public key verifies
* **Human-readable licenses**: no encryption, only signatures
* **Deterministic JSON signing**: canonical serialization ensures integrity
* **Offline verification**: no network calls required
* **Minimal logic**: only signature and date checks

If any field in the license changes, signature verification will fail.

---

## Intended Usage

- [ ] Client collects machine identification and registers / signs up to server
- [ ] Client has a license file and verifies signature using the public key (offline)
- [ ] Client without a valid license requests one from the server
- [ ] Step 4: PROFIT !?!?

- [ ] on register server creates public / private key pairs for client
- [ ] on license request verifies payments and generates a valid license


---

## Limitations

* Full control over the runtime allows bypassing verification
* System relies on contracts, payments, and support for enforcement
* No hardware binding or tamper-proofing

This is intentional and aligns with traditional commercial software licensing.


