import base64
import json
from datetime import date
from uuid import UUID

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


class LicenseStore:
    """what"""

    def __init__(self):
        self.store = dict()
        pass

    def get_or_raise(self, model: str, key: UUID):
        item = self.store[model].get(key)

        if item is None:
            raise KeyError(f"There is no app with {key}.")

        return item

    def get_application_key(self, payload: dict):
        """
        expected payload: dict(application=, customer=, machine=)
        let's embrace a new strategy:
         - application is an application identifier (uuid)
         - customer is a customer identifier (vat id)
         - machine is a machine identifier (mac)
        """
        private_key = self.get_or_raise("application_key", payload["application"])
        # TODO: create access log entry: (application, customer, machine, ip)
        return private_key
