import json
from base64 import b64decode, b64encode
from datetime import date, timedelta
from pathlib import Path
from uuid import getnode

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

from .common import License, slugify


def fetch_application_key(a_key: str) -> bytes:
    machine_id = getnode().to_bytes(length=8, byteorder="big")
    payload = dict(
        key=a_key,
        machine_id=b64encode(machine_id).decode("ascii"),
    )
    private_key = Ed25519PrivateKey.generate()
    public_bytes = private_key.public_key().public_bytes_raw()

    return public_bytes


def fetch_license(a_key: str) -> dict:
    first = date.today()
    last = first + timedelta(days=30)
    return dict(
        signature=b"",
        valid_from=first,
        valid_until=last,
        meta=dict(key=a_key),
    )


def load_application_key(a_key: str):
    public_file = Path(f"{a_key}.pub")

    if public_file.exists():
        with open(public_file, "rb") as f:
            public_bytes = f.read()

    else:
        public_bytes = fetch_application_key(a_key)
        with open(public_file, "xb") as file:
            file.write(public_bytes)

    return Ed25519PublicKey.from_public_bytes(public_bytes)


def load_license(a_key: str) -> License:
    license_file = Path(f"{a_key}-license.json")

    if license_file.exists():
        with open(license_file, "rb") as f:
            license_data = json.load(f)

    else:
        license_data = fetch_license(a_key)
        with open(license_file, "xb") as f:
            json.dump(license_data, f, separators=(",", ":"), sort_keys=True)

    return License(**license_data)


def verify(application: str, vat_id: str):
    key = f"{slugify(application)}_{slugify(vat_id)}"
    public_key = load_application_key(key)
    a_license = load_license(key)
    a_license.verify(public_key)
