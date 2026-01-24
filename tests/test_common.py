import pytest

from easy_license import slugify


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
