import json
from base64 import b64decode, b64encode
from pathlib import Path
from uuid import getnode

import requests
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from .license import License

# NOTE: getnode() may return a random value if no MAC is available
MACHINE_ID = getnode().to_bytes(length=8, byteorder="big")


def fetch_application_key(api_root: str, application: str, customer: str) -> bytes:
    payload = dict(
        application=application,
        customer=customer,
        machine_id=b64encode(MACHINE_ID).decode("ascii"),
    )
    api_url = f"{api_root}/application_key"

    response = requests.post(api_url, json=payload)
    response.raise_for_status()

    data = response.json()
    return b64decode(data["public_key"].encode("ascii"))


def fetch_license(api_root: str, application: str, customer: str) -> dict:
    payload = dict(
        application=application,
        customer=customer,
        machine_id=b64encode(MACHINE_ID).decode("ascii"),
    )
    api_url = f"{api_root}/license"

    response = requests.post(api_url, json=payload)
    response.raise_for_status()

    return response.json()


class LazyCachedClient:
    """
    Client for retrieving and validating application licenses.

    Stores the license server URL but does not maintain a persistent HTTP session,
    as requests are expected to be infrequent.

    Typical usage:
        - Instantiate the client early in application startup.
        - Call `on_app_ready()` once all services are initialised.
    """

    def __init__(self, server_url: str, application: str, customer: str):
        """
        Create a client bound to a license server and application identity.

        :param server_url: Base URL of the license server (http or https).
        :param application: Application identifier registered with the server.
        :param customer: Customer identifier.
        """
        if not server_url:
            raise ValueError("Cannot create instance without api_root")
        elif not server_url.startswith("http"):
            raise ValueError("server_url must be a valid http(s) url")

        self.api_root = server_url.strip("/")
        self.application = application
        self.customer = customer

    def load_or_fetch_application_key(self):
        """
        Loads the application public key from a local `.pub` file if it exists.
        If the file does not exist, fetches the key from the server
        (via `fetch_application_key`) and saves it to disk.
        """
        public_file = Path(f"{self.application}-{self.customer}.pub")

        try:
            public_key_bytes = public_file.read_bytes()
        except FileNotFoundError:
            public_key_bytes = fetch_application_key(
                self.api_root, self.application, self.customer
            )
            public_file.write_bytes(public_key_bytes)

        return Ed25519PublicKey.from_public_bytes(public_key_bytes)

    def load_or_fetch_license(self) -> License:
        """
        Loads a License object from a local JSON file if it exists.
        If the file does not exist, fetches the license from the server
        (via `fetch_license`) and saves it to disk.
        """
        filepath = Path(f"{self.application}-{self.customer}-license.json")

        if not filepath.exists():
            license_data = fetch_license(self.api_root, self.application, self.customer)
            with open(filepath, "xt") as f:
                json.dump(license_data, f, separators=(",", ":"), sort_keys=True)

        return License.from_file(filepath)

    def verify(self):
        """Call this from `app_ready` handler, or simply on the startup"""
        public_key = self.load_or_fetch_application_key()
        a_license = self.load_or_fetch_license()
        a_license.verify(public_key)
