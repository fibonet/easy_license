import json
from base64 import b64encode
from datetime import date, timedelta
from pathlib import Path
from uuid import getnode

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

from .license import License


def fetch_application_key(application: str, customer: str) -> bytes:
    """Fake implementation, this should make a server call"""
    machine_id = getnode().to_bytes(length=8, byteorder="big")
    payload = dict(
        application=application,
        customer=customer,
        machine_id=b64encode(machine_id).decode("ascii"),
    )
    private_key = Ed25519PrivateKey.generate()
    public_bytes = private_key.public_key().public_bytes_raw()

    return public_bytes


def fetch_license(application: str, customer: str) -> dict:
    """Fake implementation, this should make a server call"""
    first = date.today()
    last = first + timedelta(days=30)
    return dict(
        signature=b"",
        application=application,
        customer=customer,
        valid_from=first.isoformat(),
        valid_until=last.isoformat(),
    )


def load_or_fetch_application_key(application: str, customer: str):
    """
    Loads the application public key from a local `.pub` file if it exists.
    If the file does not exist, fetches the key from the server
    (via `fetch_application_key`) and saves it to disk.

    Args:
        application: The application name.
        customer: The customer identifier.

    Returns:
        Ed25519PublicKey: The loaded or fetched public key.

    Raises:
        Any exceptions raised by `Ed25519PublicKey.from_public_bytes()` if the key is invalid.
    """
    public_file = Path(f"{application}-{customer}.pub")

    if public_file.exists():
        with open(public_file, "rb") as f:
            public_bytes = f.read()

    else:
        public_bytes = fetch_application_key(application, customer)
        with open(public_file, "xb") as file:
            file.write(public_bytes)

    return Ed25519PublicKey.from_public_bytes(public_bytes)


def load_or_fetch_license(application: str, customer: str) -> License:
    """
    Loads a License object from a local JSON file if it exists.
    If the file does not exist, fetches the license from the server
    (via `fetch_license`) and saves it to disk.

    Args:
        application: The application name.
        customer: The customer identifier.

    Returns:
        License: The loaded or fetched License object.

    Raises:
        Any exceptions raised by `License.from_file()` if the file is corrupted or unreadable.
    """
    filepath = Path(f"{application}-{customer}-license.json")

    if not filepath.exists():
        license_data = fetch_license(application, customer)
        with open(filepath, "xt") as f:
            json.dump(license_data, f, separators=(",", ":"), sort_keys=True)

    return License.from_file(filepath)


def verify(application: str, customer: str):
    """
    Loads the license and application public key for the given application and customer,
    then verifies the license signature and validity period.

    Raises:
        InvalidSignature: If the license signature is invalid or the license is expired.
    """
    public_key = load_or_fetch_application_key(application, customer)
    a_license = load_or_fetch_license(application, customer)
    a_license.verify(public_key)
