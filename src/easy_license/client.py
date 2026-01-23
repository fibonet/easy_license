from base64 import b64decode, b64encode
from pathlib import Path
from uuid import getnode

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

from .common import slugify


def register_rpc(payload: dict) -> dict:
    print("register payload", payload)
    private_key = Ed25519PrivateKey.generate()
    public = private_key.public_key().public_bytes_raw()
    return dict(public_key=b64encode(public).decode("ascii"))


def register(application: str, vat_id: str):
    public_file = Path(f"{slugify(application)}_{slugify(vat_id)}.pub")

    if public_file.exists():
        with open(public_file, "rb") as f:
            public_bytes = f.read()

    else:
        machine_id = getnode().to_bytes(length=8, byteorder="big")
        app_meta = dict(
            application=application,
            vat_id=vat_id,
            machine_id=b64encode(machine_id).decode("ascii"),
        )
        response = register_rpc(app_meta)
        public_bytes = b64decode(response["public_key"].encode("ascii"))
        with open(public_file, "xb") as file:
            file.write(public_bytes)

    return Ed25519PublicKey.from_public_bytes(public_bytes)


if __name__ == "__main__":
    import sys

    print("ran with", sys.argv)
    public_key = register(sys.argv[0], vat_id="1231231")
    print(public_key.public_bytes_raw())
