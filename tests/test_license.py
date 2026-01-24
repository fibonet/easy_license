import random
import tempfile
from datetime import date, timedelta
from pathlib import Path

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)

from easy_license import InvalidSignature, License, slugify


def corrupted(buffer: bytes) -> bytes:
    """Simulate data corruption"""
    assert buffer, "Cannot corrupt empty buffer"
    data = bytearray(buffer)
    pos = random.randrange(len(buffer))
    data[pos] ^= 0x01
    return bytes(data)


@pytest.fixture
def private_key() -> Ed25519PrivateKey:
    return Ed25519PrivateKey.generate()


@pytest.fixture
def signed_license(private_key) -> License:
    today = date.today()
    lic = License(
        application="unittest",
        customer="developers",
        valid_from=today + timedelta(days=random.randrange(-30, 0)),
        valid_until=today + timedelta(days=random.randrange(30)),
    )
    lic.sign(private_key)
    return lic


def make_license(
    *,
    private_key=None,
    application="unittest",
    customer="developers",
    from_offset=-1,
    until_offset=+1,
) -> License:
    today = date.today()
    lic = License(
        application="unittest",
        customer="developers",
        valid_from=today + timedelta(days=from_offset),
        valid_until=today + timedelta(days=until_offset),
    )

    if private_key:
        lic.sign(private_key)
    return lic


def test_sign_creates_valid_signature(private_key):
    lic = make_license()
    assert lic.signature == b""

    lic.sign(private_key)

    assert lic.signature
    lic.verify(private_key.public_key())


@pytest.mark.parametrize(
    "from_offset,until_offset",
    [
        (-1, 1),
        (0, 0),
        (-30, 30),
    ],
)
def test_verify_signed_license_does_not_raise(private_key, from_offset, until_offset):
    lic = make_license(
        private_key=private_key,
        from_offset=from_offset,
        until_offset=until_offset,
    )

    lic.verify(private_key.public_key())


@pytest.mark.parametrize(
    "from_offset,until_offset",
    [
        (1, 10),
        (-10, -1),
    ],
)
def test_verify_expired_license_raises(private_key, from_offset, until_offset):
    lic = make_license(
        private_key=private_key,
        from_offset=from_offset,
        until_offset=until_offset,
    )

    with pytest.raises(InvalidSignature):
        lic.verify(private_key.public_key())


@pytest.mark.parametrize(
    "from_offset,until_offset",
    [
        (-2, 2),
        (0, 0),
        (-32, 32),
    ],
)
def test_verify_tampered_license_raises(private_key, from_offset, until_offset):
    lic = make_license(
        private_key=private_key,
        from_offset=from_offset,
        until_offset=until_offset,
    )
    lic.verify(private_key.public_key())

    lic.signature = corrupted(lic.signature)

    with pytest.raises(InvalidSignature):
        lic.verify(private_key.public_key())


def test_save_and_load_from_file(private_key, signed_license):
    with tempfile.NamedTemporaryFile("w+t") as tmp:
        license_file = Path(tmp.name)

        signed_license.to_file(license_file)
        reloaded = License.from_file(license_file)

        signed_license.verify(private_key.public_key())
        reloaded.verify(private_key.public_key())
        assert reloaded == signed_license
