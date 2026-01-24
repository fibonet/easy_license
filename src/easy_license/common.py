import re
import unicodedata
from base64 import encode
from dataclasses import dataclass
from datetime import date
from typing import ClassVar

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


@dataclass
class License:
    VERSION_TAG: ClassVar[str] = "v1"
    application: str
    customer: str
    valid_from: date
    valid_until: date
    signature: bytes = b""

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
