import base64
import json
from datetime import date

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


def sign(pk: Ed25519PrivateKey, payload: dict, start: date, end: date):
    """
    Create a signed license payload using an Ed25519 private key. The function
    enriches the provided payload with a validity interval, serializes it into
    canonical JSON, and signs it using the given private key. The signature is
    returned as a base64-encoded string.
    Parameters
    ----------
    pk : Ed25519PrivateKey
        The Ed25519 private key used to sign the payload.
    payload : dict
        The base license payload (e.g., app_id, machine_id, features).
    start : date
        The start date of the license validity interval.
    end : date
        The end date of the license validity interval.

    Returns
    -------
    dict
        A dictionary containing:
        - "data": the full enriched payload including validity fields
        - "signature": the base64-encoded Ed25519 signature
    """

    valid_payload = {
        **payload,
        "valid_from": start.isoformat(),
        "valid_until": end.isoformat(),
    }

    text_to_sign = json.dumps(valid_payload, separators=(",", ":"), sort_keys=True)
    bytes_to_sign = text_to_sign.encode("utf-8")
    raw_signature = pk.sign(bytes_to_sign)

    return dict(
        data=payload,
        signature=base64.b64encode(raw_signature).decode("utf-8"),
    )
