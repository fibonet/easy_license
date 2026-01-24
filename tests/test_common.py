import random
from datetime import date, timedelta

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)

from easy_license import InvalidSignature, License, slugify


def make_signed_license(
    *,
    application="unittest",
    customer="developers",
    valid_from,
    valid_until,
    private_key,
):
    unsigned = License(
        application=application,
        customer=customer,
        valid_from=valid_from,
        valid_until=valid_until,
    )
    signature = private_key.sign(unsigned.data())
    return License(
        application=application,
        customer=customer,
        valid_from=valid_from,
        valid_until=valid_until,
        signature=signature,
    )


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


@pytest.mark.parametrize(
    "given,expected",
    [
        ("Hello World", "hello-world"),
        ("  Hello   World  ", "hello-world"),
        ("Hello, World!", "hello-world"),
        ("Český Krumlov", "cesky-krumlov"),
        ("München", "munchen"),
        ("Already-Slugified", "already-slugified"),
        ("multiple---separators", "multiple-separators"),
        ("123 Numbers First", "123-numbers-first"),
        ("---Leading and trailing---", "leading-and-trailing"),
        ("", ""),
    ],
)
def test_slugify(given, expected):
    assert slugify(given) == expected


@pytest.mark.parametrize(
    "from_offset,until_offset",
    [
        (-1, 1),
        (0, 0),
        (-30, 30),
    ],
)
def test_verify_signed_license_does_not_raise(private_key, from_offset, until_offset):
    today = date.today()
    license = make_signed_license(
        valid_from=today + timedelta(days=from_offset),
        valid_until=today + timedelta(days=until_offset),
        private_key=private_key,
    )

    license.verify(private_key.public_key())


@pytest.mark.parametrize(
    "from_offset,until_offset",
    [
        (1, 10),
        (-10, -1),
    ],
)
def test_verify_expired_license_raises(private_key, from_offset, until_offset):
    today = date.today()
    license = make_signed_license(
        valid_from=today + timedelta(days=from_offset),
        valid_until=today + timedelta(days=until_offset),
        private_key=private_key,
    )

    with pytest.raises(InvalidSignature):
        license.verify(private_key.public_key())


@pytest.mark.parametrize(
    "from_offset,until_offset",
    [
        (-2, 2),
        (0, 0),
        (-32, 32),
    ],
)
def test_verify_tampered_license_raises(private_key, from_offset, until_offset):
    today = date.today()
    license = make_signed_license(
        valid_from=today + timedelta(days=from_offset),
        valid_until=today + timedelta(days=until_offset),
        private_key=private_key,
    )
    license.signature = corrupted(license.signature)

    with pytest.raises(InvalidSignature):
        license.verify(private_key.public_key())
