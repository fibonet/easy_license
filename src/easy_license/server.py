from base64 import b64encode
from datetime import date, timedelta
from typing import Dict, Tuple
from uuid import UUID

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from fastapi import FastAPI
from license import License
from pydantic import BaseModel

app = FastAPI(title="Easy License Server")

application_keys: Dict[Tuple[UUID, UUID], Ed25519PrivateKey] = {}


class ApplicationKeyRequest(BaseModel):
    application: UUID
    customer: UUID
    machine: str


class LicenseRequest(BaseModel):
    application: UUID
    customer: UUID
    machine_id: str


def get_private_key(application: UUID, customer: UUID) -> Ed25519PrivateKey:
    """Get or create private key for application-customer pair."""
    key = (application, customer)
    return application_keys.setdefault(key, Ed25519PrivateKey.generate())


@app.post("/application_key")
def application_key(request: ApplicationKeyRequest) -> dict:
    """Return public key for application-customer pair."""
    private_key = get_private_key(request.application, request.customer)
    public_key = private_key.public_key()

    public_key_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw
    )

    return {"public_key": b64encode(public_key_bytes).decode()}


@app.post("/license")
def license(request: LicenseRequest) -> dict:
    """Return signed license for application-customer pair."""
    private_key = get_private_key(request.application, request.customer)

    today = date.today()

    license_obj = License(
        application=str(request.application),
        customer=str(request.customer),
        valid_from=today,
        valid_until=today + timedelta(days=365),
    )

    license_obj.sign(private_key)

    return license_obj.json_data()
