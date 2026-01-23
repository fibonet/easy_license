import re
import unicodedata
from dataclasses import dataclass
from datetime import date


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


@dataclass
class License:
    signature: bytes
    valid_from: date
    valid_until: date
    application: str
    vat_id: str

    def serialise(self):
        buffer = b"".join(
            (
                self.signature,
                self.valid_from.isoformat().encode(),
                self.valid_until.isoformat().encode(),
                self.application.encode(),
                self.vat_id.encode(),
            )
        )
        return buffer
