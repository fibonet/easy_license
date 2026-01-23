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
    application: str
    vat_id: str
    valid_from: date
    valid_until: date
    signature: bytes

    def serialise(self):
        buffer = b"".join(
            (
                self.application.encode(),
                self.vat_id.encode(),
                self.valid_from.isoformat().encode(),
                self.valid_until.isoformat().encode(),
            )
        )
        return buffer
