import json
from base64 import b64decode, b64encode
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import ClassVar

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)


@dataclass
class License:
    VERSION_TAG: ClassVar[str] = "v1"
    application: str
    customer: str
    valid_from: date
    valid_until: date
    signature: bytes = b""

    @classmethod
    def from_file(cls, filepath: Path):
        with open(filepath, "rb") as f:
            data = json.load(f)

        if signature := data.get("signature"):
            data["signature"] = b64decode(signature)
        if valid_from := data.get("valid_from"):
            data["valid_from"] = date.fromisoformat(valid_from)
        if valid_until := data.get("valid_until"):
            data["valid_until"] = date.fromisoformat(valid_until)

        return cls(**data)

    def to_file(self, filepath: Path):
        data = asdict(self)

        if self.signature:
            data["signature"] = b64encode(self.signature).decode()
        if isinstance(self.valid_from, date):
            data["valid_from"] = self.valid_from.isoformat()
        if isinstance(self.valid_until, date):
            data["valid_until"] = self.valid_until.isoformat()

        with open(filepath, "wt") as f:
            json.dump(data, f, indent=4)

    def data(self) -> bytes:
        buffer = b"".join(
            (
                self.VERSION_TAG.encode(),
                self.application.encode(),
                self.customer.encode(),
                self.valid_from.isoformat().encode(),
                self.valid_until.isoformat().encode(),
            )
        )
        return buffer

    def verify(self, public_key: Ed25519PublicKey):
        """Raises InvalidSignature if anything fails"""
        public_key.verify(self.signature, self.data())

        today = date.today()
        if today < self.valid_from or today > self.valid_until:
            raise InvalidSignature("License is expired")

    def sign(self, private_key: Ed25519PrivateKey) -> None:
        """Signs (mutates) the current license"""
        self.signature = private_key.sign(self.data())
