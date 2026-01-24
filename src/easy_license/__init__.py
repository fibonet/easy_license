import re
import unicodedata

from .client import verify
from .license import InvalidSignature, License


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


__all__ = [
    "InvalidSignature",
    "License",
    "slugify",
    "verify",
]
