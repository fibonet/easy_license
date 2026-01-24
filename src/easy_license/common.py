import re
import unicodedata
from dataclasses import dataclass
from datetime import date

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


@dataclass
class License:
    application: str
    customer: str
    valid_from: date
    valid_until: date
    signature: bytes

    def data(self) -> bytes:
        buffer = b"".join(
            (
                self.application.encode(),
                self.customer.encode(),
                self.valid_from.isoformat().encode(),
                self.valid_until.isoformat().encode(),
            )
        )
        return buffer

    def verify(self, public_key: Ed25519PublicKey):
        public_key.verify(self.signature, self.data())
        today = date.today()
        if today < self.valid_from or today > self.valid_until:
            raise ValueError("License is expired")
