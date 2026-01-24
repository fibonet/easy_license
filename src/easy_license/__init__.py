import re
import unicodedata

from .client import load_or_fetch_application_key
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
    "load_or_fetch_application_key",
    "slugify",
]
