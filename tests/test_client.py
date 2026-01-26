import json
import random
from datetime import date, timedelta
from unittest.mock import patch

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

from easy_license import LazyCachedClient, License


@pytest.fixture
def private_key() -> Ed25519PrivateKey:
    return Ed25519PrivateKey.generate()


@pytest.fixture
def signed_license(private_key) -> License:
    today = date.today()
    lic = License(
        application="unittest",
        customer="RO123123",
        valid_from=today + timedelta(days=random.randrange(-30, 0)),
        valid_until=today + timedelta(days=random.randrange(30)),
    )
    lic.sign(private_key)
    return lic


@pytest.fixture
def a_client(private_key, signed_license):
    server_url = "http://fake-server.local"
    buffer = private_key.public_key().public_bytes_raw()
    with (
        patch("easy_license.client.fetch_application_key", return_value=buffer),
        patch(
            "easy_license.client.fetch_license", return_value=signed_license.json_data()
        ),
    ):
        client = LazyCachedClient(
            server_url, signed_license.application, signed_license.customer
        )

        yield client


def test_can_create_valid_instance(a_client):
    assert a_client


def test_verify_valid_instance_does_not_raise(a_client):
    a_client.verify()
