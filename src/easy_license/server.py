from base64 import b64encode
from datetime import date, timedelta
from typing import Dict, Tuple
from uuid import UUID

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from fastapi import FastAPI, HTTPException
from license import License
from pydantic import BaseModel

app = FastAPI(title="Easy Licensing Server")

application_keys: Dict[Tuple[UUID, UUID], Ed25519PrivateKey] = {}
customer_payments: Dict[UUID, bool] = {}


class ApplicationKeyRequest(BaseModel):
    application: UUID
    customer: UUID
    machine: str


class LicenseRequest(BaseModel):
    application: UUID
    customer: UUID
    machine_id: str


def get_private_key(application: UUID, customer: UUID) -> Ed25519PrivateKey:
    key = (application, customer)
    return application_keys.setdefault(key, Ed25519PrivateKey.generate())


def has_pending_payment(customer: UUID) -> bool:
    return customer_payments.get(customer, False)


@app.post("/application_key")
def application_key(request: ApplicationKeyRequest) -> dict:
    private_key = get_private_key(request.application, request.customer)
    public_key = private_key.public_key()

    public_key_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw
    )

    return {"public_key": b64encode(public_key_bytes).decode()}


@app.post("/license")
def license(request: LicenseRequest) -> dict:
    if has_pending_payment(request.customer):
        raise HTTPException(status_code=402, detail="Payment required")

    private_key = get_private_key(request.application, request.customer)

    today = date.today()
    license_obj = License(
        application=str(request.application),
        customer=str(request.customer),
        valid_from=today,
        valid_until=today + timedelta(days=30),
    )
    license_obj.sign(private_key)

    return license_obj.json_data()
