#!/usr/bin/env python3
import base64
import json
from datetime import date
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


def generate(key_name: str):
    private_key = Ed25519PrivateKey.generate()

    # NOTE: save private key
    private_file = Path(key_name)
    with open(private_file, "wb") as file:
        buffer = private_key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.OpenSSH,
            serialization.NoEncryption(),
        )
        file.write(buffer)
        print(f"Wrote {len(buffer)} bytes to {private_file}")

    # NOTE: save public key
    public_file = private_file.with_suffix(".pub")
    with open(public_file, "wb") as file:
        buffer = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.OpenSSH,
            format=serialization.PublicFormat.OpenSSH,
        )
        file.write(buffer)
        print(f"Wrote {len(buffer)} bytes to {public_file}")


def sign(use_key: str):
    with open(use_key, "rb") as f:
        buffer = f.read()
        private_key = serialization.load_ssh_private_key(buffer, password=b"")
        print(f"Using {use_key} private key")

    license_data = dict(
        customer_name="Soolutions E-commerce B.V.",
        customer_vat_id="NL853790267B01",
        valid_from="2026-01-01",
        valid_until="2026-02-28",
    )

    license_bytes = json.dumps(
        license_data, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")
    signature = private_key.sign(license_bytes)
    signed_license = {
        "data": license_data,
        "signature": base64.b64encode(signature).decode(),
    }

    license_file = f"license-{use_key}.json"
    with open(license_file, "wt") as f:
        buffer = json.dumps(signed_license, separators=(",", ":"), indent=4)
        f.write(buffer)
        print(f"Wrote {len(buffer)} bytes to {license_file}")


def verify(key_name: str, license_file: str):
    private_file = Path(key_name)
    public_file = private_file.with_suffix(".pub")
    with open(public_file, "rb") as f:
        buffer = f.read()
        public_key = serialization.load_ssh_public_key(buffer)
        print(f"Using {key_name} private key")

    with open(license_file, "rt") as f:
        buffer = f.read()
        payload = json.loads(buffer)

    license_bytes = json.dumps(
        payload["data"], separators=(",", ":"), sort_keys=True
    ).encode("utf-8")
    signature = base64.b64decode(payload["signature"])

    public_key.verify(signature, license_bytes)

    today = date.today()
    start = date.fromisoformat(payload["data"]["valid_from"])
    end = date.fromisoformat(payload["data"]["valid_until"])

    if today < start or today > end:
        raise ValueError("License expired or not yet valid")

    print(f"{license_file} is valid for {today}")


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser(
        description="Easy license management",
        epilog="Keep those fuckers paying.",
    )
    parser.add_argument("-k", "--key", help="Select private key")
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-g", "--gen", action="store_true", help="Generate private/public key pair."
    )
    group.add_argument("-s", "--sign", action="store_true", help="Sign license file.")
    group.add_argument("-v", "--verify", help="Verify license.")
    args = parser.parse_args()

    if args.gen:
        generate(args.key)
    elif args.sign:
        sign(args.key)
    elif args.verify:
        verify(args.key, args.verify)
    else:
        parser.print_usage()
