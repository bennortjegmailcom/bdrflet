"""Equipment catalogue model used by search and QR identification."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Equipment:
    equipment_id: str
    equipment_code: str
    description: str
    area: str
    plant: str
    department: str
    workgroup: str
    qr_identifier: str
    scada_tag: str
    active: bool
