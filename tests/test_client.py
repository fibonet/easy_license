import pytest

from easy_license import load_application_key


@pytest.mark.parametrize("key", ["app-name_vat-id-42", "testing-is-forever_not-999"])
def test_register_reuses_existing_file(tmp_path, monkeypatch, key):
    monkeypatch.chdir(tmp_path)
    pub1 = load_application_key(key)
    pub2 = load_application_key(key)
    assert pub1.public_bytes_raw() == pub2.public_bytes_raw()
