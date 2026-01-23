from datetime import date

import pytest

from easy_license import License, slugify


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
    "signature,valid_from,valid_until,application,vat_id,expected_bytes",
    [
        (
            b"\x01\x02",
            date(2024, 1, 1),
            date(2024, 12, 31),
            "my_app",
            "VAT123",
            b"\x01\x022024-01-012024-12-31my_appVAT123",
        ),
        (
            b"sig",
            date(2023, 6, 15),
            date(2025, 6, 15),
            "billing",
            "EU987654",
            b"sig2023-06-152025-06-15billingEU987654",
        ),
    ],
)
def test_license_serialise(
    signature, valid_from, valid_until, application, vat_id, expected_bytes
):
    lic = License(
        signature=signature,
        valid_from=valid_from,
        valid_until=valid_until,
        application=application,
        vat_id=vat_id,
    )

    actual = lic.serialise()

    assert isinstance(actual, bytes)
    assert actual == expected_bytes
